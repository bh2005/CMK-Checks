
from cmk.graphing.v1.perfometers import (
    Perfometer, Stacked, FocusRange, Closed
)

# Fokusbereich für relative Skalierung (0..100)
RANGE = FocusRange(Closed(0), Closed(100))

# ------------------------------------------------------------
# Perf-O-Meter: AP-Zahl (lineares Segment)
# ------------------------------------------------------------
perfometer_xiq_summary_aps = Perfometer(
    name="perfometer_xiq_summary_aps",
    focus_range=RANGE,
    segments=["xiq_aps_total"],
)

# ------------------------------------------------------------
# Perf-O-Meter: Clients (gestapelt 24/5/6)
# ------------------------------------------------------------
perfometer_xiq_summary_clients = Stacked(
    name="perfometer_xiq_summary_clients",
    lower=Perfometer(
        name="perfometer_xiq_summary_clients_24",
        focus_range=RANGE,
        segments=["xiq_clients_24"],
    ),
    upper=Stacked(
        name="perfometer_xiq_summary_clients_5_6",
        lower=Perfometer(
            name="perfometer_xiq_summary_clients_5",
            focus_range=RANGE,
            segments=["xiq_clients_5"],
        ),
        upper=Perfometer(
            name="perfometer_xiq_summary_clients_6",
            focus_range=RANGE,
            segments=["xiq_clients_6"],
        )
    )
)
