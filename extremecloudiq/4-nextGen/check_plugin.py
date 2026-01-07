#!/usr/bin/env python3
"""
Check_MK Check Plugins for ExtremeCloud IQ Access Points

Three check plugins:
1. extreme_ap_status - AP connection status and basic info
2. extreme_ap_clients - Client count monitoring
3. extreme_ap_details - CPU, Memory, Uptime monitoring
"""

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Service,
    Result,
    State,
    Metric,
    check_levels,
)
from typing import Any, Dict, Optional


# =============================================================================
# Plugin 1: AP Status
# =============================================================================

def parse_extreme_ap_status(string_table):
    """Parse extreme_ap_status section"""
    if not string_table:
        return None
    
    # Format: hostname|serial|mac|ip|model|status|connection_state|sw_version|site
    line = string_table[0]
    parts = line[0].split("|")
    
    if len(parts) < 9:
        return None
    
    return {
        "hostname": parts[0],
        "serial": parts[1],
        "mac": parts[2],
        "ip": parts[3],
        "model": parts[4],
        "status": parts[5],
        "connection_state": parts[6],
        "software_version": parts[7],
        "site": parts[8],
    }


def discover_extreme_ap_status(section):
    """Discover AP status check"""
    if section:
        yield Service()


def check_extreme_ap_status(params, section):
    """Check AP status"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    # Check connection status
    is_connected = section["status"] == "1"
    connection_state = section["connection_state"]
    
    if is_connected and connection_state == "CONNECTED":
        state = State.OK
        summary = f"AP is connected"
    elif connection_state == "DISCONNECTED":
        state = State.CRIT
        summary = f"AP is disconnected"
    else:
        state = State.WARN
        summary = f"AP state: {connection_state}"
    
    # Add details
    details = (
        f"\nModel: {section['model']}"
        f"\nSerial: {section['serial']}"
        f"\nMAC: {section['mac']}"
        f"\nIP: {section['ip']}"
        f"\nSoftware: {section['software_version']}"
        f"\nSite: {section['site']}"
    )
    
    yield Result(state=state, summary=summary, details=details)


register.agent_section(
    name="extreme_ap_status",
    parse_function=parse_extreme_ap_status,
)

register.check_plugin(
    name="extreme_ap_status",
    service_name="Extreme AP Status",
    discovery_function=discover_extreme_ap_status,
    check_function=check_extreme_ap_status,
    check_default_parameters={},
)


# =============================================================================
# Plugin 2: AP Clients
# =============================================================================

def parse_extreme_ap_clients(string_table):
    """Parse extreme_ap_clients section"""
    if not string_table:
        return None
    
    # Format: total_clients|radio_2.4ghz|radio_5ghz
    line = string_table[0]
    parts = line[0].split("|")
    
    if len(parts) < 3:
        return None
    
    return {
        "total": int(parts[0]),
        "radio_2_4": int(parts[1]),
        "radio_5": int(parts[2]),
    }


def discover_extreme_ap_clients(section):
    """Discover AP clients check"""
    if section is not None:
        yield Service()


def check_extreme_ap_clients(params, section):
    """Check AP client count"""
    if section is None:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    total = section["total"]
    radio_2_4 = section["radio_2_4"]
    radio_5 = section["radio_5"]
    
    # Check levels for total clients
    warn_level = params.get("clients_warn", 50)
    crit_level = params.get("clients_crit", 80)
    
    # Determine state based on client count
    if total >= crit_level:
        state = State.CRIT
    elif total >= warn_level:
        state = State.WARN
    else:
        state = State.OK
    
    summary = f"{total} clients (2.4GHz: {radio_2_4}, 5GHz: {radio_5})"
    
    yield Result(state=state, summary=summary)
    yield Metric("clients_total", total, levels=(warn_level, crit_level))
    yield Metric("clients_2_4ghz", radio_2_4)
    yield Metric("clients_5ghz", radio_5)


register.agent_section(
    name="extreme_ap_clients",
    parse_function=parse_extreme_ap_clients,
)

register.check_plugin(
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
# Plugin 3: AP Details (CPU, Memory, Uptime)
# =============================================================================

def parse_extreme_ap_details(string_table):
    """Parse extreme_ap_details section"""
    if not string_table:
        return None
    
    # Format: cpu_usage|memory_usage|uptime|power_mode|poe_power
    line = string_table[0]
    parts = line[0].split("|")
    
    if len(parts) < 5:
        return None
    
    return {
        "cpu_usage": float(parts[0]),
        "memory_usage": float(parts[1]),
        "uptime": int(parts[2]),
        "power_mode": parts[3],
        "poe_power": float(parts[4]),
    }


def discover_extreme_ap_details(section):
    """Discover AP details check"""
    if section is not None:
        yield Service()


def check_extreme_ap_details(params, section):
    """Check AP details (CPU, Memory, Uptime)"""
    if section is None:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    # CPU Check
    cpu = section["cpu_usage"]
    cpu_warn = params.get("cpu_warn", 80.0)
    cpu_crit = params.get("cpu_crit", 90.0)
    
    yield from check_levels(
        cpu,
        levels_upper=(cpu_warn, cpu_crit),
        metric_name="cpu_utilization",
        label="CPU",
        render_func=lambda v: f"{v:.1f}%",
    )
    
    # Memory Check
    memory = section["memory_usage"]
    mem_warn = params.get("memory_warn", 80.0)
    mem_crit = params.get("memory_crit", 90.0)
    
    yield from check_levels(
        memory,
        levels_upper=(mem_warn, mem_crit),
        metric_name="memory_utilization",
        label="Memory",
        render_func=lambda v: f"{v:.1f}%",
    )
    
    # Uptime
    uptime = section["uptime"]
    uptime_days = uptime / 86400  # Convert seconds to days
    
    yield Result(
        state=State.OK,
        summary=f"Uptime: {uptime_days:.1f} days"
    )
    yield Metric("uptime", uptime)
    
    # Power Info
    power_mode = section["power_mode"]
    poe_power = section["poe_power"]
    
    yield Result(
        state=State.OK,
        notice=f"Power Mode: {power_mode}, PoE: {poe_power}W"
    )
    yield Metric("poe_power", poe_power)


register.agent_section(
    name="extreme_ap_details",
    parse_function=parse_extreme_ap_details,
)

register.check_plugin(
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
# Plugin 4: Summary (Main Host)
# =============================================================================

def parse_extreme_summary(string_table):
    """Parse extreme_summary section"""
    if not string_table:
        return None
    
    # Format: access_points=X|total_clients=Y
    line = string_table[0][0]
    parts = {}
    
    for item in line.split("|"):
        if "=" in item:
            key, value = item.split("=")
            parts[key] = int(value)
    
    return parts


def discover_extreme_summary(section):
    """Discover summary check"""
    if section:
        yield Service()


def check_extreme_summary(params, section):
    """Check overall Extreme infrastructure summary"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return
    
    aps = section.get("access_points", 0)
    clients = section.get("total_clients", 0)
    
    summary = f"{aps} Access Points, {clients} total clients"
    
    yield Result(state=State.OK, summary=summary)
    yield Metric("access_points", aps)
    yield Metric("total_clients", clients)


register.agent_section(
    name="extreme_summary",
    parse_function=parse_extreme_summary,
)

register.check_plugin(
    name="extreme_summary",
    service_name="Extreme Infrastructure Summary",
    discovery_function=discover_extreme_summary,
    check_function=check_extreme_summary,
    check_default_parameters={},
)