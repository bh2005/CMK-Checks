#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk Agent-Based Plugin for ExtremeCloudIQ
Compatible with Checkmk 2.3 / 2.4 (API v2)

Sections:
  - extreme_cloud_iq_login
  - extreme_summary
  - extreme_ap_status
  - extreme_ap_clients
  - extreme_cloud_iq_rate_limits
  - extreme_device_inventory
  - extreme_device_neighbors
  - xiq_radio_information     # Radios (JSON) pro AP

Inventory:
  - Devices (AP/SW/MISC)
  - LLDP/CDP Neighbors
"""

from typing import Mapping, Any, Iterable, List, Optional
import json

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    InventoryPlugin,
    TableRow,
    Metric,
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def format_mac(raw: str) -> str:
    r = (raw or "").replace(":", "").replace("-", "").strip().upper()
    if len(r) != 12:
        return raw or ""
    return ":".join(r[i:i+2] for i in range(0, 12, 2))

def _fmt_uptime(seconds: int) -> str:
    s = max(0, int(seconds or 0))
    d, rem = divmod(s, 86400)
    h, rem = divmod(rem, 3600)
    m, _ = divmod(rem, 60)
    return f"{d}d {h}h {m}m"


# ----------------------------------------------------------------------
# Parsers
# ----------------------------------------------------------------------

def parse_xiq_login(table: StringTable) -> Optional[Mapping[str, str]]:
    if not table:
        return None

    raw = " ".join(table[0]).strip()
    if not raw:
        return None

    res: dict[str, str] = {"RAW": raw}

    def _get_value(tag: str) -> Optional[str]:
        pos = raw.find(tag)
        if pos == -1:
            return None
        pos += len(tag)
        candidates = []
        for other in ("STATUS:", "CODE:", "RESPONSE:"):
            if other == tag:
                continue
            p = raw.find(other, pos)
            if p != -1:
                candidates.append(p)
        end = min(candidates) if candidates else len(raw)
        return raw[pos:end].strip()

    status = _get_value("STATUS:")
    code = _get_value("CODE:")
    resp_pos = raw.find("RESPONSE:")
    response = raw[resp_pos + len("RESPONSE:"):].strip() if resp_pos != -1 else None

    if status is not None:
        res["STATUS"] = status
    if code is not None:
        res["CODE"] = code
    if response is not None:
        res["RESPONSE"] = response

    return res


def parse_xiq_summary(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None
    res: dict[str, Any] = {}
    for line in table:
        if len(line) >= 2:
            res[line[0]] = line[1]
    return res


def parse_xiq_ap_status(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None

    row = table[0]

    def s(i: int) -> str:
        return row[i] if len(row) > i else ""

    return {
        "ap_name": s(0),
        "serial": s(1),
        "mac": format_mac(s(2)),
        "ip": s(3),
        "model": s(4),
        "connected": s(5) == "1",
        "state": s(6),
        "sw_version": s(7),
        "uptime_s": int(s(8) or 0),
        "locations": s(9),
        "lldp_cdp_short": s(10),
    }


def parse_xiq_ap_clients(table: StringTable) -> Optional[Mapping[str, int]]:
    if not table:
        return None
    row = table[0]

    def to(i: int) -> int:
        try:
            return int(row[i])
        except Exception:
            return 0

    return {
        "clients_24": to(0),
        "clients_5":  to(1),
        "clients_6":  to(2),
    }


def parse_xiq_rate_limits(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None

    res: dict[str, Any] = {}
    for line in table:
        if len(line) == 2:
            key, val = line
            if val.isdigit():
                res[key] = int(val)
            else:
                try:
                    res[key] = float(val)
                except Exception:
                    res[key] = val or None
    return res


def parse_xiq_device_inventory(table: StringTable) -> List[List[str]]:
    """
    rows:
      id|hostname|serial|mac|ip|model|sw|location|device_function|managed_by
    """
    result: List[List[str]] = []
    for row in table:
        if len(row) < 10:
            continue
        result.append(row)
    return result


def parse_xiq_device_neighbors(table: StringTable) -> List[Mapping[str, str]]:
    """
    rows (pipe-separated):
    device_id|hostname|hostaddress|local_port|management_ip|remote_port|port_description|mac_address|remote_device
    """
    result = []
    for row in table:
        if len(row) < 9:
            continue
        result.append({
            "device_id":      row[0],
            "hostname":       row[1],
            "hostaddress":    row[2],
            "local_port":     row[3],
            "management_ip":  row[4],
            "remote_port":    row[5],
            "port_description": row[6],
            "mac_address":    row[7],
            "remote_device":  row[8],
        })
    return result

# Parser für xiq_radio_information (JSON-Section)
# Liefert Mapping: freq -> [{"ssid":..,"bssid":..}, ...]


def parse_xiq_radio_information(table: StringTable) -> Optional[Mapping[str, Any]]:
    """
    Liest die JSON-Section xiq_radio_information und liefert:
      - Frequenz-Keys ("2.4GHz", "5GHz", "6GHz") -> Liste aus {"ssid","bssid"} (rückwärtskompatibel)
      - _radios -> vollständige Radio-Liste inkl. Kanal, Breite, Mode, Power, SSID/BSSID-Listen, Client-Count
      - _device_id, _hostname -> aus der JSON-Section
    """
    if not table:
        return None

    txt = "".join("".join(row) for row in table).strip()
    if not txt or not txt.startswith("{"):
        return None

    try:
        data = json.loads(txt)
    except Exception:
        return None

    device_id = data.get("device_id")
    hostname = data.get("hostname") or ""

    radios = data.get("radios") or []
    out_by_freq: dict[str, list[dict[str, str]]] = {}
    out_radios: list[dict[str, Any]] = []

    for r in radios:
        # Frequency normalisieren
        freq = str(r.get("frequency") or "").strip()
        if not freq:
            mode = str(r.get("mode") or "").lower()
            if "5g" in mode:
                freq = "5GHz"
            elif "6g" in mode:
                freq = "6GHz"
            else:
                freq = "2.4GHz"

        # SSIDs/BSSIDs aus wlans extrahieren
        wlans = r.get("wlans") or []
        wl_by_freq = []
        ssid_list: list[str] = []
        bssid_list: list[str] = []

        for w in wlans:
            ssid = str(w.get("ssid") or "")
            bssid = format_mac(str(w.get("bssid") or ""))
            if ssid or bssid:
                wl_by_freq.append({"ssid": ssid, "bssid": bssid})
            if ssid:
                ssid_list.append(ssid)
            if bssid:
                bssid_list.append(bssid)

        if wl_by_freq:
            out_by_freq.setdefault(freq, []).extend(wl_by_freq)

        # Client-Count robust ermitteln (nur echte Zähler verwenden)
        client_count = 0
        for key in ("active_clients", "connected_clients", "client_count"):
            v = r.get(key)
            if isinstance(v, int) and v >= 0:
                client_count = v
                break
            # Strings zulassen
            try:
                client_count = int(v) if v is not None else 0
                break
            except Exception:
                pass

        out_radios.append({
            "device_id": device_id,
            "hostname": hostname,
            "radio_name": str(r.get("name") or ""),
            "radio_mac": format_mac(str(r.get("mac_address") or "")),
            "frequency": freq,
            "channel_number": int(r.get("channel_number") or 0),
            "channel_width": str(r.get("channel_width") or ""),
            "mode": str(r.get("mode") or ""),
            "power": int(r.get("power") or 0),
            "ssid_list": ssid_list,
            "bssid_list": bssid_list,
            "client_count": client_count,
        })

    # Rückgabestruktur: Frequenz-Keys + _radios + Meta
    result: dict[str, Any] = {}
    result.update(out_by_freq)
    result["_radios"] = out_radios
    result["_device_id"] = device_id
    result["_hostname"] = hostname

    return result or None


# ----------------------------------------------------------------------
# Discovery
# ----------------------------------------------------------------------

def discover_single(section: Any) -> DiscoveryResult:
    yield Service()


def discover_xiq_aps(section: Mapping[str, Any]) -> DiscoveryResult:
    if section and section.get("ap_name"):
        yield Service(item=section["ap_name"])


def discover_rate_limits(section: Mapping[str, Any]) -> DiscoveryResult:
    yield Service()


# Discovery für "ein Service je Frequenz" (korrekte Signatur gemäß sections=[])

def discover_xiq_radios(
    section_xiq_radio_information: Optional[Mapping[str, List[Mapping[str, str]]]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],
    section_extreme_ap_clients: Optional[Mapping[str, int]],  # ungenutzt, Signatur-konform
) -> DiscoveryResult:
    if not section_xiq_radio_information or not section_extreme_ap_status:
        return
    ap_name = section_extreme_ap_status.get("ap_name")
    if not ap_name:
        return

    for freq in ("2.4GHz", "5GHz", "6GHz"):
        if freq in section_xiq_radio_information:
            yield Service(item=f"{ap_name} {freq}")

# Discovery: ein Service pro SSID (aus allen Bändern gesammelt)
def discover_xiq_ssids(
    section_xiq_radio_information: Optional[Mapping[str, Any]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],      # ungenutzt, Signatur-konform
    section_extreme_ap_clients: Optional[Mapping[str, int]],     # ungenutzt, Signatur-konform
) -> DiscoveryResult:
    if not section_xiq_radio_information:
        return

    # SSIDs aus den Frequenz-Keys sammeln (rückwärtskompatibles Format aus parse_xiq_radio_information)
    ssids: set[str] = set()
    for freq in ("2.4GHz", "5GHz", "6GHz"):
        wlans = section_xiq_radio_information.get(freq) or []
        for w in wlans:
            ssid = (w.get("ssid") or "").strip()
            if ssid:
                ssids.add(ssid)

    # Fallback: falls aus irgendeinem Grund oben leer, aus _radios lesen
    if not ssids:
        radios = section_xiq_radio_information.get("_radios") or []
        for r in radios:
            for ssid in (r.get("ssid_list") or []):
                s = (ssid or "").strip()
                if s:
                    ssids.add(s)

    for ssid in sorted(ssids):
        yield Service(item=ssid)


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------

def check_xiq_login(section: Mapping[str, str]) -> Iterable[CheckResult]:
    status = section.get("STATUS", "FAILED")
    msg = section.get("RESPONSE", section.get("RAW", ""))
    yield Result(
        state=State.OK if status == "OK" else State.CRIT,
        summary=f"Login: {msg}",
    )


def check_xiq_summary(section: Mapping[str, Any]) -> Iterable[CheckResult]:
    aps  = int(section.get("access_points", "0") or 0)
    tcl  = int(section.get("total_clients", "0") or 0)
    c24  = int(section.get("clients_24", "0") or 0)
    c5   = int(section.get("clients_5", "0") or 0)
    c6   = int(section.get("clients_6", "0") or 0)

    yield Result(state=State.OK, summary=f"{aps} APs, {tcl} Clients")

    yield Metric("xiq_aps_total", aps)
    yield Metric("xiq_clients_total", tcl)
    yield Metric("xiq_clients_24", c24)
    yield Metric("xiq_clients_5",  c5)
    yield Metric("xiq_clients_6",  c6)


def check_xiq_ap_status(item: str, section: Mapping[str, Any]) -> Iterable[CheckResult]:
    connected = section.get("connected", False)
    model = section.get("model", "?")
    state_text = section.get("state", "?")
    sw = section.get("sw_version", "")
    up = section.get("uptime_s", 0)
    loc = section.get("locations", "")
    lldp = section.get("lldp_cdp_short", "")

    details: List[str] = []
    if sw:
        details.append(f"FW: {sw}")
    if up:
        details.append(f"Uptime: {_fmt_uptime(up)}")
    if loc:
        details.append(f"Loc: {loc}")
    if lldp:
        details.append(f"LLDP: {lldp}")

    suffix = " | " + " • ".join(details) if details else ""

    yield Result(
        state=State.OK if connected else State.CRIT,
        summary=f"{item} ({model}) {state_text}{suffix}",
    )


def check_xiq_ap_clients(item: str, section: Mapping[str, Any]) -> Iterable[CheckResult]:
    c24 = int(section.get("clients_24", 0))
    c5  = int(section.get("clients_5", 0))
    c6  = int(section.get("clients_6", 0))
    total = c24 + c5 + c6

    yield Result(
        state=State.OK,
        summary=f"{item}: {total} Clients (2.4GHz: {c24}, 5GHz: {c5}, 6GHz: {c6})",
    )

    yield Metric("xiq_clients_24", c24)
    yield Metric("xiq_clients_5",  c5)
    yield Metric("xiq_clients_6",  c6)


def check_xiq_rate_limits(section: Mapping[str, Any]) -> Iterable[CheckResult]:
    state = section.get("state")

    if state == "UNLIMITED":
        yield Result(state=State.OK, summary="API has no rate limit headers")
        return

    limit     = section.get("limit")
    remaining = section.get("remaining")
    reset     = section.get("reset_in_seconds")

    if limit is None:
        yield Result(state=State.OK, summary="No rate limit information available")
        return

    if remaining is not None:
        summary = f"Remaining {remaining}/{limit}, reset in {reset}s"
    else:
        summary = "Rate limit data incomplete"

    if limit and remaining is not None:
        ratio = float(remaining) / float(limit)
        if ratio < 0.05:
            yield Result(state=State.CRIT, summary=summary)
            return
        if ratio < 0.10:
            yield Result(state=State.WARN, summary=summary)
            return

    yield Result(state=State.OK, summary=summary)


# Check: ein Service je Frequenz, mit Schwellwerten & Perfdata-Levels

def check_xiq_radios(
    item: str,
    params: Mapping[str, Any],
    section_xiq_radio_information: Optional[Mapping[str, List[Mapping[str, str]]]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],  # ungenutzt
    section_extreme_ap_clients: Optional[Mapping[str, int]],
) -> Iterable[CheckResult]:
    if not section_xiq_radio_information:
        return

    parts = item.split()
    freq = parts[-1] if parts else "2.4GHz"

    clients_total = 0
    if section_extreme_ap_clients:
        if freq == "2.4GHz":
            clients_total = int(section_extreme_ap_clients.get("clients_24", 0))
        elif freq == "5GHz":
            clients_total = int(section_extreme_ap_clients.get("clients_5", 0))
        elif freq == "6GHz":
            clients_total = int(section_extreme_ap_clients.get("clients_6", 0))

    warn = crit = None
    per_band = (params or {}).get("per_band") or {}
    if freq in per_band:
        band_wc = per_band[freq]
        if isinstance(band_wc, (list, tuple)) and len(band_wc) >= 2:
            warn, crit = band_wc[0], band_wc[1]
    if warn is None or crit is None:
        gl = (params or {}).get("global_levels")
        if isinstance(gl, (list, tuple)) and len(gl) >= 2:
            warn = gl[0] if warn is None else warn
            crit = gl[1] if crit is None else crit

    state = State.OK
    if crit is not None and clients_total >= crit:
        state = State.CRIT
    elif warn is not None and clients_total >= warn:
        state = State.WARN

    wlans = section_xiq_radio_information.get(freq, []) if section_xiq_radio_information else []
    yield Result(state=state, summary=f"{freq}: {clients_total} Clients")

    for w in wlans:
        ssid = w.get("ssid", "")
        bssid = w.get("bssid", "")
        yield Result(state=State.OK, notice=f"SSID {ssid} | BSSID {bssid}")

    yield Metric(
        "xiq_radio_clients",
        clients_total,
        levels=(float(warn) if warn is not None else None,
                float(crit) if crit is not None else None),
    )


def check_xiq_ssid(
    item: str,
    params: Mapping[str, Any],
    section_xiq_radio_information: Optional[Mapping[str, Any]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],     # nur für Kontexte/Notices
    section_extreme_ap_clients: Optional[Mapping[str, int]],    # für AP-weite Totals (optional)
) -> Iterable[CheckResult]:
    if not section_xiq_radio_information:
        return

    ap_name = ""
    if section_extreme_ap_status:
        ap_name = section_extreme_ap_status.get("ap_name", "") or ""

    # Ziel: clients je Frequenz für genau diese SSID (item)
    counts = {"2.4GHz": 0, "5GHz": 0, "6GHz": 0}
    notices: list[str] = []

    # 1) Primärer Weg: Wenn wlans-Einträge *künftig* pro-SSID-Zähler enthalten,
    #    dann hier je Radio/Frequenz summieren (client_count/clients_count/stations/num_clients)
    radios = section_xiq_radio_information.get("_radios") or []
    for r in radios:
        freq = r.get("frequency", "")
        if freq not in counts:
            continue

        # Liste der SSIDs auf diesem Radio
        ssids_on_radio = [s for s in (r.get("ssid_list") or []) if s]
        radio_clients_total = int(r.get("client_count") or 0)

        # Falls wir *detaillierte* SSID-Zähler in der Section hätten (z. B. aus erweitertem Agent)
        # könnten wir sie hier lesen – das folgende Muster unterstützt das bereits:
        # section["_ssid_freq"] = { "SSID": {"2.4GHz": N, "5GHz": M, "6GHz": K}, ... }
        ssid_freq_map = section_xiq_radio_information.get("_ssid_freq") or {}
        if isinstance(ssid_freq_map, dict):
            per_freq = ssid_freq_map.get(item) or {}
            if isinstance(per_freq, dict):
                try:
                    v = int(per_freq.get(freq) or 0)
                    if v > 0:
                        counts[freq] += v
                        continue  # Fertig für dieses Radio/Frequenz
                except Exception:
                    pass

        # Heuristik/Fallback:
        # - Wenn das Radio genau *eine* SSID hat und das ist *dieses* item,
        #   dann ordnen wir den Radio-Clientcount komplett dieser SSID zu.
        if len(ssids_on_radio) == 1 and ssids_on_radio[0] == item:
            counts[freq] += radio_clients_total
        else:
            # Verteilung unklar -> Hinweis in Details
            if radio_clients_total > 0 and item in ssids_on_radio:
                rname = r.get("radio_name", "")
                notices.append(
                    f"{freq}: {radio_clients_total} Clients auf Radio '{rname}' mit "
                    f"{len(ssids_on_radio)} SSIDs – Verteilung auf SSIDs unbekannt"
                )

    total = counts["2.4GHz"] + counts["5GHz"] + counts["6GHz"]

    # Schwellen/Levels: pro Band (per_band) oder global
    warn = crit = None
    per_band: Mapping[str, Any] = (params or {}).get("per_band") or {}

    band_warn_crit = {}
    for band in ("2.4GHz", "5GHz", "6GHz"):
        bwc = per_band.get(band)
        if isinstance(bwc, (list, tuple)) and len(bwc) >= 2:
            band_warn_crit[band] = (bwc[0], bwc[1])

    gl = (params or {}).get("global_levels")
    if isinstance(gl, (list, tuple)) and len(gl) >= 2:
        warn, crit = gl[0], gl[1]

    # Statusberechnung (auf Gesamtwert)
    state = State.OK
    if crit is not None and total >= crit:
        state = State.CRIT
    elif warn is not None and total >= warn:
        state = State.WARN

    # Summary
    prefix = f"AP {ap_name}: " if ap_name else ""
    yield Result(
        state=state,
        summary=f"{prefix}SSID {item}: {total} Clients (2.4GHz: {counts['2.4GHz']}, 5GHz: {counts['5GHz']}, 6GHz: {counts['6GHz']})",
    )

    # Details/Notices – Unklarheiten explizit ausweisen
    for n in notices:
        yield Result(state=State.OK, notice=n)

    # Perfdata total + je Band (Levels optional je Band)
    yield Metric(
        "xiq_ssid_clients_total",
        float(total),
        levels=(float(warn) if warn is not None else None,
                float(crit) if crit is not None else None),
    )

    for band in ("2.4GHz", "5GHz", "6GHz"):
        bw = bc = None
        if band in band_warn_crit:
            bw, bc = band_warn_crit[band]
        yield Metric(
            f"xiq_ssid_clients_{'24' if band=='2.4GHz' else ('5' if band=='5GHz' else '6')}",
            float(counts[band]),
            levels=(float(bw) if bw is not None else None,
                    float(bc) if bc is not None else None),
        )


# ----------------------------------------------------------------------
# Inventory
# ----------------------------------------------------------------------

def inventory_xiq_devices(section: List[List[str]]):
    """
    row:
      id, hostname, serial, mac, ip, model, sw, location, device_function, managed_by
    """
    for row in section:
        dev_id, hostname, serial, mac, ip, model, sw, loc, dev_fun, managed_by = row
        dev_fun_u = (dev_fun or "").upper()

        if "AP" in dev_fun_u:
            path = ["networking", "extreme_ap"]
        elif "SW" in dev_fun_u:
            path = ["networking", "extreme_sw"]
        else:
            path = ["networking", "extreme_misc"]

        location_leaf = ""
        if loc:
            parts = [p.strip() for p in loc.split("/") if p.strip()]
            if parts:
                last = parts[-1]
                idx = last.find("LOC")
                location_leaf = last[idx:] if idx != -1 else last

        yield TableRow(
            path=path,
            key_columns={"id": dev_id},
            inventory_columns={
                "hostname": hostname,
                "serial": serial,
                "mac": mac,
                "ip": ip,
                "model": model,
                "software": sw,
                "location_full": loc,
                "location_leaf": location_leaf,
                "device_function": dev_fun_u,
                "managed_by": managed_by,
            },
        )


def inventory_xiq_neighbors(section: List[Mapping[str, str]]):
    """
    rows aus parse_xiq_device_neighbors():
      device_id|hostname|hostaddress|local_port|management_ip|remote_port|port_description|mac_address|remote_device
    """
    for row in section:
        device_id     = row.get("device_id", "")
        hostname      = row.get("hostname", "")
        hostaddress   = row.get("hostaddress", "")
        local_port    = row.get("local_port", "")
        remote_port   = row.get("remote_port", "")
        port_desc     = row.get("port_description", "")
        management_ip = row.get("management_ip", "")
        remote_device = row.get("remote_device", "")
        mac_address   = format_mac(row.get("mac_address", ""))

        yield TableRow(
            path=["networking", "lldp_infos"],
            key_columns={
                "hostaddress":      hostaddress,
                "hostname":         hostname,
                "id":               device_id,
                "local_port":       local_port,
                "remote_port":      remote_port,
                "port_description": port_desc,
                "management_ip":    management_ip,
                "remote_device":    remote_device,
                "mac_address":      mac_address,
            },
            inventory_columns={},
        )
        


# ----------------------------------------------------------------------
# Unified Inventory: Extreme AP Radios + BSSIDs (hierarchisch)
# ----------------------------------------------------------------------


def inventory_xiq_radio_parent(section):
    if not section:
        return

    radios = section.get("_radios") or []
    if not isinstance(radios, list):
        return

    for r in radios:
        radio_name = r.get("radio_name", "")
        radio_mac  = r.get("radio_mac", "")
        device_id  = r.get("device_id")
        hostname   = r.get("hostname", "")

        freq  = r.get("frequency", "")
        chan  = int(r.get("channel_number") or 0)
        width = r.get("channel_width", "")
        mode  = r.get("mode", "")
        power = int(r.get("power") or 0)

        key_cols = {"radio_name": radio_name}
        if radio_mac:
            key_cols["radio_mac"] = radio_mac

        yield TableRow(
            path=["extreme_ap_radios"],
            key_columns=key_cols,
            inventory_columns={
                "frequency": freq,
                "channel_number": chan,
                "channel_width": width,
                "mode": mode,
                "power": power,
                "device_id": device_id,
                "hostname": hostname,
            },
        )

def inventory_xiq_radio_bssid_children(section):
    if not section:
        return

    radios = section.get("_radios") or []
    ssid_freq = section.get("_ssid_freq") or {}

    for r in radios:
        radio_name = r.get("radio_name", "")
        freq = r.get("frequency", "")
        device_id = r.get("device_id")
        hostname = r.get("hostname", "")

        wlans = r.get("wlans") or []
        for w in wlans:
            ssid = (w.get("ssid", "") or "").strip()
            bssid = format_mac(w.get("bssid", ""))

            clients = 0
            if ssid in ssid_freq:
                clients = int(ssid_freq[ssid].get(freq, 0))

            key_cols = {
                "radio_name": radio_name,
                "bssid": bssid,
            }

            yield TableRow(
                path=["extreme_ap_radios", radio_name],
                key_columns=key_cols,
                inventory_columns={
                    "ssid": ssid,
                    "bssid": bssid,
                    "frequency": freq,
                    "clients": clients,
                    "device_id": device_id,
                    "hostname": hostname,
                },
            )

# ----------------------------------------------------------------------
# Inventory: Extreme AP BSSIDs (Top-Level → nach SSID gruppiert)
# ----------------------------------------------------------------------

def inventory_xiq_bssids_by_ssid(section):
    """
    Erstellt einen eigenen Top-Level Knoten:
    extreme_ap_bssids/ <SSID> / <BSSID>
    """
    if not section:
        return

    radios = section.get("_radios") or []
    ssid_freq = section.get("_ssid_freq") or {}

    # Sammeln nach SSID
    ssid_map = {}  # { "SSID": [ {bssid, freq, radio, device_id, hostname, clients}, ... ] }

    for r in radios:
        radio_name = r.get("radio_name", "")
        freq = r.get("frequency", "")
        device_id = r.get("device_id")
        hostname = r.get("hostname", "")
        wlans = r.get("wlans") or []

        for w in wlans:
            ssid = (w.get("ssid", "") or "").strip()
            bssid = format_mac(w.get("bssid", ""))

            clients = 0
            if ssid in ssid_freq:
                clients = int(ssid_freq[ssid].get(freq, 0))

            ssid_map.setdefault(ssid, []).append({
                "ssid": ssid,
                "bssid": bssid,
                "freq": freq,
                "radio_name": radio_name,
                "device_id": device_id,
                "hostname": hostname,
                "clients": clients,
            })

    # Jetzt ausgeben:
    for ssid, entries in sorted(ssid_map.items()):
        ssid_key = {"ssid": ssid}

        # 1) SSID-Knoten (eltern)
        yield TableRow(
            path=["extreme_ap_bssids", ssid],
            key_columns=ssid_key,
            inventory_columns={},  # reine Container-Zeile
        )

        # 2) darunter BSSID-Zeilen
        for e in entries:
            yield TableRow(
                path=["extreme_ap_bssids", ssid],
                key_columns={"bssid": e["bssid"]},
                inventory_columns={
                    "bssid": e["bssid"],
                    "frequency": e["freq"],
                    "radio_name": e["radio_name"],
                    "clients": e["clients"],
                    "device_id": e["device_id"],
                    "hostname": e["hostname"],
                },
            )



# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

agent_section_xiq_login = AgentSection(
    name="extreme_cloud_iq_login",
    parse_function=parse_xiq_login,
)

agent_section_xiq_summary = AgentSection(
    name="extreme_summary",
    parse_function=parse_xiq_summary,
)

agent_section_xiq_ap_status = AgentSection(
    name="extreme_ap_status",
    parse_function=parse_xiq_ap_status,
)

agent_section_xiq_ap_clients = AgentSection(
    name="extreme_ap_clients",
    parse_function=parse_xiq_ap_clients,
)

agent_section_xiq_rate_limits = AgentSection(
    name="extreme_cloud_iq_rate_limits",
    parse_function=parse_xiq_rate_limits,
)

agent_section_xiq_device_inventory = AgentSection(
    name="extreme_device_inventory",
    parse_function=parse_xiq_device_inventory,
)

agent_section_xiq_device_neighbors = AgentSection(
    name="extreme_device_neighbors",
    parse_function=parse_xiq_device_neighbors,
)

# Radios (JSON)
agent_section_xiq_radios = AgentSection(
    name="xiq_radio_information",
    parse_function=parse_xiq_radio_information,
)

# Checks
check_plugin_xiq_login = CheckPlugin(
    name="xiq_login",
    sections=["extreme_cloud_iq_login"],
    service_name="XIQ API Login",
    discovery_function=discover_single,
    check_function=check_xiq_login,
)

check_plugin_xiq_summary = CheckPlugin(
    name="xiq_summary",
    sections=["extreme_summary"],
    service_name="XIQ Summary",
    discovery_function=discover_single,
    check_function=check_xiq_summary,
)

check_plugin_xiq_ap_status = CheckPlugin(
    name="xiq_ap_status",
    sections=["extreme_ap_status"],
    service_name="XIQ AP %s Status",
    discovery_function=discover_xiq_aps,
    check_function=check_xiq_ap_status,
)

check_plugin_xiq_ap_clients = CheckPlugin(
    name="xiq_ap_clients",
    sections=["extreme_ap_clients"],
    service_name="XIQ AP %s Clients",
    discovery_function=discover_xiq_aps,
    check_function=check_xiq_ap_clients,
)

check_plugin_xiq_rate_limits = CheckPlugin(
    name="xiq_rate_limits",
    sections=["extreme_cloud_iq_rate_limits"],
    service_name="XIQ API Rate Limits",
    discovery_function=discover_rate_limits,
    check_function=check_xiq_rate_limits,
)

check_plugin_xiq_ssid_clients = CheckPlugin(
    name="xiq_ssid_clients",
    sections=["xiq_radio_information", "extreme_ap_status", "extreme_ap_clients"],
    service_name="XIQ SSID %s",
    discovery_function=discover_xiq_ssids,
    check_function=check_xiq_ssid,
    check_default_parameters={
        "global_levels": (None, None),   # z. B. (100, 150)
        "per_band": {
            # Optional: z. B. "2.4GHz": (50, 80), "5GHz": (100, 150)
        },
    },
    check_ruleset_name="xiq_ssid_clients",
)

# Ein Service pro Frequenz inkl. Parameter/Ruleset
check_plugin_xiq_radios = CheckPlugin(
    name="xiq_radios",
    sections=["xiq_radio_information", "extreme_ap_status", "extreme_ap_clients"],
    service_name="XIQ AP %s Radio",
    discovery_function=discover_xiq_radios,
    check_function=check_xiq_radios,
    check_default_parameters={
        "global_levels": (None, None),
        "per_band": {},
    },
    check_ruleset_name="xiq_radios_clients",
)


# Inventory plugins
inventory_plugin_xiq_devices = InventoryPlugin(
    name="xiq_inventory_devices",
    sections=["extreme_device_inventory"],
    inventory_function=inventory_xiq_devices,
)

inventory_plugin_xiq_neighbors = InventoryPlugin(
    name="xiq_inventory_neighbors",
    sections=["extreme_device_neighbors"],
    inventory_function=inventory_xiq_neighbors,
)

inventory_plugin_xiq_radio_parent = InventoryPlugin(
    name="xiq_radio_parent",
    sections=["xiq_radio_information"],
    inventory_function=inventory_xiq_radio_parent,
)

inventory_plugin_xiq_radio_bssid_children = InventoryPlugin(
    name="xiq_radio_children",
    sections=["xiq_radio_information"],
    inventory_function=inventory_xiq_radio_bssid_children,
)

inventory_plugin_xiq_bssids_by_ssid = InventoryPlugin(
    name="xiq_bssids_by_ssid",
    sections=["xiq_radio_information"],
    inventory_function=inventory_xiq_bssids_by_ssid,
)


