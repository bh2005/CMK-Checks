#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2
"""
Painters and Sorters for Extreme Cloud IQ Access Points inventory

This defines how columns can be displayed, sorted, and filtered in views.

Install to: local/share/check_mk/web/plugins/views/extreme_cloud_iq_painters.py
"""

from cmk.gui.i18n import _
from cmk.gui.plugins.views.utils import (
    register_painter,
    register_sorter,
)
from cmk.gui.plugins.views.painters.v0.base import Painter
from cmk.gui.plugins.views.sorters import Sorter, declare_simple_sorter


# Helper function to create painters for inventory attributes
def register_inventory_painter(
    name: str,
    title: str,
    short: str,
    paint_function="str",
    sortable=True,
):
    """Register a painter for an inventory attribute"""
    
    painter_spec = {
        "title": _(title),
        "short": _(short),
        "columns": ["invhist_" + name],
        "options": [],
        "printable": True,
    }
    
    # Create paint function
    def paint(row, cell):
        value = row.get("invhist_" + name, "")
        if paint_function == "number":
            return "", str(value) if value else "0"
        elif paint_function == "bool":
            return "", "✓" if value else "✗"
        elif paint_function == "age":
            if value:
                hours = int(value) // 3600
                minutes = (int(value) % 3600) // 60
                return "", f"{hours}h {minutes}m"
            return "", "0h 0m"
        else:
            return "", str(value) if value else ""
    
    painter_spec["paint"] = paint
    
    # Register the painter
    register_painter(
        "invhist_" + name,
        painter_spec,
    )
    
    # Register sorter if needed
    if sortable:
        declare_simple_sorter(
            "invhist_" + name,
            _(title),
            "invhist_" + name,
            lambda row: row.get("invhist_" + name, ""),
        )


# Register all painters and sorters for Extreme AP inventory
register_inventory_painter(
    "networking_extreme_access_points_hostname",
    "AP Hostname",
    "Hostname",
)

register_inventory_painter(
    "networking_extreme_access_points_serial",
    "Serial Number",
    "Serial",
)

register_inventory_painter(
    "networking_extreme_access_points_mac_address",
    "MAC Address",
    "MAC",
)

register_inventory_painter(
    "networking_extreme_access_points_ip_address",
    "IP Address",
    "IP",
)

register_inventory_painter(
    "networking_extreme_access_points_model",
    "Model",
    "Model",
)

register_inventory_painter(
    "networking_extreme_access_points_connection_state",
    "Connection State",
    "State",
)

register_inventory_painter(
    "networking_extreme_access_points_connected",
    "Connected",
    "Conn",
    paint_function="bool",
)

register_inventory_painter(
    "networking_extreme_access_points_software_version",
    "Software Version",
    "SW Ver",
)

register_inventory_painter(
    "networking_extreme_access_points_location",
    "Location",
    "Location",
)

register_inventory_painter(
    "networking_extreme_access_points_device_id",
    "Device ID",
    "Dev ID",
)

register_inventory_painter(
    "networking_extreme_access_points_client_count",
    "Total Clients",
    "Clients",
    paint_function="number",
)

register_inventory_painter(
    "networking_extreme_access_points_clients_2ghz",
    "2.4 GHz Clients",
    "2.4G",
    paint_function="number",
)

register_inventory_painter(
    "networking_extreme_access_points_clients_5ghz",
    "5 GHz Clients",
    "5G",
    paint_function="number",
)

register_inventory_painter(
    "networking_extreme_access_points_cpu_usage",
    "CPU Usage (%)",
    "CPU",
    paint_function="number",
)

register_inventory_painter(
    "networking_extreme_access_points_memory_usage",
    "Memory Usage (%)",
    "Memory",
    paint_function="number",
)

register_inventory_painter(
    "networking_extreme_access_points_uptime_seconds",
    "Uptime",
    "Uptime",
    paint_function="age",
)

register_inventory_painter(
    "networking_extreme_access_points_power_mode",
    "Power Mode",
    "Power",
)

register_inventory_painter(
    "networking_extreme_access_points_poe_power_watts",
    "PoE Power (W)",
    "PoE",
    paint_function="number",
)
