#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - Hardware Check (CPU & Temperature)
Checkmk 2.4 - Check API v2

Install path: ~/local/lib/python3/cmk_addons/plugins/extreme_networks/agent_based/
Author: bh2005
License: GPL v2
"""
from typing import Any, Mapping, Optional

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
    all_of,
    check_levels,
    contains,
    exists,
)


def parse_extreme_hw(string_table: StringTable) -> Optional[Mapping[str, float]]:
    if not string_table or len(string_table[0]) < 2:
        return None
    try:
        return {
            "temp": float(string_table[0][0]),
            "cpu_5min": float(string_table[0][1]),
        }
    except (ValueError, IndexError):
        return None



snmp_section_extreme_hw = SimpleSNMPSection(
    name="extreme_hw",
    parse_function=parse_extreme_hw,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.1.1",
        oids=["8.0", "27.0"],
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.4.1.1916.1.1.1.8.0"),
    ),
)


def discover_extreme_hw(section: Mapping[str, float]) -> DiscoveryResult:
    if section:
        yield Service()


def check_extreme_hw(
    params: Mapping[str, Any], section: Mapping[str, float]
) -> CheckResult:
    temp = section.get("temp")
    cpu = section.get("cpu_5min")

    if temp is not None:
        temp_warn, temp_crit = params.get("temp_levels", (80.0, 95.0))
        yield from check_levels(
            temp,
            metric_name="temp",
            levels_upper=("fixed", (temp_warn, temp_crit)),
            render_func=lambda v: f"{v:.1f} C",
            label="Temperature",
            boundaries=(None, None),
        )

    if cpu is not None:
        cpu_warn, cpu_crit = params.get("cpu_levels", (70.0, 90.0))
        yield from check_levels(
            cpu,
            metric_name="cpu_load5",
            levels_upper=("fixed", (cpu_warn, cpu_crit)),
            render_func=lambda v: f"{v:.1f}%",
            label="CPU load (5 min)",
            boundaries=(0.0, 100.0),
        )


check_plugin_extreme_hw = CheckPlugin(
    name="extreme_hw",
    service_name="Hardware Health",
    discovery_function=discover_extreme_hw,
    check_function=check_extreme_hw,
    check_default_parameters={},
    check_ruleset_name="extreme_hw",
)
