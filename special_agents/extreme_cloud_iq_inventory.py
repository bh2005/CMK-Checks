#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2
"""
Display hints for Extreme Cloud IQ Access Points Inventory

This defines how the inventory table is displayed in the Check_MK UI,
including column names, formats, filters, and sorting options.

Install to: local/share/check_mk/web/plugins/views/extreme_cloud_iq_inventory.py
"""

from cmk.gui.i18n import _
from cmk.gui.plugins.views.icons import icon_and_action_registry, Icon
from cmk.gui.type_defs import ColumnSpec, SorterSpec
from cmk.gui.inventory import displayhints

# Register display hints for the Access Points table
displayhints.register({
    ".networking.extreme_access_points:": {
        "title": _("Extreme Cloud IQ Access Points"),
        "icon": "network_wireless",
        "keyorder": [
            "hostname",
            "model",
            "connection_state",
            "ip_address",
            "mac_address",
            "serial",
            "location",
            "client_count",
            "software_version",
            "cpu_usage",
            "memory_usage",
            "uptime_seconds",
            "power_mode",
            "poe_power_watts",
            "device_id",
            "clients_2ghz",
            "clients_5ghz",
            "connected",
        ],
    },
    ".networking.extreme_access_points:*.hostname": {
        "title": _("AP Hostname"),
        "short": _("Hostname"),
    },
    ".networking.extreme_access_points:*.serial": {
        "title": _("Serial Number"),
        "short": _("Serial"),
    },
    ".networking.extreme_access_points:*.mac_address": {
        "title": _("MAC Address"),
        "short": _("MAC"),
    },
    ".networking.extreme_access_points:*.ip_address": {
        "title": _("IP Address"),
        "short": _("IP"),
    },
    ".networking.extreme_access_points:*.model": {
        "title": _("Model"),
        "short": _("Model"),
    },
    ".networking.extreme_access_points:*.connection_state": {
        "title": _("Connection State"),
        "short": _("State"),
        "paint": "str",
    },
    ".networking.extreme_access_points:*.connected": {
        "title": _("Connected"),
        "short": _("Conn"),
        "paint": "bool",
    },
    ".networking.extreme_access_points:*.software_version": {
        "title": _("Software Version"),
        "short": _("SW Version"),
    },
    ".networking.extreme_access_points:*.location": {
        "title": _("Location"),
        "short": _("Location"),
    },
    ".networking.extreme_access_points:*.device_id": {
        "title": _("Device ID"),
        "short": _("Device ID"),
    },
    ".networking.extreme_access_points:*.client_count": {
        "title": _("Total Clients"),
        "short": _("Clients"),
        "paint": "number",
    },
    ".networking.extreme_access_points:*.clients_2ghz": {
        "title": _("2.4 GHz Clients"),
        "short": _("2.4G"),
        "paint": "number",
    },
    ".networking.extreme_access_points:*.clients_5ghz": {
        "title": _("5 GHz Clients"),
        "short": _("5G"),
        "paint": "number",
    },
    ".networking.extreme_access_points:*.cpu_usage": {
        "title": _("CPU Usage (%)"),
        "short": _("CPU"),
        "paint": "number",
    },
    ".networking.extreme_access_points:*.memory_usage": {
        "title": _("Memory Usage (%)"),
        "short": _("Memory"),
        "paint": "number",
    },
    ".networking.extreme_access_points:*.uptime_seconds": {
        "title": _("Uptime (seconds)"),
        "short": _("Uptime"),
        "paint": "age",
    },
    ".networking.extreme_access_points:*.power_mode": {
        "title": _("Power Mode"),
        "short": _("Power"),
    },
    ".networking.extreme_access_points:*.poe_power_watts": {
        "title": _("PoE Power (Watts)"),
        "short": _("PoE (W)"),
        "paint": "number",
    },
})
