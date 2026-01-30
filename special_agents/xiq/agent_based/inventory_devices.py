#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List
from cmk.agent_based.v2 import (
    InventoryPlugin,
    TableRow,
)

from .common import extract_location_leaf, norm_connected

def inventory_xiq_devices(section: List[List[str]]):
    for row in section:
        # Robustes Auslesen nach Index (Sektionen liefern 11 Spalten – Index 10 ist connected)
        dev_id      = row[0] if len(row) > 0 else ""
        hostname    = row[1] if len(row) > 1 else ""
        serial      = row[2] if len(row) > 2 else ""
        mac         = row[3] if len(row) > 3 else ""
        ip          = row[4] if len(row) > 4 else ""
        model       = row[5] if len(row) > 5 else ""
        sw          = row[6] if len(row) > 6 else ""
        loc_full    = row[7] if len(row) > 7 else ""
        dev_fun     = row[8] if len(row) > 8 else ""
        managed_by  = row[9] if len(row) > 9 else ""
        connected_v = row[10] if len(row) > 10 else None

        dev_fun_u = (dev_fun or "").upper()
        if "AP" in dev_fun_u:
            path = ["extreme", "ap"]
        elif "SW" in dev_fun_u:
            path = ["extreme", "sw"]
        else:
            path = ["extreme", "misc"]

        attrs = {
            "hostname": hostname,
            "serial": serial,
            "mac": mac,
            "ip": ip,
            "model": model,
            "software": sw,
            "location_full": loc_full,
            "location_leaf": extract_location_leaf(loc_full),
            "device_function": dev_fun_u,
            "managed_by": managed_by,
        }
        if connected_v is not None:
            attrs["connected"] = norm_connected(connected_v)

        # Keine Filterung: ALLE Geräte werden inventarisiert
        yield TableRow(
            path=path,
            key_columns={"id": dev_id},
            inventory_columns=attrs,
        )

inventory_plugin_xiq_devices = InventoryPlugin(
    name="xiq_inventory_devices",
    sections=["extreme_device_inventory"],
    inventory_function=inventory_xiq_devices,
)
