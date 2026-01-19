# /opt/omd/sites/test/local/lib/python3/cmk_addons/plugins/xiq/graphing/xiq_metrics.py
from cmk.graphing.v1.metrics import Metric, Title, Unit, DecimalNotation, AutoPrecision, Color

COUNT = Unit(DecimalNotation("count"), AutoPrecision(0))

metric_xiq_aps_total = Metric(
    name="xiq_aps_total",
    title=Title("Access Points"),
    unit=COUNT,
    color=Color.BLUE,
)

metric_xiq_clients_total = Metric(
    name="xiq_clients_total",
    title=Title("Clients (gesamt)"),
    unit=COUNT,
    color=Color.GREEN,
)

metric_xiq_clients_24 = Metric(
    name="xiq_clients_24",
    title=Title("Clients (2.4 GHz)"),
    unit=COUNT,
    color=Color.LIGHT_GREEN,
)

metric_xiq_clients_5 = Metric(
    name="xiq_clients_5",
    title=Title("Clients (5 GHz)"),
    unit=COUNT,
    color=Color.ORANGE,
)

metric_xiq_clients_6 = Metric(
    name="xiq_clients_6",
    title=Title("Clients (6 GHz)"),
    unit=COUNT,
    color=Color.RED,
)
