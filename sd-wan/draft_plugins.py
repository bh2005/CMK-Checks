#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SD-WAN Monitoring - Praktische Implementierung
# ==============================================
# Beispiel-Checks für verschiedene SD-WAN Vendors
# ==============================================

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
    exists,
    render,
)

# ============================================================================
# 1. SD-WAN LINK STATUS & PERFORMANCE
# ============================================================================

def parse_sdwan_links(string_table: StringTable) -> Mapping[str, Mapping[str, str]]:
    """
    Parse SD-WAN link information.
    
    Supports generic format from various vendors:
    - Cisco SD-WAN (Viptela)
    - Fortinet SD-WAN
    - VMware VeloCloud
    - Versa Networks
    - Silver Peak
    """
    links = {}
    for idx, row in enumerate(string_table, start=1):
        if len(row) < 7:
            continue
        
        links[str(idx)] = {
            "name": row[0],           # Link Name (e.g., "MPLS", "Internet1")
            "type": row[1],           # Link Type (MPLS/Internet/LTE/5G)
            "state": row[2],          # State (up/down/degraded)
            "latency": row[3],        # Latency in ms
            "jitter": row[4],         # Jitter in ms
            "packet_loss": row[5],    # Packet loss in %
            "bandwidth_util": row[6], # Bandwidth utilization in %
        }
    
    return links


snmp_section_sdwan_links = SimpleSNMPSection(
    name="sdwan_links",
    parse_function=parse_sdwan_links,
    detect=exists(".1.3.6.1.4.1.99999.1.1"),  # Vendor-specific OID
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.99999.2.1",
        oids=[
            "2",  # Link Name
            "3",  # Link Type
            "4",  # Link State
            "5",  # Latency
            "6",  # Jitter
            "7",  # Packet Loss
            "8",  # Bandwidth Utilization
        ],
    ),
)


def discover_sdwan_links(section_sdwan_links: Mapping[str, Mapping[str, str]] | None) -> DiscoveryResult:
    """Discover all SD-WAN links."""
    if not section_sdwan_links:
        return
    
    for item_id, link in section_sdwan_links.items():
        yield Service(item=f"{link['name']} ({link['type']})")


def check_sdwan_links(
    item: str,
    params: Mapping[str, Any],
    section_sdwan_links: Mapping[str, Mapping[str, str]] | None,
) -> CheckResult:
    """
    Check SD-WAN link health with performance metrics.
    
    Monitors:
    - Link state (up/down/degraded)
    - Latency with thresholds
    - Jitter with thresholds
    - Packet loss with thresholds
    - Bandwidth utilization
    """
    if not section_sdwan_links:
        return
    
    # Find matching link
    link = None
    for l in section_sdwan_links.values():
        if f"{l['name']} ({l['type']})" == item:
            link = l
            break
    
    if not link:
        return
    
    # Check link state
    state = State.OK
    if link["state"].lower() == "down":
        state = State.CRIT
    elif link["state"].lower() == "degraded":
        state = State.WARN
    
    yield Result(
        state=state,
        summary=f"{link['type']}: {link['state'].upper()}",
    )
    
    # Parse numeric values
    try:
        latency = float(link["latency"])
        jitter = float(link["jitter"])
        packet_loss = float(link["packet_loss"])
        bandwidth_util = float(link["bandwidth_util"])
    except (ValueError, TypeError):
        yield Result(state=State.UNKNOWN, summary="Invalid metrics")
        return
    
    # Latency check
    latency_warn, latency_crit = params.get("latency_levels", (100, 200))
    latency_state = State.OK
    if latency >= latency_crit:
        latency_state = State.CRIT
    elif latency >= latency_warn:
        latency_state = State.WARN
    
    yield Result(
        state=latency_state,
        summary=f"Latency: {latency:.1f}ms",
    )
    yield Metric("latency", latency, levels=(latency_warn, latency_crit))
    
    # Jitter check
    jitter_warn, jitter_crit = params.get("jitter_levels", (20, 50))
    jitter_state = State.OK
    if jitter >= jitter_crit:
        jitter_state = State.CRIT
    elif jitter >= jitter_warn:
        jitter_state = State.WARN
    
    yield Result(
        state=jitter_state,
        summary=f"Jitter: {jitter:.1f}ms",
    )
    yield Metric("jitter", jitter, levels=(jitter_warn, jitter_crit))
    
    # Packet Loss check
    loss_warn, loss_crit = params.get("packet_loss_levels", (1.0, 3.0))
    loss_state = State.OK
    if packet_loss >= loss_crit:
        loss_state = State.CRIT
    elif packet_loss >= loss_warn:
        loss_state = State.WARN
    
    yield Result(
        state=loss_state,
        summary=f"Packet Loss: {packet_loss:.2f}%",
    )
    yield Metric("packet_loss", packet_loss, levels=(loss_warn, loss_crit))
    
    # Bandwidth Utilization
    bw_warn, bw_crit = params.get("bandwidth_levels", (70, 85))
    bw_state = State.OK
    if bandwidth_util >= bw_crit:
        bw_state = State.CRIT
    elif bandwidth_util >= bw_warn:
        bw_state = State.WARN
    
    yield Result(
        state=bw_state,
        summary=f"Bandwidth: {bandwidth_util:.1f}%",
    )
    yield Metric("bandwidth_util", bandwidth_util, levels=(bw_warn, bw_crit), boundaries=(0, 100))


