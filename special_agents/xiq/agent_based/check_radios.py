#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Mapping, Any, Iterable, Optional
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
)

def discover_xiq_radios(
    section_xiq_radio_information: Optional[Mapping[str, Any]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],
    section_extreme_ap_clients: Optional[Mapping[str, int]],
) -> DiscoveryResult:
    if not section_xiq_radio_information or not section_extreme_ap_status:
        return
    ap_name = section_extreme_ap_status.get("ap_name")
    if not ap_name:
        return
    for freq in ("2.4GHz", "5GHz", "6GHz"):
        if freq in section_xiq_radio_information:
            yield Service(item=f"{ap_name} {freq}")

def check_xiq_radios(
    item: str,
    params: Mapping[str, Any],
    section_xiq_radio_information: Optional[Mapping[str, Any]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],
    section_extreme_ap_clients: Optional[Mapping[str, int]],
) -> Iterable[CheckResult]:
    if not section_xiq_radio_information or not section_extreme_ap_status:
        return

    ap_name = section_extreme_ap_status.get("ap_name", "")
    freq = item[len(ap_name):].strip() if ap_name and item.startswith(ap_name) else item

    radios = section_xiq_radio_information.get("_radios") or []
    clients_total = 0
    channels = []
    powers = []
    radio_names = []

    for r in radios:
        if r.get("frequency") == freq:
            clients_total += int(r.get("client_count") or 0)
            ch = r.get("channel_number")
            if ch not in (None, ""):
                channels.append(str(ch))
            pw = r.get("power")
            if pw not in (None, ""):
                powers.append(str(pw))
            rn = (r.get("radio_name") or "").strip()
            if rn:
                radio_names.append(rn)

    details = []
    if channels:
        details.append(f"Channels: {', '.join(sorted(set(channels)))}")
    if powers:
        details.append(f"Power: {', '.join(sorted(set(powers)))} dBm")
    if radio_names:
        details.append(f"Radios: {', '.join(sorted(set(radio_names)))}")

    suffix = " | " + " • ".join(details) if details else ""
    yield Result(state=State.OK, summary=f"{item}: {clients_total} Clients{suffix}")
    yield Metric("xiq_radio_clients_total", float(clients_total))

check_plugin_xiq_radios = CheckPlugin(
    name="xiq_radios",
    sections=["xiq_radio_information", "extreme_ap_status", "extreme_ap_clients"],
    service_name="XIQ AP %s Radio",
    discovery_function=discover_xiq_radios,
    check_function=check_xiq_radios,
    check_default_parameters={"global_levels": (None, None), "per_band": {}},
    check_ruleset_name="xiq_radios_clients",
)
