#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 bh2005
# License: GNU General Public License v2

"""
Check Plugins for Extreme Cloud IQ Access Points

This module provides check plugins for monitoring Extreme Networks Access Points.

Install to: local/lib/python3/cmk_addons/plugins/xiq_agent/agent_based/extreme_cloud_iq.py
"""

from typing import Any, Mapping
from collections.abc import Sequence

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
)


# =============================================================================
# Section 1: AP Status
# =============================================================================

class APStatus:
    """Data model for AP Status"""
    def __init__(self, data: Sequence[str]):
        # Format: hostname|serial|mac|ip|model|status|connection_state|sw_version|site
        self.hostname = data[0] if len(data) > 0 else "unknown"
        self.serial = data[1] if len(data) > 1 else "unknown"
        self.mac = data[2] if len(data) > 2 else "unknown"
        self.ip = data[3] if len(data) > 3 else "unknown"
        self.model = data[4] if len(data) > 4 else "unknown"
        self.status = data[5] if len(data) > 5 else "0"
        self.connection_state = data[6] if len(data) > 6 else "DISCONNECTED"
        self.software_version = data[7] if len(data) > 7 else "unknown"
        self.site = data[8] if len(data) > 8 else "N/A"


def parse_extreme_ap_status(string_table: StringTable) -> APStatus | None:
    """Parse extreme_ap_status section"""
    if not string_table or not string_table[0]:
        return None
    
    parts = string_table[0][0].split("|")
    return APStatus(parts)


agent_section_extreme_ap_status = AgentSection(
    name="extreme_ap_status",
    parse_function=parse_extreme_ap_status,
)


def discover_extreme_ap_status(section: APStatus) -> DiscoveryResult:
    """Discover AP status check"""
    if section:
        yield Service()


