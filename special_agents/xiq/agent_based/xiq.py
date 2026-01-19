
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

Inventory:
  - Devices (AP/SW/MISC)
  - LLDP/CDP Neighbors
"""

from typing import Mapping, Any, Iterable, List, Optional
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
#    Table,
#    Columns,
#    Column,
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

    # Beispiel-Agentzeile:
    # "STATUS:OK CODE:200 RESPONSE:Token valid and data fetched"
    raw = " ".join(table[0]).strip()
    if not raw:
        return None

    res: dict[str, str] = {"RAW": raw}

    def _get_value(tag: str) -> Optional[str]:
        pos = raw.find(tag)
        if pos == -1:
            return None
        pos += len(tag)
        # Ende ist die nächste Tag-Position oder das Zeilenende
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
            # numerisch, wenn möglich
            if val.isdigit():
                res[key] = int(val)
            else:
                try:
                    # Float (falls reset Sekunden als Zahl mit Nachkommastellen kämen)
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
            "hostname":       row[1],  # lokaler Hostname (ehem. Device Id-Spalte in der Anzeige)
            "hostaddress":    row[2],  # lokale IP
            "local_port":     row[3],  # ehem. Interface Name
            "management_ip":  row[4],  # Remote Mgmt IP
            "remote_port":    row[5],  # ehem. Port
            "port_description": row[6],
            "mac_address":    row[7],  # ehem. System Id
            "remote_device":  row[8],  # ehem. System Name
        })
    return result



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

    # Unlimited → keine Limit-Header vorhanden
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

    # Thresholds (kritisch <5%, warn <10%)
    if limit and remaining is not None:
        ratio = float(remaining) / float(limit)
        if ratio < 0.05:
            yield Result(state=State.CRIT, summary=summary)
            return
        if ratio < 0.10:
            yield Result(state=State.WARN, summary=summary)
            return

    yield Result(state=State.OK, summary=summary)



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

        # location leaf extraction
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
        mac_address   = format_mac(row.get("mac_address", ""))  # optional: anzeigenormiert

        # Alle sichtbaren Spalten als key_columns -> Reihenfolge exakt wie gewünscht
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
            inventory_columns={},  # keine weiteren Spalten -> kein Alphabetisierungs-Effekt
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
