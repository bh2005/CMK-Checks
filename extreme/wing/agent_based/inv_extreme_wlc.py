# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Inventory Plug-in for Extreme WiNG Wireless LAN Controller Access Points
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Inspired by bh2005/CMK-Checks/extreme_wlc.py and inv_cisco_wlc_aps_lwap.py

from typing import List, Optional
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    StringTable,
    InventoryResult,
)
from cmk.base.plugins.agent_based.utils.inventory import Attributes
import json

def parse_wing_ap(string_table: StringTable) -> Optional[List[dict]]:
    """Parse JSON data from the wing_ap agent section.

    Args:
        string_table: List of strings from the agent output.

    Returns:
        Parsed JSON list of access point data or None if parsing fails.
    """
    try:
        json_data = " ".join(" ".join(line) for line in string_table)
        return json.loads(json_data)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing wing_ap data: {e}")
        return None

register.agent_section(
    name="wing_ap",
    parse_function=parse_wing_ap,
)

def inventory_extreme_wlc_aps(section: Optional[List[dict]]) -> InventoryResult:
    """Generate inventory data for Extreme WiNG access points.

    Args:
        section: Parsed JSON data from the wing_ap section.

    Yields:
        Inventory attributes for each access point.
    """
    if not section:
        return

    for ap in section:
        yield Attributes(
            path=["hardware", "wlan", "access_points"],
            inventory_attributes={
                "name": ap.get("Name", ""),
                "mac_address": ap.get("MAC", ""),
                "ip_address": ap.get("IP", ""),
                "model": ap.get("Model", ""),
                "serial": ap.get("Serial", ""),
                "status": ap.get("Status", {}).get("State", ""),
            },
        )

register.inventory_plugin(
    name="extreme_wlc_aps",
    sections=["wing_ap"],
    inventory_function=inventory_extreme_wlc_aps,
)