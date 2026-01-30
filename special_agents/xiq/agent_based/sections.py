#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Mapping, Any, Optional, List, Dict
import json
import time

from cmk.agent_based.v2 import (
    AgentSection,
    StringTable,
)

from .common import format_mac, _clean_text


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def parse_xiq_login(table: StringTable) -> Optional[Mapping[str, str]]:
    if not table:
        return None
    raw = " ".join(table[0]).strip()
    if not raw:
        return None
    res: Dict[str, str] = {"RAW": raw}

    def _extract(tag: str) -> Optional[str]:
        pos = raw.find(tag)
        if pos == -1:
            return None
        pos += len(tag)
        ends = []
        for other in ("STATUS:", "CODE:", "RESPONSE:"):
            if other == tag:
                continue
            p = raw.find(other, pos)
            if p != -1:
                ends.append(p)
        end = min(ends) if ends else len(raw)
        return raw[pos:end].strip()

    status = _extract("STATUS:")
    code = _extract("CODE:")
    resp_pos = raw.find("RESPONSE:")
    response = raw[resp_pos + len("RESPONSE:"):].strip() if resp_pos != -1 else None

    if status:
        res["STATUS"] = status
    if code:
        res["CODE"] = code
    if response:
        res["RESPONSE"] = response
    return res


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def parse_xiq_summary(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None
    return {line[0]: line[1] for line in table if len(line) >= 2}


# ---------------------------------------------------------------------------
# AP STATUS
# ---------------------------------------------------------------------------
def parse_xiq_ap_status(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None
    row = table[0]

    def s(i: int) -> str:
        return row[i] if len(row) > i else ""

    up_raw = s(8).strip()
    uptime_seconds = 0
    uptime_ms = 0
    if up_raw:
        try:
            v = int(float(up_raw))
            now_s = int(time.time())
            now_ms = now_s * 1000
            if v >= 10**11:
                uptime_ms = max(0, now_ms - v)         # input was ms timestamp
                uptime_seconds = int(uptime_ms / 1000)
            elif v >= 10**9:
                uptime_seconds = max(0, now_s - v)      # input was s timestamp
                uptime_ms = uptime_seconds * 1000
            elif v > 10**7:
                uptime_seconds = v                      # input already seconds
                uptime_ms = v * 1000
            else:
                uptime_ms = v                           # input was ms uptime
                uptime_seconds = int(v / 1000)
        except Exception:
            pass

    return {
        "ap_name": s(0),
        "serial": s(1),
        "mac": format_mac(s(2)),
        "ip": s(3),
        "model": s(4),
        "connected": s(5) == "1",
        "state": s(6),
        "sw_version": s(7),

        "uptime_seconds": uptime_seconds,
        "uptime_ms": uptime_ms,
        "uptime_s": uptime_seconds,

        "locations": s(9),
        # compact LLDP/CDP preview, cleaned
        "lldp_cdp_short": _clean_text(s(10)),
    }


# ---------------------------------------------------------------------------
# CLIENTS
# ---------------------------------------------------------------------------
def parse_xiq_ap_clients(table: StringTable) -> Optional[Mapping[str, int]]:
    if not table:
        return None
    row = table[0]

    def to(i: int) -> int:
        try:
            return int(row[i])
        except Exception:
            return 0

    return {"clients_24": to(0), "clients_5": to(1), "clients_6": to(2)}


# ---------------------------------------------------------------------------
# RATE LIMITS
# ---------------------------------------------------------------------------
def parse_xiq_rate_limits(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None
    res: Dict[str, Any] = {}
    headers: List[str] = []
    in_headers = False

    for line in table:
        if len(line) != 2:
            continue
        key_raw, val_raw = line[0].strip(), (line[1] or "").strip()
        k = key_raw.lower()

        if k == "headers_begin":
            in_headers = True
            continue
        if k == "headers_end":
            in_headers = False
            continue
        if in_headers and k == "header":
            if val_raw:
                headers.append(val_raw)
            continue

        if k == "state":
            res["state"] = val_raw or "OK"
        elif k in ("limit", "ratelimit-limit"):
            main = val_raw.split(";", 1)[0]
            try:
                res["limit"] = int(main)
            except Exception:
                try:
                    res["limit"] = int(float(main))
                except Exception:
                    pass
            if ";w=" in val_raw:
                try:
                    res["window_s"] = int(val_raw.split(";w=", 1)[1])
                except Exception:
                    pass
        elif k in ("remaining", "ratelimit-remaining"):
            try:
                res["remaining"] = int(val_raw)
            except Exception:
                try:
                    res["remaining"] = int(float(val_raw))
                except Exception:
                    pass
        elif k in ("reset_in_seconds", "ratelimit-reset", "reset"):
            try:
                res["reset_in_seconds"] = int(val_raw)
            except Exception:
                try:
                    res["reset_in_seconds"] = int(float(val_raw))
                except Exception:
                    pass
        elif k == "window_s":
            try:
                res["window_s"] = int(val_raw)
            except Exception:
                pass

    if headers:
        res["_headers"] = headers
    return res if res else None


# ---------------------------------------------------------------------------
# DEVICE INVENTORY
# ---------------------------------------------------------------------------
def parse_xiq_device_inventory(table: StringTable) -> List[List[str]]:
    result: List[List[str]] = []
    for row in table:
        if len(row) >= 10:
            result.append(row)
    return result


# ---------------------------------------------------------------------------
# NEIGHBORS (LLDP/CDP) – fully cleaned
# ---------------------------------------------------------------------------
def parse_xiq_device_neighbors(table: StringTable) -> List[Mapping[str, str]]:
    result: List[Mapping[str, str]] = []
    for row in table:
        if len(row) < 9:
            continue
        result.append({
            "device_id":        _clean_text(row[0]),
            "hostname":         _clean_text(row[1]),
            "host_ip":          _clean_text(row[2]),
            "local_port":       _clean_text(row[3]),
            "management_ip":    _clean_text(row[4]),
            "remote_port":      _clean_text(row[5]),
            "port_description": _clean_text(row[6]),
            "mac_address":      format_mac(_clean_text(row[7])),
            "remote_device":    _clean_text(row[8]),
        })
    return result


# ---------------------------------------------------------------------------
# RADIO INFORMATION (JSON) – includes policies
# ---------------------------------------------------------------------------
def parse_xiq_radio_information(table: StringTable) -> Optional[Mapping[str, Any]]:
    if not table:
        return None

    raw = "".join("".join(row) for row in table).strip()
    if not raw.startswith("{"):
        return None

    try:
        data = json.loads(raw)
    except Exception:
        return None

    device_id = data.get("device_id")
    hostname = data.get("hostname") or ""
    radios_in = data.get("radios") or []

    result: Dict[str, Any] = {}
    result["_radios"] = []
    result["_device_id"] = device_id
    result["_hostname"] = hostname
    result["_ssid_freq"] = {}

    # For discovery / aggregation: SSID per band
    freq_map: Dict[str, List[Dict[str, Any]]] = {"2.4GHz": [], "5GHz": [], "6GHz": []}

    for r in radios_in:
        freq = str(r.get("frequency") or "").strip()
        if not freq:
            mode = str(r.get("mode") or "").lower()
            if "5g" in mode:
                freq = "5GHz"
            elif "6g" in mode:
                freq = "6GHz"
            else:
                freq = "2.4GHz"

        if freq not in freq_map:
            freq = "2.4GHz"

        wlans_in = r.get("wlans") or []
        wlans_out: List[Dict[str, str]] = []
        ssid_list: List[str] = []
        bssid_list: List[str] = []

        for w in wlans_in:
            ssid = str(w.get("ssid") or "").strip()
            policy = str(w.get("network_policy_name") or "").strip()
            bssid = format_mac(str(w.get("bssid") or ""))

            entry = {
                "ssid": ssid,
                "bssid": bssid,
                "policy": policy,
            }
            wlans_out.append(entry)

            if ssid:
                ssid_list.append(ssid)
            if bssid:
                bssid_list.append(bssid)
            if ssid or bssid:
                freq_map[freq].append(entry)

        # try to consolidate client count from multiple possible keys
        client_count = 0
        for key in ("active_clients", "connected_clients", "client_count"):
            try:
                vc = int(r.get(key))
                if vc >= 0:
                    client_count = vc
                    break
            except Exception:
                pass

        result["_radios"].append({
            "device_id": device_id,
            "hostname": hostname,
            "radio_name": str(r.get("name") or ""),
            "radio_mac": format_mac(str(r.get("mac_address") or "")),
            "frequency": freq,
            "channel_number": int(r.get("channel_number") or 0),
            "channel_width": str(r.get("channel_width") or ""),
            "mode": str(r.get("mode") or ""),
            "power": int(r.get("power") or 0),
            "wlans": wlans_out,
            "ssid_list": ssid_list,
            "bssid_list": bssid_list,
            "client_count": client_count,
        })

    result.update(freq_map)
    return result


# ---------------------------------------------------------------------------
# SECTION REGISTRATIONS
# ---------------------------------------------------------------------------
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

agent_section_xiq_radios = AgentSection(
    name="xiq_radio_information",
    parse_function=parse_xiq_radio_information,
)

agent_section_xiq_ap_neighbors = AgentSection(
    name="extreme_ap_neighbors",
    parse_function=parse_xiq_device_neighbors,
)
