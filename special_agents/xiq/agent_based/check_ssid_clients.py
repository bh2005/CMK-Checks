#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Mapping, Any, Iterable, Optional, List

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
)

from cmk_addons.plugins.xiq.agent_based.common import format_mac


# -----------------------------------------------------------------------------
# DISCOVERY
# -----------------------------------------------------------------------------
def discover_xiq_ssids(
    section_xiq_radio_information: Optional[Mapping[str, Any]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],
    section_extreme_ap_clients: Optional[Mapping[str, int]],
) -> DiscoveryResult:

    if not section_xiq_radio_information:
        return

    ssids: set[str] = set()

    ssid_freq_map = section_xiq_radio_information.get("_ssid_freq") or {}
    ssids.update(ssid_freq_map.keys())

    if not ssids:
        radios = (
            section_xiq_radio_information.get("_radios")
            or section_xiq_radio_information.get("radios")
            or []
        )
        for r in radios:
            for wlan in r.get("wlans", []):
                s = (wlan.get("ssid") or "").strip()
                if s:
                    ssids.add(s)

    for ssid in sorted(ssids):
        yield Service(item=ssid)


# -----------------------------------------------------------------------------
# CHECK FUNCTION
# -----------------------------------------------------------------------------
def check_xiq_ssid_clients(
    item: str,
    params: Mapping[str, Any],
    section_xiq_radio_information: Optional[Mapping[str, Any]],
    section_extreme_ap_status: Optional[Mapping[str, Any]],
    section_extreme_ap_clients: Optional[Mapping[str, int]],
) -> Iterable[CheckResult]:

    if not section_xiq_radio_information:
        return

    ap_name = section_extreme_ap_status.get("ap_name", "") if section_extreme_ap_status else ""
    ssid = item

    radios = (
        section_xiq_radio_information.get("_radios")
        or section_xiq_radio_information.get("radios")
        or []
    )

    ssid_freq_map = section_xiq_radio_information.get("_ssid_freq") or {}

    counts = {"2.4GHz": 0, "5GHz": 0, "6GHz": 0}
    notices: List[str] = []

    for r in radios:
        freq = r.get("frequency", "")
        if freq not in counts:
            continue

        wlans = r.get("wlans", [])
        clients_total = int(r.get("client_count") or 0)

        if ssid in ssid_freq_map:
            try:
                per_freq = int(ssid_freq_map[ssid].get(freq, 0))
                if per_freq > 0:
                    counts[freq] += per_freq
                    continue
            except Exception:
                pass

        ssids_on_radio = [w.get("ssid") for w in wlans]
        if ssids_on_radio == [ssid]:
            counts[freq] += clients_total
        else:
            if clients_total > 0 and ssid in ssids_on_radio:
                notices.append(
                    f"{freq}: {clients_total} Clients auf Radio '{r.get('radio_name')}' "
                    f"mit {len(ssids_on_radio)} SSIDs – Verteilung unbekannt"
                )

    total = sum(counts.values())

    warn = crit = None
    gl = (params or {}).get("global_levels")
    if isinstance(gl, (list, tuple)) and len(gl) >= 2:
        warn, crit = gl[0], gl[1]

    state = State.OK
    if crit is not None and total >= crit:
        state = State.CRIT
    elif warn is not None and total >= warn:
        state = State.WARN

    prefix = f"AP {ap_name}: " if ap_name else ""
    yield Result(
        state=state,
        summary=(
            f"{prefix}SSID {ssid}: {total} Clients "
            f"(2.4GHz {counts['2.4GHz']}, 5GHz {counts['5GHz']}, 6GHz {counts['6GHz']})"
        ),
    )

    # -------------------------------------------------------------------------
    # BSSID & Policy
    # -------------------------------------------------------------------------
    bssids = {"2.4GHz": "", "5GHz": "", "6GHz": ""}
    policy = ""

    for r in radios:
        freq = r.get("frequency", "")
        if freq not in bssids:
            continue

        for wlan in r.get("wlans", []):
            if wlan.get("ssid") == ssid:
                bssids[freq] = format_mac(wlan.get("bssid", ""))
                if not policy:
                    policy = wlan.get("policy", "")

    # -------------------------------------------------------------------------
    # Details-Block (Markdown)
    # -------------------------------------------------------------------------

    details = (
        "**Radios**\n"
        f"- 2.4 GHz : {bssids['2.4GHz'] or '-'}\n"
        f"- 5   GHz : {bssids['5GHz'] or '-'}\n"
        f"- 6   GHz : {bssids['6GHz'] or '-'}\n"
        "\n**Policy**\n"
        f"- NetworkPolicy : {policy or '-'}"
    )


    yield Result(state=State.OK, notice=details)

    for n in notices:
        yield Result(state=State.OK, notice=n)

    yield Metric("xiq_ssid_clients_total", float(total))


# -----------------------------------------------------------------------------
# REGISTRATION
# -----------------------------------------------------------------------------
check_plugin_xiq_ssid_clients_plugin = CheckPlugin(
    name="xiq_ssid_clients",
    sections=["xiq_radio_information", "extreme_ap_status", "extreme_ap_clients"],
    service_name="XIQ SSID %s",
    discovery_function=discover_xiq_ssids,
    check_function=check_xiq_ssid_clients,
    check_default_parameters={"global_levels": (None, None)},
    check_ruleset_name="xiq_ssid_clients",
)