check_plugin_sdwan_links = CheckPlugin(
    name="sdwan_links",
    service_name="SD-WAN Link %s",
    discovery_function=discover_sdwan_links,
    check_function=check_sdwan_links,
    check_ruleset_name="sdwan_links",
    check_default_parameters={
        "latency_levels": (100, 200),      # WARN/CRIT in ms
        "jitter_levels": (20, 50),         # WARN/CRIT in ms
        "packet_loss_levels": (1.0, 3.0),  # WARN/CRIT in %
        "bandwidth_levels": (70, 85),      # WARN/CRIT in %
    },
)


# ============================================================================
# 2. SD-WAN TUNNEL STATUS
# ============================================================================

def parse_sdwan_tunnels(string_table: StringTable) -> Mapping[str, Mapping[str, str]]:
    """Parse SD-WAN tunnel status."""
    tunnels = {}
    for idx, row in enumerate(string_table, start=1):
        if len(row) < 6:
            continue
        
        tunnels[str(idx)] = {
            "name": row[0],           # Tunnel name
            "remote": row[1],         # Remote endpoint
            "state": row[2],          # up/down/degraded
            "link": row[3],           # Underlay link (MPLS/Internet)
            "traffic": row[4],        # Current traffic (Mbit/s)
            "encryption": row[5],     # Encryption status (active/inactive)
        }
    
    return tunnels


snmp_section_sdwan_tunnels = SimpleSNMPSection(
    name="sdwan_tunnels",
    parse_function=parse_sdwan_tunnels,
    detect=exists(".1.3.6.1.4.1.99999.3.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.99999.3.1",
        oids=["2", "3", "4", "5", "6", "7"],
    ),
)


def discover_sdwan_tunnels(section_sdwan_tunnels: Mapping[str, Mapping[str, str]] | None) -> DiscoveryResult:
    """Discover all SD-WAN tunnels."""
    if not section_sdwan_tunnels:
        return
    
    for tunnel in section_sdwan_tunnels.values():
        yield Service(item=f"{tunnel['name']} ({tunnel['link']})")


def check_sdwan_tunnels(
    item: str,
    section_sdwan_tunnels: Mapping[str, Mapping[str, str]] | None,
) -> CheckResult:
    """Check SD-WAN tunnel status."""
    if not section_sdwan_tunnels:
        return
    
    # Find matching tunnel
    tunnel = None
    for t in section_sdwan_tunnels.values():
        if f"{t['name']} ({t['link']})" == item:
            tunnel = t
            break
    
    if not tunnel:
        return
    
    # Check tunnel state
    state = State.OK
    if tunnel["state"].lower() == "down":
        state = State.CRIT
    elif tunnel["state"].lower() == "degraded":
        state = State.WARN
    
    yield Result(
        state=state,
        summary=f"Tunnel to {tunnel['remote']}: {tunnel['state'].upper()}",
    )
    
    # Check encryption
    if tunnel["encryption"].lower() != "active":
        yield Result(
            state=State.WARN,
            summary=f"Encryption: {tunnel['encryption']} (should be active)",
        )
    else:
        yield Result(state=State.OK, notice="Encryption: Active")
    
    # Traffic metric
    try:
        traffic = float(tunnel["traffic"])
        yield Metric("traffic", traffic)
        yield Result(
            state=State.OK,
            summary=f"Traffic: {traffic:.1f} Mbit/s",
        )
    except (ValueError, TypeError):
        pass


