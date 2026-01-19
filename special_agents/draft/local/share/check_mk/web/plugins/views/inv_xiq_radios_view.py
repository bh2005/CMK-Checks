
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# XIQ AP Radios & BSSIDs – CMK 2.4 FIXED Version (no invalid paths)

from cmk.gui.i18n import _

try:
    from cmk.gui.plugins.inventory.displayhints import inventory_displayhints
except Exception:
    try:
        from cmk.gui.views.inventory.registry import inventory_displayhints
    except Exception:
        from cmk.gui.inventory import displayhints as inventory_displayhints


# --------------------------------------------------------------------
# 1) Parent: Table for extreme_ap_radios
# REQUIRED: ".table" suffix to avoid CMK 2.4 crashes
# --------------------------------------------------------------------

TABLE_RADIOS = "extreme_ap_radios.table"
ROW_RADIOS   = "extreme_ap_radios.*"

inventory_displayhints.update({

    TABLE_RADIOS: {
        "title": _("Extreme AP Radios"),
        "icon": "network",
        "view": "table",
        "keyorder": [
            "radio_name",
            "radio_mac",
            "frequency",
            "channel_number",
            "channel_width",
            "mode",
            "power",
            "device_id",
            "hostname",
        ],
    },

    f"{ROW_RADIOS}.radio_name":      {"title": _("Radio")},
    f"{ROW_RADIOS}.radio_mac":       {"title": _("MAC")},
    f"{ROW_RADIOS}.frequency":       {"title": _("Freq")},
    f"{ROW_RADIOS}.channel_number":  {"title": _("Channel")},
    f"{ROW_RADIOS}.channel_width":   {"title": _("Width")},
    f"{ROW_RADIOS}.mode":            {"title": _("Mode")},
    f"{ROW_RADIOS}.power":           {"title": _("Power")},
    f"{ROW_RADIOS}.device_id":       {"title": _("Device ID")},
    f"{ROW_RADIOS}.hostname":        {"title": _("Hostname")},
})


# --------------------------------------------------------------------
# 2) Children under each Radio: extreme_ap_radios.<radio_name>.*
# --------------------------------------------------------------------

TABLE_CHILD = "extreme_ap_radios.*.table"
ROW_CHILD   = "extreme_ap_radios.*.*"

inventory_displayhints.update({

    TABLE_CHILD: {
        "title": _("Radio BSSIDs"),
        "icon": "network",
        "view": "table",
        "keyorder": [
            "bssid",
            "ssid",
            "frequency",
            "clients",
            "device_id",
            "hostname",
        ],
    },

    f"{ROW_CHILD}.bssid":      {"title": _("BSSID")},
    f"{ROW_CHILD}.ssid":       {"title": _("SSID")},
    f"{ROW_CHILD}.frequency":  {"title": _("Freq")},
    f"{ROW_CHILD}.clients":    {"title": _("Clients")},
    f"{ROW_CHILD}.device_id":  {"title": _("Device ID")},
    f"{ROW_CHILD}.hostname":   {"title": _("Hostname")},
})


# --------------------------------------------------------------------
# 3) SSID Grouping: extreme_ap_bssids.table
# --------------------------------------------------------------------

TABLE_SSID = "extreme_ap_bssids.table"
ROW_SSID   = "extreme_ap_bssids.*"

inventory_displayhints.update({

    TABLE_SSID: {
        "title": _("SSIDs"),
        "icon": "network",
        "view": "table",
        "keyorder": ["ssid"],
    },

    f"{ROW_SSID}.ssid": {"title": _("SSID")},
})


# --------------------------------------------------------------------
# 4) SSID → BSSID children: extreme_ap_bssids.<SSID>.*
# --------------------------------------------------------------------

TABLE_SSID_CHILD = "extreme_ap_bssids.*.table"
ROW_SSID_CHILD   = "extreme_ap_bssids.*.*"

inventory_displayhints.update({

    TABLE_SSID_CHILD: {
        "title": _("BSSIDs"),
        "icon": "network",
        "view": "table",
        "keyorder": [
            "bssid",
            "frequency",
            "radio_name",
            "clients",
            "device_id",
            "hostname",
        ],
    },

    f"{ROW_SSID_CHILD}.bssid":      {"title": _("BSSID")},
    f"{ROW_SSID_CHILD}.frequency":  {"title": _("Freq")},
    f"{ROW_SSID_CHILD}.radio_name": {"title": _("Radio")},
    f"{ROW_SSID_CHILD}.clients":    {"title": _("Clients")},
    f"{ROW_SSID_CHILD}.device_id":  {"title": _("Device ID")},
    f"{ROW_SSID_CHILD}.hostname":   {"title": _("Hostname")},
})
