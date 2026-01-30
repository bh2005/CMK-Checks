# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Iterable, List, Dict, Set
import re
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from .common import _shorten_location_to_loc_leaf, _clean_text


def discover_xiq_aps(section_extreme_ap_status,
                     section_extreme_ap_neighbors,
                     section_xiq_radio_information) -> DiscoveryResult:
    """Discover exactly one service per AP using 'ap_name' from the status section."""
    if not section_extreme_ap_status:
        return
    ap_name = section_extreme_ap_status.get("ap_name")
    if ap_name:
        yield Service(item=ap_name)


def _map_state(connected: bool, state_text: str) -> State:
    """Optional finer state mapping."""
    if connected:
        return State.OK
    st = (state_text or "").strip().lower()
    if st in {"provisioning", "configuring", "adopting"}:
        return State.WARN
    return State.CRIT


def _clean_lldp_short(lldp_str: str) -> str:
    """Compact LLDP/CDP string: drop any (...) fragments and extra spaces; also clean suffix markers."""
    if not lldp_str:
        return ""
    s = re.sub(r"\([^)]*\)", "", lldp_str).strip()
    s = _clean_text(s)
    s = re.sub(r"\s{2,}", " ", s)
    return s


def _fmt_kv(key: str, value: str) -> str:
    """Uniform '- Key: Value' line (ASCII-only)."""
    v = (value or "").strip()
    if not v:
        return ""
    return f"- {key}: {v}"


def _neighbors_detailed_lines(nei: Any) -> List[str]:
    """
    Build a detailed list of neighbors.
    Expects a list[dict], otherwise returns empty list.
    """
    if not isinstance(nei, list):
        return []
    field_order = [
        ("local_port",       "Local Port"),
        ("remote_device",    "Remote Device"),
        ("management_ip",    "Remote Mgmt-IP"),
        ("remote_port",      "Remote Port"),
        ("port_description", "Port Desc"),
        ("mac_address",      "MAC"),
        ("device_id",        "Device-ID"),
    ]
    lines: List[str] = []
    for idx, entry in enumerate(nei, start=1):
        if not isinstance(entry, dict):
            continue
        lines.append(f"- Neighbor #{idx}:")
        for fkey, ftitle in field_order:
            val = (entry.get(fkey) or "")
            if val:
                lines.append(f"  - {ftitle}: {_clean_text(str(val))}")
    return lines


def _extract_policies(radio_info: Any) -> List[str]:
    """
    Collect unique policy names from 'xiq_radio_information'.
    Expected structure:
      radio_info["_radios"][i]["wlans"] -> [{"ssid":..., "bssid":..., "policy": ...}, ...]
    """
    policies: Set[str] = set()
    if isinstance(radio_info, dict):
        radios = radio_info.get("_radios") or []
        if isinstance(radios, list):
            for r in radios:
                wlans = (r or {}).get("wlans") or []
                if not isinstance(wlans, list):
                    continue
                for w in wlans:
                    p = (w or {}).get("policy")
                    if p:
                        policies.add(str(p).strip())
    return sorted(policies)


def check_xiq_ap_status(item,
                        section_extreme_ap_status,
                        section_extreme_ap_neighbors,
                        section_xiq_radio_information) -> Iterable[CheckResult]:
    """AP status: compact summary + clear long output including LLDP full and policies."""
    if not section_extreme_ap_status:
        yield Result(state=State.UNKNOWN, summary=f"{item}: keine Statusdaten vorhanden")
        return

    s = section_extreme_ap_status
    connected   = bool(s.get("connected", False))
    model       = s.get("model", "?")
    state_t     = s.get("state", "")
    sw          = s.get("sw_version", "")
    ip_addr     = s.get("ip", "")
    loc_full    = s.get("locations", "")  # now full path from agent; may be short if agent cannot provide full
    lldp_short  = _clean_lldp_short(s.get("lldp_cdp_short", ""))

    # Neighbors come piggybacked for this AP; already the full list for this AP
    neighbors = section_extreme_ap_neighbors if isinstance(section_extreme_ap_neighbors, list) else []

    # Policies from radio-information section
    policies  = _extract_policies(section_xiq_radio_information)

    # Leaf for summary bit (if full path present)
    loc_leaf = _shorten_location_to_loc_leaf(loc_full) if loc_full else ""

    # Summary bits
    bits: List[str] = []
    if sw:
        bits.append(f"FW: {sw}")
    if ip_addr:
        bits.append(f"IP: {ip_addr}")
    if loc_leaf:
        bits.append(f"Loc: {loc_leaf}")
    if lldp_short:
        bits.append(f"LLDP: {lldp_short}")

    human_state = "CONNECTED" if connected else (state_t or "DISCONNECTED")
    suffix = " | " + " | ".join(bits) if bits else ""

    # ---- Long Output ----
    lines: List[str] = []

    # Device
    lines.append("**Device**")
    lines.append(_fmt_kv("Name", item))
    lines.append(_fmt_kv("Model", model))
    if sw:
        lines.append(_fmt_kv("Firmware", sw))  # between Model and Serial
    serial = s.get("serial", "")
    if serial:
        lines.append(_fmt_kv("Serial", serial))

    # Location: prefer full path, else show short
    if loc_full and "/" in str(loc_full):
        lines.append(_fmt_kv("Location", loc_full))
        if loc_leaf:
            lines.append(_fmt_kv("Loc (short)", loc_leaf))
    elif loc_full:
        lines.append(_fmt_kv("Loc (short)", loc_full))

    # Policies (unique)
    if policies:
        lines.append(_fmt_kv("Policy", ", ".join(policies)))

    # Separator
    lines.append("------------------------------")

    # Network
    lines.append("**Network**")
    lines.append(_fmt_kv("Status", "Verbunden" if connected else "Nicht verbunden"))
    if ip_addr:
        lines.append(_fmt_kv("IP", ip_addr))

    # Separator
    lines.append("------------------------------")

    # LLDP Info (compact without prefix + detailed neighbors)
    if lldp_short or neighbors:
        lines.append("**LLDP Info**")
        if lldp_short:
            lines.append(f"- {lldp_short}")
        detailed = _neighbors_detailed_lines(neighbors)
        if detailed:
            lines.extend(detailed)

    yield Result(
        state=_map_state(connected, state_t),
        summary=f"{item} ({model}) {human_state}{suffix}",
        details="\n".join([ln for ln in lines if ln]),
    )


check_plugin_xiq_ap_status = CheckPlugin(
    name="xiq_ap_status",
    sections=[
        "extreme_ap_status",
        "extreme_ap_neighbors",     # piggybacked neighbors for this AP (full)
        "xiq_radio_information",
    ],
    service_name="XIQ AP %s Status",
    discovery_function=discover_xiq_aps,
    check_function=check_xiq_ap_status,
)