check_plugin_sdwan_tunnels = CheckPlugin(
    name="sdwan_tunnels",
    service_name="SD-WAN Tunnel %s",
    discovery_function=discover_sdwan_tunnels,
    check_function=check_sdwan_tunnels,
)


# ============================================================================
# 3. SD-WAN PATH SELECTION & FAILOVER
# ============================================================================

def parse_sdwan_path_selection(string_table: StringTable) -> Mapping[str, str]:
    """Parse active path selection status."""
    if not string_table or len(string_table[0]) < 5:
        return {}
    
    row = string_table[0]
    return {
        "active_path": row[0],           # Current active path
        "path_priority": row[1],         # primary/secondary/tertiary
        "traffic_split": row[2],         # Traffic split % between paths
        "last_failover": row[3],         # Timestamp of last failover
        "failover_count_24h": row[4],    # Number of failovers in last 24h
    }


snmp_section_sdwan_path_selection = SimpleSNMPSection(
    name="sdwan_path_selection",
    parse_function=parse_sdwan_path_selection,
    detect=exists(".1.3.6.1.4.1.99999.4.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.99999.4.1",
        oids=["1.0", "2.0", "3.0", "4.0", "5.0"],
    ),
)


def discover_sdwan_path_selection(section_sdwan_path_selection: Mapping[str, str] | None) -> DiscoveryResult:
    """Discover SD-WAN path selection monitoring."""
    if section_sdwan_path_selection:
        yield Service()


def check_sdwan_path_selection(
    params: Mapping[str, Any],
    section_sdwan_path_selection: Mapping[str, str] | None,
) -> CheckResult:
    """
    Check SD-WAN path selection and failover status.
    
    Monitors:
    - Active path
    - Failover events
    - Path priority compliance
    """
    if not section_sdwan_path_selection:
        return
    
    ps = section_sdwan_path_selection
    
    # Check active path
    active_path = ps.get("active_path", "Unknown")
    priority = ps.get("path_priority", "unknown")
    
    # Determine state based on priority
    state = State.OK
    if priority.lower() == "secondary":
        state = State.WARN
        summary = f"Active Path: {active_path} (BACKUP - Primary down?)"
    elif priority.lower() == "tertiary":
        state = State.CRIT
        summary = f"Active Path: {active_path} (TERTIARY - Multiple links down!)"
    else:
        summary = f"Active Path: {active_path} (Primary)"
    
    yield Result(state=state, summary=summary)
    
    # Traffic split
    traffic_split = ps.get("traffic_split", "")
    if traffic_split:
        yield Result(state=State.OK, notice=f"Traffic Split: {traffic_split}")
    
    # Failover monitoring
    try:
        failover_count = int(ps.get("failover_count_24h", "0"))
        failover_warn, failover_crit = params.get("failover_count_levels", (3, 5))
        
        failover_state = State.OK
        if failover_count >= failover_crit:
            failover_state = State.CRIT
        elif failover_count >= failover_warn:
            failover_state = State.WARN
        
        yield Result(
            state=failover_state,
            summary=f"Failovers (24h): {failover_count}",
        )
        yield Metric("failover_count", failover_count, levels=(failover_warn, failover_crit))
        
    except (ValueError, TypeError):
        pass
    
    # Last failover time
    last_failover = ps.get("last_failover", "Never")
    if last_failover != "Never":
        yield Result(state=State.OK, notice=f"Last Failover: {last_failover}")


