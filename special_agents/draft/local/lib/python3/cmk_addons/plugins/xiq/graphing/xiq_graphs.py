# /opt/omd/sites/test/local/lib/python3/cmk_addons/plugins/xiq/graphing/xiq_graphs.py

from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Title

# ------------------------------------------------------------
# Graph 1: Anzahl der APs
# ------------------------------------------------------------
graph_xiq_summary_aps = Graph(
    name="graph_xiq_summary_aps",
    title=Title("XIQ: Anzahl Access Points"),
    minimal_range=MinimalRange(0, 1),
    simple_lines=["xiq_aps_total"],
    optional=["xiq_aps_total"],
)

# ------------------------------------------------------------
# Graph 2: Anzahl der Clients (gestapelt nach Frequenzen)
# ------------------------------------------------------------
graph_xiq_summary_clients = Graph(
    name="graph_xiq_summary_clients",
    title=Title("XIQ: Anzahl Clients (2.4 / 5 / 6 GHz)"),
    minimal_range=MinimalRange(0, 1),
    compound_lines=[
        "xiq_clients_24",
        "xiq_clients_5",
        "xiq_clients_6",
    ],
    simple_lines=["xiq_clients_total"],
    optional=["xiq_clients_total"],
)

