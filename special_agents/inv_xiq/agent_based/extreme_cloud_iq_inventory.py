#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2
"""
Inventory plugin for Extreme Cloud IQ Access Points

This plugin creates an inventory table with all Access Points discovered
via the Extreme Cloud IQ special agent.

WICHTIG: Verwendet die bereits existierenden Sections aus xiq.agent_based.xiq
Registriert KEINE neuen Sections!

Install to: local/lib/python3/cmk_addons/plugins/inv_xiq/agent_based/extreme_cloud_iq_inventory.py
"""

from typing import Any
from collections.abc import Mapping

from cmk.agent_based.v2 import (
    InventoryPlugin,
    InventoryResult,
    TableRow,
)


def inventory_extreme_cloud_iq_aps(
    section_extreme_ap_status: Mapping[str, Any] | None,
    section_extreme_ap_clients: Mapping[str, Any] | None,
    section_extreme_ap_details: Mapping[str, Any] | None,
) -> InventoryResult:
    """
    Inventory function for Extreme Cloud IQ Access Points
    
    Creates a table row for each Access Point with all relevant information.
    Uses the existing sections that are already registered in the xiq plugin.
    """
    if not section_extreme_ap_status:
        return
    
    # Merge all available data
    ap_data = dict(section_extreme_ap_status)
    
    if section_extreme_ap_clients:
        ap_data.update(section_extreme_ap_clients)
    
    if section_extreme_ap_details:
        ap_data.update(section_extreme_ap_details)
    
    # Create inventory table row
    yield TableRow(
        path=["networking", "extreme_access_points"],
        key_columns={
            "serial": ap_data.get("serial", ""),
        },
        inventory_columns={
            "hostname": ap_data.get("hostname", ""),
            "mac_address": ap_data.get("mac", ""),
            "ip_address": ap_data.get("ip", ""),
            "model": ap_data.get("model", ""),
            "connection_state": ap_data.get("state", "UNKNOWN"),
            "software_version": ap_data.get("software", ""),
            "location": ap_data.get("location", ""),
            "device_id": ap_data.get("device_id", ""),
            "client_count": ap_data.get("client_count", 0),
            "clients_2ghz": ap_data.get("clients_2g", 0),
            "clients_5ghz": ap_data.get("clients_5g", 0),
            "cpu_usage": ap_data.get("cpu_usage", 0.0),
            "memory_usage": ap_data.get("memory_usage", 0.0),
            "uptime_seconds": ap_data.get("uptime", 0),
            "power_mode": ap_data.get("power_mode", ""),
            "poe_power_watts": ap_data.get("poe_power", 0.0),
        },
        status_columns={
            "connected": ap_data.get("connected", False),
        },
    )


# Register inventory plugin - verwendet die bereits existierenden Sections!
inventory_plugin_extreme_cloud_iq_aps = InventoryPlugin(
    name="extreme_cloud_iq_aps",
    sections=["extreme_ap_status", "extreme_ap_clients", "extreme_ap_details"],
    inventory_function=inventory_extreme_cloud_iq_aps,
)