check_plugin_sdwan_path_selection = CheckPlugin(
    name="sdwan_path_selection",
    service_name="SD-WAN Path Selection",
    discovery_function=discover_sdwan_path_selection,
    check_function=check_sdwan_path_selection,
    check_ruleset_name="sdwan_path_selection",
    check_default_parameters={
        "failover_count_levels": (3, 5),  # WARN/CRIT number of failovers in 24h
    },
)


# ============================================================================
# 4. SD-WAN SLA COMPLIANCE
# ============================================================================

def parse_sdwan_sla(string_table: StringTable) -> Mapping[str, Mapping[str, str]]:
    """Parse SLA compliance status per application."""
    slas = {}
    for idx, row in enumerate(string_table, start=1):
        if len(row) < 6:
            continue
        
        slas[str(idx)] = {
            "app_name": row[0],           # Application (VoIP, Video, etc.)
            "current_path": row[1],       # Current path
            "avg_latency": row[2],        # Average latency
            "avg_jitter": row[3],         # Average jitter
            "avg_loss": row[4],           # Average packet loss
            "sla_status": row[5],         # compliant/degraded/violated
        }
    
    return slas


snmp_section_sdwan_sla = SimpleSNMPSection(
    name="sdwan_sla",
    parse_function=parse_sdwan_sla,
    detect=exists(".1.3.6.1.4.1.99999.5.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.99999.5.1",
        oids=["2", "3", "4", "5", "6", "7"],
    ),
)


def discover_sdwan_sla(section_sdwan_sla: Mapping[str, Mapping[str, str]] | None) -> DiscoveryResult:
    """Discover SLA monitoring for each application."""
    if not section_sdwan_sla:
        return
    
    for sla in section_sdwan_sla.values():
        yield Service(item=sla["app_name"])


def check_sdwan_sla(
    item: str,
    params: Mapping[str, Any],
    section_sdwan_sla: Mapping[str, Mapping[str, str]] | None,
) -> CheckResult:
    """Check SD-WAN SLA compliance per application."""
    if not section_sdwan_sla:
        return
    
    # Find matching SLA
    sla = None
    for s in section_sdwan_sla.values():
        if s["app_name"] == item:
            sla = s
            break
    
    if not sla:
        return
    
    # Check SLA status
    sla_status = sla["sla_status"].lower()
    state = State.OK
    if sla_status == "violated":
        state = State.CRIT
    elif sla_status == "degraded":
        state = State.WARN
    
    yield Result(
        state=state,
        summary=f"SLA: {sla_status.upper()} on {sla['current_path']}",
    )
    
    # Parse metrics
    try:
        latency = float(sla["avg_latency"])
        jitter = float(sla["avg_jitter"])
        loss = float(sla["avg_loss"])
        
        yield Result(
            state=State.OK,
            summary=f"Latency: {latency:.1f}ms, Jitter: {jitter:.1f}ms, Loss: {loss:.2f}%",
        )
        
        yield Metric("sla_latency", latency)
        yield Metric("sla_jitter", jitter)
        yield Metric("sla_packet_loss", loss)
        
    except (ValueError, TypeError):
        pass


check_plugin_sdwan_sla = CheckPlugin(
    name="sdwan_sla",
    service_name="SD-WAN SLA: %s",
    discovery_function=discover_sdwan_sla,
    check_function=check_sdwan_sla,
)


# ============================================================================
# 5. SD-WAN CONTROLLER STATUS
# ============================================================================

def parse_sdwan_controller(string_table: StringTable) -> Mapping[str, str]:
    """Parse SD-WAN controller status."""
    if not string_table or len(string_table[0]) < 5:
        return {}
    
    row = string_table[0]
    return {
        "controller_state": row[0],       # reachable/unreachable
        "api_latency": row[1],            # API response time
        "registered_edges": row[2],       # Number of registered edges
        "policy_push_success": row[3],    # Success rate of policy updates
        "cert_expiry_days": row[4],       # Certificate expiry in days
    }


snmp_section_sdwan_controller = SimpleSNMPSection(
    name="sdwan_controller",
    parse_function=parse_sdwan_controller,
    detect=exists(".1.3.6.1.4.1.99999.6.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.99999.6.1",
        oids=["1.0", "2.0", "3.0", "4.0", "5.0"],
    ),
)


