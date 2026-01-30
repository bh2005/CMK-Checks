# -*- coding: utf-8 -*-
# Graphs for ExtremeCloudIQ Summary

from cmk.graphing.v1 import graphs, metrics

# ------------------------------------------------------------
# Graph 1: Access Points
# ------------------------------------------------------------
graph_xiq_aps = graphs.Graph(
    name="xiq_aps",
    title=metrics.Title("XIQ: Access Points"),
    minimal_range=graphs.MinimalRange(0, 10),
    simple_lines=["xiq_aps_total"],
)

# ------------------------------------------------------------
# Graph 2: Clients nach Frequenz (gestacked)
# ------------------------------------------------------------
#graph_xiq_clients_by_frequency = graphs.Graph(
#    name="xiq_clients_by_frequency",
#    title=metrics.Title("XIQ: Clients nach Frequenz"),
#    minimal_range=graphs.MinimalRange(0, 10),
#    compound_lines=[
#        "xiq_clients_24",
#        "xiq_clients_5",
#        "xiq_clients_6",
#    ],
#)

# ------------------------------------------------------------
# Graph 3: Clients gesamt
# ------------------------------------------------------------
#graph_xiq_clients_total = graphs.Graph(
#    name="xiq_clients_total",
#    title=metrics.Title("XIQ: Clients gesamt"),
#    minimal_range=graphs.MinimalRange(0, 10),
#    simple_lines=["xiq_clients_total"],
#)

# ------------------------------------------------------------
# Graph 4: Kombinierte Uebersicht APs + Clients
# ------------------------------------------------------------
#graph_xiq_overview = graphs.Graph(
#    name="xiq_overview",
#    title=metrics.Title("XIQ: Overview APs & Clients"),
#    minimal_range=graphs.MinimalRange(0, 10),
#    simple_lines=[
#        "xiq_aps_total",
#        "xiq_clients_total",
#    ],
#)

# ------------------------------------------------------------
# Graph 5: Clients mit Frequenzen + Total
# ------------------------------------------------------------
graph_xiq_clients_combined = graphs.Graph(
    name="xiq_clients_combined",
    title=metrics.Title("XIQ: Clients (total and by frequency)"),
    minimal_range=graphs.MinimalRange(0, 10),
    compound_lines=[
        "xiq_clients_24",
        "xiq_clients_5",
        "xiq_clients_6",
    ],
    simple_lines=["xiq_clients_total"],
)

# ------------------------------------------------------------
# Graph 6: API Remaining
# ------------------------------------------------------------
graph_xiq_api_remaining = graphs.Graph(
    name="xiq_api_remaining",
    title=metrics.Title("XIQ: API Calls Remaining"),
    minimal_range=graphs.MinimalRange(0, 1000),
    simple_lines=["xiq_api_remaining"],
)