def check_extreme_ap_status(
    params: Mapping[str, Any],
    section: APStatus,
) -> CheckResult:
    """Check AP status"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    # Check connection status
    is_connected = section.status == "1"
    connection_state = section.connection_state
    
    if is_connected and connection_state == "CONNECTED":
        state = State.OK
        summary = "AP is connected"
    elif connection_state == "DISCONNECTED":
        state = State.CRIT
        summary = "AP is disconnected"
    else:
        state = State.WARN
        summary = f"AP state: {connection_state}"
    
    yield Result(state=state, summary=summary)
    
    # Add details
    yield Result(
        state=State.OK,
        notice=(
            f"Model: {section.model}, "
            f"Serial: {section.serial}, "
            f"MAC: {section.mac}, "
            f"IP: {section.ip}, "
            f"Software: {section.software_version}, "
            f"Site: {section.site}"
        ),
    )


check_plugin_extreme_ap_status = CheckPlugin(
    name="extreme_ap_status",
    service_name="Extreme AP Status",
    discovery_function=discover_extreme_ap_status,
    check_function=check_extreme_ap_status,
    check_default_parameters={},
)


# =============================================================================
# Section 2: AP Clients
# =============================================================================

class APClients:
    """Data model for AP Clients"""
    def __init__(self, data: Sequence[str]):
        # Format: total_clients|radio_2.4ghz|radio_5ghz
        self.total = int(data[0]) if len(data) > 0 and data[0].isdigit() else 0
        self.radio_2_4 = int(data[1]) if len(data) > 1 and data[1].isdigit() else 0
        self.radio_5 = int(data[2]) if len(data) > 2 and data[2].isdigit() else 0


def parse_extreme_ap_clients(string_table: StringTable) -> APClients | None:
    """Parse extreme_ap_clients section"""
    if not string_table or not string_table[0]:
        return None
    
    parts = string_table[0][0].split("|")
    return APClients(parts)


agent_section_extreme_ap_clients = AgentSection(
    name="extreme_ap_clients",
    parse_function=parse_extreme_ap_clients,
)


def discover_extreme_ap_clients(section: APClients) -> DiscoveryResult:
    """Discover AP clients check"""
    if section is not None:
        yield Service()


def check_extreme_ap_clients(
    params: Mapping[str, Any],
    section: APClients,
) -> CheckResult:
    """Check AP client count"""
    if section is None:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    # Get thresholds
    warn_level = params.get("clients_warn", 50)
    crit_level = params.get("clients_crit", 80)
    
    # Check total clients
    yield from check_levels(
        value=section.total,
        levels_upper=(warn_level, crit_level),
        metric_name="clients_total",
        label="Total clients",
        render_func=str,
    )
    
    # Add details about radio split
    yield Result(
        state=State.OK,
        notice=f"2.4GHz: {section.radio_2_4}, 5GHz: {section.radio_5}",
    )
    
    # Additional metrics
    yield Metric("clients_2_4ghz", section.radio_2_4)
    yield Metric("clients_5ghz", section.radio_5)


check_plugin_extreme_ap_clients = CheckPlugin(
    name="extreme_ap_clients",
    service_name="Extreme AP Clients",
    discovery_function=discover_extreme_ap_clients,
    check_function=check_extreme_ap_clients,
    check_default_parameters={
        "clients_warn": 50,
        "clients_crit": 80,
    },
    check_ruleset_name="extreme_ap_clients",
)


# =============================================================================
# Section 3: AP Details (CPU, Memory, Uptime)
# =============================================================================

class APDetails:
    """Data model for AP Details"""
    def __init__(self, data: Sequence[str]):
        # Format: cpu_usage|memory_usage|uptime|power_mode|poe_power
        self.cpu_usage = float(data[0]) if len(data) > 0 else 0.0
        self.memory_usage = float(data[1]) if len(data) > 1 else 0.0
        self.uptime = int(data[2]) if len(data) > 2 and data[2].isdigit() else 0
        self.power_mode = data[3] if len(data) > 3 else "unknown"
        self.poe_power = float(data[4]) if len(data) > 4 else 0.0


def parse_extreme_ap_details(string_table: StringTable) -> APDetails | None:
    """Parse extreme_ap_details section"""
    if not string_table or not string_table[0]:
        return None
    
    parts = string_table[0][0].split("|")
    return APDetails(parts)


agent_section_extreme_ap_details = AgentSection(
    name="extreme_ap_details",
    parse_function=parse_extreme_ap_details,
)


def discover_extreme_ap_details(section: APDetails) -> DiscoveryResult:
    """Discover AP details check"""
    if section is not None:
        yield Service()


def check_extreme_ap_details(
    params: Mapping[str, Any],
    section: APDetails,
) -> CheckResult:
    """Check AP details (CPU, Memory, Uptime)"""
    if section is None:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    # CPU Check
    cpu_warn = params.get("cpu_warn", 80.0)
    cpu_crit = params.get("cpu_crit", 90.0)
    
    yield from check_levels(
        value=section.cpu_usage,
        levels_upper=(cpu_warn, cpu_crit),
        metric_name="cpu_utilization",
        label="CPU",
        render_func=lambda v: f"{v:.1f}%",
    )
    
    # Memory Check
    mem_warn = params.get("memory_warn", 80.0)
    mem_crit = params.get("memory_crit", 90.0)
    
    yield from check_levels(
        value=section.memory_usage,
        levels_upper=(mem_warn, mem_crit),
        metric_name="memory_utilization",
        label="Memory",
        render_func=lambda v: f"{v:.1f}%",
    )
    
    # Uptime
    uptime_days = section.uptime / 86400
    yield Result(
        state=State.OK,
        notice=f"Uptime: {uptime_days:.1f} days",
    )
    yield Metric("uptime", section.uptime)
    
    # Power Info
    yield Result(
        state=State.OK,
        notice=f"Power Mode: {section.power_mode}, PoE: {section.poe_power}W",
    )
    yield Metric("poe_power", section.poe_power)


check_plugin_extreme_ap_details = CheckPlugin(
    name="extreme_ap_details",
    service_name="Extreme AP Details",
    discovery_function=discover_extreme_ap_details,
    check_function=check_extreme_ap_details,
    check_default_parameters={
        "cpu_warn": 80.0,
        "cpu_crit": 90.0,
        "memory_warn": 80.0,
        "memory_crit": 90.0,
    },
    check_ruleset_name="extreme_ap_details",
)


# =============================================================================
# Section 4: Summary (Main Host)
# =============================================================================

class ExtremeSummary:
    """Data model for Extreme Summary"""
    def __init__(self, data: Mapping[str, int]):
        self.access_points = data.get("access_points", 0)
        self.total_clients = data.get("total_clients", 0)


def parse_extreme_summary(string_table: StringTable) -> ExtremeSummary | None:
    """Parse extreme_summary section"""
    if not string_table or not string_table[0]:
        return None
    
    # Format: access_points=X|total_clients=Y
    data = {}
    for item in string_table[0][0].split("|"):
        if "=" in item:
            key, value = item.split("=", 1)
            try:
                data[key] = int(value)
            except ValueError:
                pass
    
    return ExtremeSummary(data)


agent_section_extreme_summary = AgentSection(
    name="extreme_summary",
    parse_function=parse_extreme_summary,
)


def discover_extreme_summary(section: ExtremeSummary) -> DiscoveryResult:
    """Discover summary check"""
    if section:
        yield Service()


def check_extreme_summary(
    params: Mapping[str, Any],
    section: ExtremeSummary,
) -> CheckResult:
    """Check overall Extreme infrastructure summary"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    summary = f"{section.access_points} Access Points, {section.total_clients} total clients"
    
    yield Result(state=State.OK, summary=summary)
    yield Metric("access_points", section.access_points)
    yield Metric("total_clients", section.total_clients)


check_plugin_extreme_summary = CheckPlugin(
    name="extreme_summary",
    service_name="Extreme Infrastructure Summary",
    discovery_function=discover_extreme_summary,
    check_function=check_extreme_summary,
    check_default_parameters={},
)
