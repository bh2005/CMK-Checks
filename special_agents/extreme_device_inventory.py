#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2
"""
Display hints for Extreme Cloud IQ Devices Inventory

Install to: local/share/check_mk/web/plugins/views/extreme_device_inventory.py
"""

from cmk.gui.i18n import _
from cmk.gui.inventory import displayhints

# Register display hints for the Devices table
displayhints.register({
    ".networking.extreme_devices:": {
        "title": _("Extreme Network Devices"),
        "icon": "network",
        "keyorder": [
            "hostname",
            "device_type",
            "model",
            "ip_address",
            "mac_address",
            "serial",
            "software_version",
            "location",
            "status",
            "source",
            "device_id",
        ],
    },
    ".networking.extreme_devices:*.device_id": {
        "title": _("Device ID"),
        "short": _("ID"),
    },
    ".networking.extreme_devices:*.hostname": {
        "title": _("Hostname"),
        "short": _("Hostname"),
    },
    ".networking.extreme_devices:*.serial": {
        "title": _("Serial Number"),
        "short": _("Serial"),
    },
    ".networking.extreme_devices:*.mac_address": {
        "title": _("MAC Address"),
        "short": _("MAC"),
    },
    ".networking.extreme_devices:*.ip_address": {
        "title": _("IP Address"),
        "short": _("IP"),
    },
    ".networking.extreme_devices:*.model": {
        "title": _("Model"),
        "short": _("Model"),
    },
    ".networking.extreme_devices:*.software_version": {
        "title": _("Software Version"),
        "short": _("SW Version"),
    },
    ".networking.extreme_devices:*.location": {
        "title": _("Location"),
        "short": _("Location"),
    },
    ".networking.extreme_devices:*.device_type": {
        "title": _("Device Type"),
        "short": _("Type"),
        "paint": "str",
    },
    ".networking.extreme_devices:*.status": {
        "title": _("Status"),
        "short": _("Status"),
        "paint": "str",
    },
    ".networking.extreme_devices:*.source": {
        "title": _("Source"),
        "short": _("Source"),
    },
})
