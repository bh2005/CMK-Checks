#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2
"""
Inventory plugin for Extreme Cloud IQ Devices

This plugin creates an inventory table with all devices discovered
via the Extreme Cloud IQ special agent.

Verarbeitet die Section: extreme_device_inventory

Format: device_id|hostname|serial|mac|ip|model|software|location|status|source
Example: 917843101189834|XiQ-SE|XIQSE-DD5399B3EBDA44D09BA858801BE33819|00:50:56:97:97:A4|10.124.34.240|XIQ_SE|25.11.11.10||UNKNOWN|XIQ

Install to: local/lib/python3/cmk_addons/plugins/inv_xiq/agent_based/extreme_device_inventory.py
"""

from typing import Any
from collections.abc import Mapping

from cmk.agent_based.v2 import (
    InventoryPlugin,
    InventoryResult,
    TableRow,
)

# WICHTIG: Keine Section-Registrierung!
# Die Section "extreme_device_inventory" ist bereits in xiq.agent_based.xiq registriert
# als "agent_section_xiq_device_inventory"


def inventory_extreme_devices(
    section: dict[str, Mapping[str, Any]] | None,
) -> InventoryResult:
    """
    Inventory function for Extreme Cloud IQ Devices
    
    Creates a table row for each device with all relevant information
    """
    if not section:
        return
    
    for device_id, device_data in section.items():
        # Create inventory table row
        yield TableRow(
            path=["networking", "extreme_devices"],
            key_columns={
                "device_id": device_data.get("device_id", ""),
            },
            inventory_columns={
                "hostname": device_data.get("hostname", ""),
                "serial": device_data.get("serial", ""),
                "mac_address": device_data.get("mac_address", ""),
                "ip_address": device_data.get("ip_address", ""),
                "model": device_data.get("model", ""),
                "software_version": device_data.get("software_version", ""),
                "location": device_data.get("location", ""),
                "device_type": device_data.get("device_type", "UNKNOWN"),
                "source": device_data.get("source", ""),
            },
            status_columns={
                "status": device_data.get("status", "UNKNOWN"),
            },
        )


# Register inventory plugin - verwendet die bereits existierende Section!
inventory_plugin_extreme_devices = InventoryPlugin(
    name="extreme_devices",
    sections=["extreme_device_inventory"],  # Verwendet die existierende Section
    inventory_function=inventory_extreme_devices,
)
