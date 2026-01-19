#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Extreme Switch Inventory – THL-style (CMK 2.4)

from cmk.gui.i18n import _

try:
    from cmk.gui.plugins.inventory.displayhints import inventory_displayhints
except Exception:
    try:
        from cmk.gui.views.inventory.registry import inventory_displayhints
    except Exception:
        from cmk.gui.inventory import displayhints as inventory_displayhints

BASE = "networking.extreme_sw"

DEFAULT_COLS = [
    "hostname",
    "device_function",
    "model",
    "ip",
    "mac",
    "serial",
    "software",
    "location_leaf",
    "managed_by",
    "id",
]

inventory_displayhints.update({
    BASE: {
        "title": _("Extreme Switches"),
        "icon": "network",
        "view": "table",
        "keyorder": DEFAULT_COLS,
    },

    f"{BASE}.*.hostname":        {"title": _("Hostname")},
    f"{BASE}.*.device_function": {"title": _("Type")},
    f"{BASE}.*.model":           {"title": _("Model")},
    f"{BASE}.*.ip":              {"title": _("IP")},
    f"{BASE}.*.mac":             {"title": _("MAC")},
    f"{BASE}.*.serial":          {"title": _("Serial")},
    f"{BASE}.*.software":        {"title": _("SW Version")},
    f"{BASE}.*.location_leaf":   {"title": _("Location")},
    f"{BASE}.*.managed_by":      {"title": _("Source")},
    f"{BASE}.*.id":              {"title": _("Device ID")},
})
