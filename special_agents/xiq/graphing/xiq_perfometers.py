# -*- coding: utf-8 -*-
# Perfometers for ExtremeCloudIQ Summary

from cmk.graphing.v1 import perfometers

# ------------------------------------------------------------
# Focus Ranges
# ------------------------------------------------------------
# Define the display ranges for our metrics
# Closed() means the range has hard boundaries
RANGE_APS = perfometers.FocusRange(
    perfometers.Closed(0),
    perfometers.Closed(100)
)

RANGE_CLIENTS = perfometers.FocusRange(
    perfometers.Closed(0),
    perfometers.Closed(600)
)

# ------------------------------------------------------------
# Haupt-Perfometer: Stacked (APs unten, Clients oben)
# ------------------------------------------------------------
# Dieser Perfometer wird automatisch fuer den Check "xiq_summary" 
# verwendet, wenn alle benoetigten Metriken verfuegbar sind.
# Der Name muss NICHT zwingend dem Check-Namen entsprechen,
# aber es ist Best Practice.
perfometer_xiq_summary = perfometers.Stacked(
    name="xiq_summary",
    lower=perfometers.Perfometer(
        name="xiq_summary_lower",
        focus_range=RANGE_APS,
        segments=["xiq_aps_total"],
    ),
    upper=perfometers.Perfometer(
        name="xiq_summary_upper",
        focus_range=RANGE_CLIENTS,
        segments=[
            "xiq_clients_24",  # Wird als gestackte Segmente angezeigt
            "xiq_clients_5",   # in verschiedenen Farben
            "xiq_clients_6",
        ],
    ),
)

# ------------------------------------------------------------
# Alternative Perfometer (werden automatisch gewaehlt wenn
# nur ein Teil der Metriken verfuegbar ist)
# ------------------------------------------------------------

# Nur APs anzeigen
perfometer_xiq_aps_only = perfometers.Perfometer(
    name="xiq_aps_only",
    focus_range=RANGE_APS,
    segments=["xiq_aps_total"],
)

# Nur Clients gesamt
perfometer_xiq_clients_only = perfometers.Perfometer(
    name="xiq_clients_only",
    focus_range=RANGE_CLIENTS,
    segments=["xiq_clients_total"],
)

# Clients aufgeteilt nach Frequenz
perfometer_xiq_clients_by_frequency = perfometers.Perfometer(
    name="xiq_clients_by_frequency",
    focus_range=RANGE_CLIENTS,
    segments=[
        "xiq_clients_24",
        "xiq_clients_5",
        "xiq_clients_6",
    ],
)