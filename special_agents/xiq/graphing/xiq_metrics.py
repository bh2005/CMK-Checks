#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XIQ Metrics (Checkmk 2.4, Graphing API v1)

Diese Datei definiert alle Metriken, die in den XIQ-Checks und Graphs/Perf-O-Metern
verwendet werden. Farben/Titel sind konsistent fuer NOC-Dashboards.

Pfad: ~/local/lib/check_mk/graphing/xiq_summary/metrics.py
"""
from cmk.graphing.v1 import metrics

# --------------------------------------------------------------------
# Einheit: Ganzzahl (count) ohne Nachkommastellen
# --------------------------------------------------------------------
UNIT_COUNTER = metrics.Unit(metrics.DecimalNotation(""), metrics.AutoPrecision(0))

# --------------------------------------------------------------------
# Access Points (gesamt / optional: connected / disconnected)
# --------------------------------------------------------------------
metric_xiq_aps_total = metrics.Metric(
    name="xiq_aps_total",
    title=metrics.Title("Access Points gesamt"),
    unit=UNIT_COUNTER,
    color=metrics.Color.BLUE,
)

# Optional, falls dein Check diese Metriken liefert:
metric_xiq_aps_connected = metrics.Metric(
    name="xiq_aps_connected",
    title=metrics.Title("Access Points verbunden"),
    unit=UNIT_COUNTER,
    color=metrics.Color.LIGHT_GREEN,
)

metric_xiq_aps_disconnected = metrics.Metric(
    name="xiq_aps_disconnected",
    title=metrics.Title("Access Points getrennt"),
    unit=UNIT_COUNTER,
    color=metrics.Color.LIGHT_RED,
)

# --------------------------------------------------------------------
# Clients (gesamt und je Band)
# --------------------------------------------------------------------
metric_xiq_clients_total = metrics.Metric(
    name="xiq_clients_total",
    title=metrics.Title("Clients gesamt"),
    unit=UNIT_COUNTER,
    color=metrics.Color.GREEN,
)

metric_xiq_clients_24 = metrics.Metric(
    name="xiq_clients_24",
    title=metrics.Title("Clients (2.4 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.LIGHT_GREEN,   # konsistent mit Band-Farbschema
)

metric_xiq_clients_5 = metrics.Metric(
    name="xiq_clients_5",
    title=metrics.Title("Clients (5 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.ORANGE,
)

metric_xiq_clients_6 = metrics.Metric(
    name="xiq_clients_6",
    title=metrics.Title("Clients (6 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.RED,
)

# --------------------------------------------------------------------
# API-Quota / Remaining (optional)
# --------------------------------------------------------------------
metric_xiq_api_remaining = metrics.Metric(
    name="xiq_api_remaining",
    title=metrics.Title("API Requests verbleibend"),
    unit=UNIT_COUNTER,
    color=metrics.Color.DARK_BLUE,
)