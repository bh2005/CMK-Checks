#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from cmk.agent_based.v2 import (
    InventoryPlugin,
    TableRow,
)

def inventory_xiq_neighbors(section):
    for e in section:
        key = f"{e.get('device_id','')}_{e.get('local_port','')}"
        yield TableRow(
            path=["networking", "lldp_infos"],
            key_columns={"key": key},
            inventory_columns={
                "device_id":        e.get("device_id", ""),
                "hostname":         e.get("hostname", ""),
                "host_ip":          e.get("host_ip", ""),
                "local_port":       e.get("local_port", ""),
                "management_ip":    e.get("management_ip", ""),
                "remote_port":      e.get("remote_port", ""),
                "port_description": e.get("port_description", ""),
                "mac_address":      e.get("mac_address", ""),
                "remote_device":    e.get("remote_device", ""),
            },
        )

inventory_plugin_xiq_neighbors = InventoryPlugin(
    name="xiq_inventory_neighbors",
    sections=["extreme_device_neighbors"],
    inventory_function=inventory_xiq_neighbors,
)
