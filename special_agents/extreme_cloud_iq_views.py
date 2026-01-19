#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2025 Your Company
# License: GNU General Public License v2
"""
Custom View for Extreme Cloud IQ Access Points with filtering and sorting

Install to: local/share/check_mk/web/plugins/views/extreme_cloud_iq_views.py
"""

from cmk.gui.i18n import _
from cmk.gui.plugins.views.utils import (
    multisite_builtin_views,
)

# Define the custom view for Extreme Access Points
multisite_builtin_views.update({
    "extreme_aps_all": {
        "title": _("Extreme Cloud IQ - All Access Points"),
        "description": _("List of all Extreme Cloud IQ Access Points with filtering and sorting"),
        "topic": "inventory",
        "datasource": "invhist",
        "browser_reload": 30,
        "layout": "table",
        "num_columns": 1,
        "column_headers": "pergroup",
        "public": True,
        "single_infos": [],
        "context": {
            "invhist_tree": {"tree": ["networking", "extreme_access_points"]},
        },
        "hidden": False,
        "hidebutton": False,
        "icon": None,
        "linktitle": _("Extreme Access Points"),
        "mobile": False,
        "mustsearch": False,
        "name": "extreme_aps_all",
        "owner": "",
        "painters": [
            ("invhist_host", None),
            ("invhist_networking_extreme_access_points_hostname", None),
            ("invhist_networking_extreme_access_points_model", None),
            ("invhist_networking_extreme_access_points_connection_state", None),
            ("invhist_networking_extreme_access_points_ip_address", None),
            ("invhist_networking_extreme_access_points_mac_address", None),
            ("invhist_networking_extreme_access_points_serial", None),
            ("invhist_networking_extreme_access_points_location", None),
            ("invhist_networking_extreme_access_points_client_count", None),
            ("invhist_networking_extreme_access_points_clients_2ghz", None),
            ("invhist_networking_extreme_access_points_clients_5ghz", None),
            ("invhist_networking_extreme_access_points_software_version", None),
            ("invhist_networking_extreme_access_points_cpu_usage", None),
            ("invhist_networking_extreme_access_points_memory_usage", None),
            ("invhist_networking_extreme_access_points_uptime_seconds", None),
            ("invhist_networking_extreme_access_points_power_mode", None),
            ("invhist_networking_extreme_access_points_poe_power_watts", None),
        ],
        "play_sounds": False,
        "show_checkboxes": False,
        "sorters": [
            ("invhist_host", False),
            ("invhist_networking_extreme_access_points_hostname", False),
        ],
        "user_sortable": True,
    },
    
    "extreme_aps_connected": {
        "title": _("Extreme Cloud IQ - Connected Access Points"),
        "description": _("List of connected Extreme Cloud IQ Access Points"),
        "topic": "inventory",
        "datasource": "invhist",
        "browser_reload": 30,
        "layout": "table",
        "num_columns": 1,
        "column_headers": "pergroup",
        "public": True,
        "single_infos": [],
        "context": {
            "invhist_tree": {"tree": ["networking", "extreme_access_points"]},
            "invhist_networking_extreme_access_points_connection_state": {
                "invhist_networking_extreme_access_points_connection_state": "CONNECTED"
            },
        },
        "hidden": False,
        "hidebutton": False,
        "icon": None,
        "linktitle": _("Connected APs"),
        "mobile": False,
        "mustsearch": False,
        "name": "extreme_aps_connected",
        "owner": "",
        "painters": [
            ("invhist_host", None),
            ("invhist_networking_extreme_access_points_hostname", None),
            ("invhist_networking_extreme_access_points_model", None),
            ("invhist_networking_extreme_access_points_ip_address", None),
            ("invhist_networking_extreme_access_points_location", None),
            ("invhist_networking_extreme_access_points_client_count", None),
            ("invhist_networking_extreme_access_points_clients_2ghz", None),
            ("invhist_networking_extreme_access_points_clients_5ghz", None),
        ],
        "play_sounds": False,
        "show_checkboxes": False,
        "sorters": [
            ("invhist_networking_extreme_access_points_client_count", True),
        ],
        "user_sortable": True,
    },
    
    "extreme_aps_with_clients": {
        "title": _("Extreme Cloud IQ - Access Points with Clients"),
        "description": _("Access Points that have active clients"),
        "topic": "inventory",
        "datasource": "invhist",
        "browser_reload": 30,
        "layout": "table",
        "num_columns": 1,
        "column_headers": "pergroup",
        "public": True,
        "single_infos": [],
        "context": {
            "invhist_tree": {"tree": ["networking", "extreme_access_points"]},
        },
        "hidden": False,
        "hidebutton": False,
        "icon": None,
        "linktitle": _("APs with Clients"),
        "mobile": False,
        "mustsearch": False,
        "name": "extreme_aps_with_clients",
        "owner": "",
        "painters": [
            ("invhist_host", None),
            ("invhist_networking_extreme_access_points_hostname", None),
            ("invhist_networking_extreme_access_points_location", None),
            ("invhist_networking_extreme_access_points_client_count", None),
            ("invhist_networking_extreme_access_points_clients_2ghz", None),
            ("invhist_networking_extreme_access_points_clients_5ghz", None),
            ("invhist_networking_extreme_access_points_cpu_usage", None),
            ("invhist_networking_extreme_access_points_memory_usage", None),
        ],
        "play_sounds": False,
        "show_checkboxes": False,
        "sorters": [
            ("invhist_networking_extreme_access_points_client_count", True),
        ],
        "user_sortable": True,
    },
})
