# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from cmk.gui.plugins.views import register_view

register_view(
    name="inv_xiq_lldp_infos",
    title="LLDP Infos",
    datasource="invtable",
    table="networking.lldp_infos",  # passt zu path=["networking","lldp_infos"]
    # EXAKTE Wunsch-Reihenfolge:
    columns=[
        "hostaddress",
        "hostname",
        "id",
        "local_port",
        "remote_port",
        "port_description",
        "management_ip",
        "remote_device",
        "mac_address",
    ],
    # Optional: lesbare Spaltentitel
    column_headers={
        "hostaddress":      "Hostaddress",
        "hostname":         "Hostname",
        "id":               "Id",
        "local_port":       "Local Port",
        "remote_port":      "Remote Port",
        "port_description": "Port Description",
        "management_ip":    "Management Ip",
        "remote_device":    "Remote Device",
        "mac_address":      "Mac Address",
    },
    # Optional: Standardsortierung der Zeilen
    sort_columns=["hostname", "local_port", "remote_port"],
)
