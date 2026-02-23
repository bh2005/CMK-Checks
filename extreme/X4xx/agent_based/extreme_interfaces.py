#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - PoE Budget
Checkmk 2.4 - Check API v2

Install path: ~/local/lib/python3/cmk_addons/plugins/extreme_networks/agent_based/
Author: bh2005
License: GPL v2
"""
from typing import Any, Mapping

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


def parse_extreme_poe(string_table: StringTable) -> Mapping[str, float]:
    """Parses Extreme PoE budget (total + used watts)."""
    if not string_table or len(string_table[0]) < 2:
        return {}
    try:
        return {
            "budget": float(string_table[0][0]),
            "used": float(string_table[0][1]),
        }
    except (ValueError, IndexError):
        return {}


snmp_section_extreme_poe = SimpleSNMPSection(
    name="extreme_poe",
    parse_function=parse_extreme_poe,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1916.1.1.1.2",
        oids=["7.0", "8.0"],  # extremeSystemPowerBudgetTotal, extremeSystemPowerBudgetConsumed
    ),
    detect=all_of(
        contains(".1.3.6.1.2.1.1.1.0", "ExtremeXOS"),
        exists(".1.3.6.1.4.1.1916.1.1.1.2.7.0"),
    ),
)


def discover_extreme_poe(section: Mapping[str, float]) -> DiscoveryResult:
    """Discovers PoE Power Budget service if data available."""
    if section:
        yield Service()


def check_extreme_poe(
    params: Mapping[str, Any], section: Mapping[str, float]
) -> CheckResult:
    """Checks PoE budget usage with configurable thresholds."""
    budget = section.get("budget")
    used = section.get("used")

    if budget is None or used is None or budget <= 0:
        yield Result(state=State.UNKNOWN, summary="No PoE data available")
        return

    usage_pct = (used / budget) * 100
    warn_pct, crit_pct = params.get("poe_levels_pct", (80.0, 90.0))

    yield from check_levels(
        usage_pct,
        metric_name="poe_usage_pct",
        levels_upper=("fixed", (warn_pct, crit_pct)),
        render_func=lambda v: f"{v:.1f}%",
        label=f"PoE Used {used:.1f}W / {budget:.1f}W",
        boundaries=(0.0, 100.0),
    )
    yield Metric("poe_used_watts", used, boundaries=(0.0, budget))
    yield Metric("poe_total_watts", budget)


check_plugin_extreme_poe = CheckPlugin(
    name="extreme_poe",
    service_name="PoE Power Budget",
    discovery_function=discover_extreme_poe,
    check_function=check_extreme_poe,
    check_default_parameters={},
    check_ruleset_name="extreme_poe",
)
