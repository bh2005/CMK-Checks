#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .agent_sections import register_check_plugin
from cmk.agent_based.v2 import (
    CheckResult,
    DiscoveryResult,
    Result,
    State,
    Service,
    Metric,
)

# --- Check 1: AP Status ---

def discover_extreme_ap_status(section):
    # Da jeder AP nur einen Status-Datensatz liefert, 
    # brauchen wir keine Parameter, sondern entdecken den Service einfach.
    yield DiscoveryResult()

def check_extreme_ap_status(section):
    # section ist eine Liste der Zeilen aus <<<extreme_ap_status>>>
    # Beispiel Zeile: PoCTest-460c-1|24602...|90B8...|10.187...|AP_460C|0|DISCONNECTED|N/A|N/A
    if not section:
        return

    row = section[0]
    hostname, sn, mac, ip, model, is_connected, conn_state, sw_ver, site = row

    # Status auswerten
    if is_connected == "1":
        yield Result(state=State.OK, summary=f"Status: {conn_state}")
    else:
        yield Result(state=State.CRIT, summary=f"Status: {conn_state}")

    yield Result(state=State.OK, summary=f"Modell: {model}")
    yield Result(state=State.OK, summary=f"S/N: {sn}")
    yield Result(state=State.OK, summary=f"IP: {ip}")

# --- Check 2: AP Clients ---

def discover_extreme_ap_clients(section):
    yield DiscoveryResult()

def check_extreme_ap_clients(section):
    # Beispiel Zeile: 5|2|3 (Total|2.4GHz|5GHz)
    if not section:
        return

    total_clients, c_24, c_5 = section[0]
    total = int(total_clients)

    yield Result(state=State.OK, summary=f"Clients gesamt: {total}")
    
    # Metrik für Graphen hinzufügen
    yield Metric("clients_total", total)
    
    if c_24 != "0" or c_5 != "0":
        yield Result(state=State.OK, summary=f"(2.4GHz: {c_24}, 5GHz: {c_5})")

# --- Registrierung ---

register_check_plugin(
    name="extreme_ap_status",
    service_name="AP Status",
    discovery_function=discover_extreme_ap_status,
    check_function=check_extreme_ap_status,
)

register_check_plugin(
    name="extreme_ap_clients",
    service_name="AP Clients",
    discovery_function=discover_extreme_ap_clients,
    check_function=check_extreme_ap_clients,
)