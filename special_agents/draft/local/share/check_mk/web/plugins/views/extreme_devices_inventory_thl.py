
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Extreme Devices Inventory – THL-style (CMK 2.4)

from cmk.gui.i18n import _

# Versionstoleranter Import
try:
    from cmk.gui.plugins.inventory.displayhints import inventory_displayhints
except Exception:
    try:
        from cmk.gui.views.inventory.registry import inventory_displayhints
    except Exception:
        from cmk.gui.inventory import displayhints as inventory_displayhints

# WICHTIG: String-Pfad, keine Tuple!
BASE = "networking.extreme_devices"

DEFAULT_COLS = [
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
]

inventory_displayhints.update({
    # Tabelle
    BASE: {
        "title": _("Extreme Network Devices"),
        "icon": "network",
        "view": "table",
        "keyorder": DEFAULT_COLS,
    },

    # Spalten (dot-notation + wildcard für Listenelemente)
    f"{BASE}.*.hostname":          {"title": _("Hostname")},
    f"{BASE}.*.device_type":       {"title": _("Type")},
    f"{BASE}.*.model":             {"title": _("Model")},
    f"{BASE}.*.ip_address":        {"title": _("IP")},
    f"{BASE}.*.mac_address":       {"title": _("MAC")},
    f"{BASE}.*.serial":            {"title": _("Serial")},
    f"{BASE}.*.software_version":  {"title": _("SW Version")},
    f"{BASE}.*.location":          {"title": _("Location")},
    f"{BASE}.*.status":            {"title": _("Status")},
    f"{BASE}.*.source":            {"title": _("Source")},
    f"{BASE}.*.device_id":         {"title": _("Device ID")},
})