def discover_sdwan_controller(section_sdwan_controller: Mapping[str, str] | None) -> DiscoveryResult:
    """Discover SD-WAN controller monitoring."""
    if section_sdwan_controller:
        yield Service()


def check_sdwan_controller(
    params: Mapping[str, Any],
    section_sdwan_controller: Mapping[str, str] | None,
) -> CheckResult:
    """Check SD-WAN controller health."""
    if not section_sdwan_controller:
        return
    
    ctrl = section_sdwan_controller
    
    # Controller reachability
    if ctrl["controller_state"].lower() != "reachable":
        yield Result(state=State.CRIT, summary="Controller: UNREACHABLE")
        return
    else:
        yield Result(state=State.OK, summary="Controller: Reachable")
    
    # API Latency
    try:
        api_latency = float(ctrl["api_latency"])
        api_warn, api_crit = params.get("api_latency_levels", (1000, 2000))
        
        api_state = State.OK
        if api_latency >= api_crit:
            api_state = State.CRIT
        elif api_latency >= api_warn:
            api_state = State.WARN
        
        yield Result(
            state=api_state,
            summary=f"API Latency: {api_latency:.0f}ms",
        )
        yield Metric("api_latency", api_latency, levels=(api_warn, api_crit))
    except (ValueError, TypeError):
        pass
    
    # Registered edges
    try:
        registered = int(ctrl["registered_edges"])
        yield Metric("registered_edges", registered)
        yield Result(state=State.OK, notice=f"Registered Edges: {registered}")
    except (ValueError, TypeError):
        pass
    
    # Policy push success
    try:
        success_rate = float(ctrl["policy_push_success"])
        if success_rate < 100:
            yield Result(
                state=State.WARN,
                summary=f"Policy Push Success: {success_rate:.1f}% (some edges failed)",
            )
        else:
            yield Result(state=State.OK, notice="Policy Push: 100% success")
        yield Metric("policy_push_success", success_rate, boundaries=(0, 100))
    except (ValueError, TypeError):
        pass
    
    # Certificate expiry
    try:
        cert_days = int(ctrl["cert_expiry_days"])
        cert_warn, cert_crit = params.get("cert_expiry_levels", (30, 7))
        
        cert_state = State.OK
        if cert_days <= cert_crit:
            cert_state = State.CRIT
        elif cert_days <= cert_warn:
            cert_state = State.WARN
        
        yield Result(
            state=cert_state,
            summary=f"Certificate Expiry: {cert_days} days",
        )
    except (ValueError, TypeError):
        pass


check_plugin_sdwan_controller = CheckPlugin(
    name="sdwan_controller",
    service_name="SD-WAN Controller",
    discovery_function=discover_sdwan_controller,
    check_function=check_sdwan_controller,
    check_ruleset_name="sdwan_controller",
    check_default_parameters={
        "api_latency_levels": (1000, 2000),  # WARN/CRIT in ms
        "cert_expiry_levels": (30, 7),       # WARN/CRIT in days
    },
)


# ============================================================================
# INSTALLATION NOTES
# ============================================================================
"""
Installation:
1. Copy to: ~/local/lib/python3/cmk_addons/plugins/sdwan/agent_based/sdwan.py

2. Adapt OIDs for your vendor:
   - Cisco SD-WAN (Viptela): .1.3.6.1.4.1.41916.*
   - Fortinet SD-WAN: .1.3.6.1.4.1.12356.*
   - VMware VeloCloud: .1.3.6.1.4.1.45346.*
   - Versa Networks: .1.3.6.1.4.1.42359.*

3. Configure thresholds in WATO:
   Setup → Monitoring Rules → SD-WAN Link Performance

4. Run discovery:
   cmk -II <hostname>

Services discovered:
- SD-WAN Link MPLS (Primary)
- SD-WAN Link Internet (Backup)
- SD-WAN Tunnel HQ (MPLS)
- SD-WAN Path Selection
- SD-WAN SLA: VoIP
- SD-WAN Controller
"""