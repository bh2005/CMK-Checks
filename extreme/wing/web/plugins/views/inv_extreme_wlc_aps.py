# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# View for Extreme WiNG Access Points Inventory
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Inspired by bh2005/CMK-Checks/extreme_wlc.py and Cisco WLC inv_cisco_wlc_aps_lwap.py

from cmk.gui.i18n import _
from cmk.gui.plugins.views import (
    declare_simple_inventory_table_view,
)

declare_simple_inventory_table_view(
    ident="inv_extreme_wlc_aps",
    title=_("Extreme WiNG Access Points"),
    inventory_path="hardware.wlan.access_points.",
    columns=[
        "name",
        "mac_address",
        "ip_address",
        "model",
        "serial",
        "status",
    ],
)