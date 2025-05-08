# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Ruleset for Extreme WiNG Access Points Inventory Parameters
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Inspired by bh2005/CMK-Checks/extreme_wlc.py and Cisco WLC inv_cisco_wlc_aps_lwap.py

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Checkbox,
    Dictionary,
)
from cmk.gui.plugins.wato import (
    RulespecGroupInventoryParameters,
    register_check_parameters,
)

def _parameter_valuespec_inv_extreme_wlc_aps():
    """Define parameters for Extreme WiNG Access Points Inventory"""
    return Dictionary(
        title=_("Extreme WiNG Access Points Inventory"),
        elements=[
            (
                "model",
                Checkbox(
                    title=_("Include model"),
                    label=_("Include model in inventory"),
                    default_value=True,
                ),
            ),
            (
                "serial",
                Checkbox(
                    title=_("Include serial number"),
                    label=_("Include serial number in inventory"),
                    default_value=True,
                ),
            ),
            (
                "status",
                Checkbox(
                    title=_("Include status"),
                    label=_("Include status in inventory"),
                    default_value=True,
                ),
            ),
        ],
        optional_keys=["model", "serial", "status"],
    )

register_check_parameters(
    RulespecGroupInventoryParameters,
    "inv_extreme_wlc_aps",
    _("Extreme WiNG Access Points Inventory"),
    _parameter_valuespec_inv_extreme_wlc_aps,
    match_type="dict",
)