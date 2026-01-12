#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    State,
    Service,
    Metric,
)

# 1. Summary Check (für den Host )
def discover_extreme_summary(section):
    yield DiscoveryResult()

def check_extreme_summary(section) -> CheckResult:
    for line in section:
        if len(line) < 2:
            continue
        key, value = line[0], line[1]
        yield Result(state=State.OK, summary=f"{key.replace('_', ' ').title()}: {value}")

CheckPlugin(
    name="extreme_summary",
    sections=["extreme_summary"],
    service_name="Extreme Cloud Summary",
    discovery_function=discover_extreme_summary,
    check_function=check_extreme_summary,
)

# 2. AP Status (Piggyback)
def discover_extreme_ap_status(section):
    yield DiscoveryResult()

def check_extreme_ap_status(section) -> CheckResult:
    if not section:
        return
    row = section[0]
    # hostname|sn|mac|ip|model|is_connected|conn_state|...
    if len(row) >= 7:
        is_connected = row[5]
        conn_state = row[6]
        state = State.OK if is_connected == "1" else State.CRIT
        yield Result(state=state, summary=f"Status: {conn_state}")
        yield Result(state=State.OK, summary=f"Modell: {row[4]}, IP: {row[3]}")

CheckPlugin(
    name="extreme_ap_status",
    sections=["extreme_ap_status"],
    service_name="AP Status",
    discovery_function=discover_extreme_ap_status,
    check_function=check_extreme_ap_status,
)