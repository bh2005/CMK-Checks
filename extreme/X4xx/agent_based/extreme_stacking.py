#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - Stacking Check (Role & Operational Status)
Checkmk 2.4 - Check API v2

Install path: ~/local/lib/python3/cmk_addons/plugins/extreme_networks/agent_based/
Author: bh2005
License: GPL v2
"""
from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    exists,
)

_ROLE_MAP = {
    "1": "Master",
    "2": "Backup",
    "3": "Standby",
    "4": "Disabled",
}

_STATE_MAP = {
    "1": "Up",
    "2": "Down",
    "3": "Version Mismatch",
}


def parse_extreme_stacking(string_table: StringTable) -> Dict[str, Dict[str, str]]:
    """Parses Extreme Stacking table (slot -> role + oper status)."""
    parsed: Dict[str, Dict[str, str]] = {}
    for line in string_table:
        if len(line) < 3:
            continue
        slot_id = line[0].strip()
        role = line[1].strip()
        oper_status = line[2].strip()
        parsed[slot_id] = {"role": role, "status": oper_status}
    return parsed


snmp_section_extreme_stacking = SimpleSNMPSection(
    name="extreme_stacking",
    parse_function=parse_extreme_stacking,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.33.2.1",
        oids=["2", "4", "3"],
    ),
    detect=exists(".1.3.6.1.4.1.1916.1.33.2.1.2"),
)


def discover_extreme_stacking(section: Dict[str, Dict[str, str]]) -> DiscoveryResult:
    """Discovers one service per stack slot."""
    for slot_id in sorted(section):
        yield Service(item=slot_id)


def check_extreme_stacking(
    item: str,
    params: Mapping[str, Any],
    section: Dict[str, Dict[str, str]],
) -> CheckResult:
    """Checks role and operational status of a stack slot."""
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Slot {item} not found in SNMP data",
        )
        return

    member = section[item]
    role_id = member["role"]
    status_id = member["status"]

    role_str = _ROLE_MAP.get(role_id, f"Unknown ({role_id})")
    status_str = _STATE_MAP.get(status_id, f"Unknown ({status_id})")

    # Check expected role from rule (optional)
    expected_role = params.get("expected_role")

    state = State.OK
    if status_id != "1":
        state = State.CRIT
    elif role_id == "4":
        state = State.WARN
    elif expected_role is not None and role_id != expected_role:
        state = State.WARN

    yield Metric("stack_role", int(role_id), boundaries=(1, 4))
    yield Metric("stack_status", int(status_id), boundaries=(1, 3))
    yield Result(
        state=state,
        summary=f"Role: {role_str}, Status: {status_str}",
        details=f"Raw Role ID: {role_id}, Raw Status ID: {status_id}",
    )


check_plugin_extreme_stacking = CheckPlugin(
    name="extreme_stacking",
    sections=["extreme_stacking"],
    service_name="Stack Slot %s",
    discovery_function=discover_extreme_stacking,
    check_function=check_extreme_stacking,
    check_default_parameters={},
    check_ruleset_name="extreme_stacking",
)
