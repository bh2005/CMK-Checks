#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - Interface Egress Errors Check
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
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
    check_levels,
    exists,
)


def parse_extreme_errors(string_table: StringTable) -> Mapping[str, int]:
    """Parses Extreme egress errors per interface index."""
    parsed: Dict[str, int] = {}
    for line in string_table:
        if len(line) < 2:
            continue
        try:
            ifindex = line[0].strip()
            errors = int(line[1])
            if errors >= 0:
                parsed[ifindex] = errors
        except (ValueError, IndexError):
            continue
    return parsed


snmp_section_extreme_errors = SimpleSNMPSection(
    name="extreme_errors",
    parse_function=parse_extreme_errors,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.1.1.34.1",
        oids=["1", "2"],  # ifIndex, extremePortEgressErrors
    ),
    detect=exists(".1.3.6.1.4.1.1916.1.1.1.34.1.1"),
)


def discover_extreme_errors(section: Mapping[str, int]) -> DiscoveryResult:
    """Discovers one service per interface with egress errors > 0."""
    for ifindex, errors in sorted(section.items()):
        if errors > 0:
            yield Service(item=ifindex)


def check_extreme_errors(
    item: str,
    params: Mapping[str, Any],
    section: Mapping[str, int],
) -> CheckResult:
    """Checks egress errors on a single interface."""
    errors = section.get(item)
    if errors is None:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Interface {item} not found in SNMP data",
        )
        return

    warn_threshold, crit_threshold = params.get("egress_errors_levels", (10, 50))

    yield from check_levels(
        float(errors),
        metric_name="egress_errors",
        levels_upper=("fixed", (float(warn_threshold), float(crit_threshold))),
        render_func=lambda v: f"{int(v)} Errors",
        label="Egress Errors",
        boundaries=(0.0, None),
    )


check_plugin_extreme_errors = CheckPlugin(
    name="extreme_errors",
    sections=["extreme_errors"],
    service_name="Interface Egress Errors %s",
    discovery_function=discover_extreme_errors,
    check_function=check_extreme_errors,
    check_default_parameters={},
    check_ruleset_name="extreme_errors",
)
