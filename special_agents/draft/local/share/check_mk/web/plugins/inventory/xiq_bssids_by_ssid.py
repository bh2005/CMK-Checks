# -*- coding: utf-8 -*-
from cmk.gui.i18n import _
from cmk.gui.plugins.inventory import inventory_display_info

inventory_display_info.update({

    # Top-Level: SSIDs
    ("extreme_ap_bssids",): {
        "title": _("Extreme AP BSSIDs (by SSID)"),
        "icon": "wifi",
        "view": "table",
        "nesting": True,
        "join_element": "ssid",
        "columns": [
            ("ssid", _("SSID")),
        ],
    },

    # Child-Level: BSSIDs unter der SSID
    ("extreme_ap_bssids", "*"): {
        "title": _("BSSIDs"),
        "view": "table",
        "nesting": False,
        "columns": [
            ("bssid", _("BSSID")),
            ("frequency", _("Frequency")),
            ("clients", _("Clients")),
            ("radio_name", _("Radio")),
            ("hostname", _("AP Hostname")),
            ("device_id", _("Device ID")),
        ],
        "keyorder": ["bssid"],
    },
})
``
