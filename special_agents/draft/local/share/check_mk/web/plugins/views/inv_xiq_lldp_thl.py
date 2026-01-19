
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# XIQ LLDP/CDP Inventory – THL-style (CMK 2.4)

from cmk.gui.i18n import _

# Versionstoleranter Import (falls intern Pfade variieren)
try:
    from cmk.gui.plugins.inventory.displayhints import inventory_displayhints
except Exception:
    try:
        from cmk.gui.views.inventory.registry import inventory_displayhints
    except Exception:
        from cmk.gui.inventory import displayhints as inventory_displayhints

# Inventory-Basis-Pfad als STRING (wichtig! kein Tuple)
BASE = "networking.lldp_infos"

# Spaltenreihenfolge so wie zuletzt gewünscht/bestätigt
DEFAULT_COLS = [
    "hostaddress",
    "hostname",
    "id",
    "local_port",
    "mac_address",
    "management_ip",
    "port_description",
    "remote_device",
    "remote_port",
]

# Displayhints (Legacy-Format) mit dot-notierten Strings
inventory_displayhints.update({
    # Tabellen-Definition für die Liste
    BASE: {
        "title": _("LLDP/CDP Neighbors"),
        "icon": "network",
        "view": "table",
        "keyorder": DEFAULT_COLS,
    },

    # Spalten (jede Spalte refers to "<base>.*.<field>")
    f"{BASE}.*.hostaddress":      {"title": _("Hostaddress")},
    f"{BASE}.*.hostname":         {"title": _("Hostname")},
    f"{BASE}.*.id":               {"title": _("ID")},
    f"{BASE}.*.local_port":       {"title": _("Local Port")},
    f"{BASE}.*.mac_address":      {"title": _("MAC Address")},
    f"{BASE}.*.management_ip":    {"title": _("Mgmt IP")},
    f"{BASE}.*.port_description": {"title": _("Port Description")},
    f"{BASE}.*.remote_device":    {"title": _("Remote Device")},
    f"{BASE}.*.remote_port":      {"title": _("Remote Port")},
})
