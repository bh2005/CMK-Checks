# -*- coding: utf-8 -*-
from cmk.gui.i18n import _
from cmk.gui.plugins.inventory import inventory_display_info

inventory_display_info.update({
    ("extreme_ap_radios",): {
        "title": _("Extreme AP Radios"),
        "view": "table",
        "icon": "wifi",
        "nesting": True,              # Unterknoten anzeigen
        "join_element": "radio_name", # Gruppierung nach Radio
        "columns": [
            ("radio_name", _("Radio Name")),
            ("radio_mac", _("Radio Mac")),
            ("frequency", _("Frequency")),
            ("channel_number", _("Channel Number")),
            ("channel_width", _("Channel Width")),
            ("mode", _("Mode")),
            ("power", _("Power")),
            ("device_id", _("Device Id")),
            ("hostname", _("Hostname")),
        ],
        "keyorder": ["radio_name", "radio_mac"],
    },
    ("extreme_ap_radios", "*"): {
        "title": _("BSSIDs"),
        "view": "table",
        "nesting": False,
        "columns": [
            ("ssid", _("SSID")),
            ("bssid", _("BSSID")),
            ("clients", _("Clients")),
            ("frequency", _("Frequency")),
            ("device_id", _("Device Id")),
            ("hostname", _("Hostname")),
        ],
        "keyorder": ["bssid", "ssid"],
    },
})
