#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XIQ Metrics (Checkmk 2.4, Graphing API v1)

Diese Datei definiert alle Metriken, die in den XIQ-Checks und Graphs/Perf-O-Metern
verwendet werden. Farben/Titel sind konsistent fuer NOC-Dashboards.

Pfad: ~/local/lib/check_mk/graphing/xiq_summary/metrics.py
"""
from cmk.graphing.v1 import metrics, unit

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

# --------------------------------------------------------------------
# Uptime
# --------------------------------------------------------------------
metric_xiq_uptime_seconds = metrics.Metric(
    name="xiq_uptime_seconds",
    title=metrics.Title("Uptime"),
    unit=unit.SECOND,
    color=metrics.Color.BLUE,
)

metric_xiq_uptime_days = metrics.Metric(
    name="xiq_uptime_days",
    title=metrics.Title("Uptime (Tage)"),
    unit=metrics.Unit(metrics.DecimalNotation("d"), metrics.AutoPrecision(0)),
    color=metrics.Color.BLUE,
)

# --------------------------------------------------------------------
# SSID-Clients
# --------------------------------------------------------------------
metric_xiq_ssid_clients_total = metrics.Metric(
    name="xiq_ssid_clients_total",
    title=metrics.Title("SSID Clients (gesamt)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.GREEN,
)

metric_xiq_ssid_clients_24 = metrics.Metric(
    name="xiq_ssid_clients_24",
    title=metrics.Title("SSID Clients (2.4 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.LIGHT_GREEN,
)

metric_xiq_ssid_clients_5 = metrics.Metric(
    name="xiq_ssid_clients_5",
    title=metrics.Title("SSID Clients (5 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.ORANGE,
)

metric_xiq_ssid_clients_6 = metrics.Metric(
    name="xiq_ssid_clients_6",
    title=metrics.Title("SSID Clients (6 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.RED,
)

# --------------------------------------------------------------------
# Radio-Clients
# --------------------------------------------------------------------
metric_xiq_radio_clients_total = metrics.Metric(
    name="xiq_radio_clients_total",
    title=metrics.Title("Radio Clients (gesamt)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.GREEN,
)

metric_xiq_radio_clients_24 = metrics.Metric(
    name="xiq_radio_clients_24",
    title=metrics.Title("Radio Clients (2.4 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.LIGHT_GREEN,
)

metric_xiq_radio_clients_5 = metrics.Metric(
    name="xiq_radio_clients_5",
    title=metrics.Title("Radio Clients (5 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.ORANGE,
)

metric_xiq_radio_clients_6 = metrics.Metric(
    name="xiq_radio_clients_6",
    title=metrics.Title("Radio Clients (6 GHz)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.RED,
)

# --------------------------------------------------------------------
# Radio Power & Channels
# --------------------------------------------------------------------
metric_xiq_radio_power_avg_dbm = metrics.Metric(
    name="xiq_radio_power_avg_dbm",
    title=metrics.Title("Radio Power (Ø, dBm)"),
    unit=metrics.Unit(metrics.DecimalNotation("dBm"), metrics.AutoPrecision(0)),
    color=metrics.Color.PURPLE,
)

metric_xiq_radio_power_min_dbm = metrics.Metric(
    name="xiq_radio_power_min_dbm",
    title=metrics.Title("Radio Power (min, dBm)"),
    unit=metrics.Unit(metrics.DecimalNotation("dBm"), metrics.AutoPrecision(0)),
    color=metrics.Color.DARK_PURPLE,
)

metric_xiq_radio_channels_count = metrics.Metric(
    name="xiq_radio_channels_count",
    title=metrics.Title("Radio Channels (distinct)"),
    unit=UNIT_COUNTER,
    color=metrics.Color.GRAY,
)