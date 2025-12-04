#!/usr/bin/env python3
# 
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Graphing: ExtremeCloud IQ Controller


from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, TimeNotation, Unit
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Stacked, Perfometer


metric_netextreme_xiq_controller_uptime = Metric(
    name = "netextreme_xiq_controller_uptime",
    title = Title("AP uptime"),
    unit = Unit(TimeNotation()),
    color = Color.LIGHT_GREEN
)


metric_netextreme_xiq_controller_ap_clients = Metric(
    name = "netextreme_xiq_controller_ap_clients",
    title = Title("AP clients"),
    unit = Unit(DecimalNotation("")),
    color = Color.YELLOW
)


metric_netextreme_xiq_controller_ap_power = Metric(
    name = "netextreme_xiq_controller_ap_power",
    title = Title("AP Power"),
    unit = Unit(DecimalNotation("W")),
    color = Color.LIGHT_ORANGE
)


metric_netextreme_xiq_controller_clients = Metric(
    name = "netextreme_xiq_controller_clients",
    title = Title("Active clients"),
    unit = Unit(DecimalNotation("")),
    color = Color.YELLOW
)


perfometer_netextreme_xiq_controller_clients = Perfometer(
    name='perfometer_netextreme_xiq_controller_clients',
    focus_range = FocusRange(Closed(0), Open(1000)),
    segments = ["netextreme_xiq_controller_clients"],
)


perfometer_netextreme_xiq_controller_ap = Stacked(
    name='perfometer_netextreme_xiq_controller_ap',
    upper=Perfometer(
        name='perfometer_netextreme_xiq_controller_ap_upper',
        segments=['netextreme_xiq_controller_uptime'],
        focus_range=FocusRange(lower=Closed(0), upper=Open(31536000))
    ),
    lower=Perfometer(
        name='perfometer_netextreme_xiq_controller_ap_lower',
        segments=['netextreme_xiq_controller_ap_clients'],
        focus_range=FocusRange(lower=Closed(0), upper=Open(100))
    ))
