#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

metric_downloads = Metric(
    name="downloads",
    title=Title("Downloads"),
    unit=Unit(DecimalNotation("")),
    color=Color.BLUE,
)

metric_average_rating = Metric(
    name="average_rating",
    title=Title("Average Rating"),
    unit=Unit(DecimalNotation("")),
    color=Color.GREEN,
)

performeter_download = Perfometer(
    name="downloads", focus_range=FocusRange(Closed(0), Open(1000)), segments=["downloads"]
)


graph_downloads = Graph(
    name="downloads",
    title=Title("Downloads"),
    compound_lines=["downloads", "average_rating"],
    minimal_range=MinimalRange(0, 2500),
)
