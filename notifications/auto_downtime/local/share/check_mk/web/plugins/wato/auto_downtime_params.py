#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Downtime nach langem DOWN – Konfiguration für Notification-Plugin
Checkmk 2.4 – flexible Downtime ohne Endzeit
"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    Float,
    String,
    DefaultValue,
)
from cmk.rulesets.v1.rule_specs import NotificationParameter
from cmk.rulesets.v1.form_specs.validators import NumberInRange


class AutoDowntimeFlexibleParams(NotificationParameter):
    @property
    def ident(self) -> str:
        return "auto_downtime_flexible"

    @property
    def spec(self):
        return Dictionary(
            title=Title("Auto-Downtime nach langem Host-DOWN (flexibel)"),
            help_text=Help(
                "Wenn ein Host länger als die eingestellte Zeit DOWN ist, "
                "wird eine flexible Downtime (ohne feste Endzeit) über die REST-API gesetzt. "
                "Die Downtime wird automatisch entfernt, sobald der Host wieder UP ist. "
                "Zeitangabe in Tagen als Dezimalzahl (z. B. 2.0 = 2 Tage, 0.5 = 12 Stunden)."
            ),
            elements={
                "duration_days": DictElement(
                    parameter_form=Float(
                        title=Title("Schwelle in Tagen"),
                        unit_symbol="Tage",
                        prefill=DefaultValue(2.0),
                        custom_validate=[NumberInRange(min_value=0.1, max_value=365.0)],
                    ),
                    required=True,
                ),
                "comment_prefix": DictElement(
                    parameter_form=String(
                        title=Title("Kommentar-Präfix (optional)"),
                        prefill=DefaultValue("Auto-Downtime: Host DOWN seit > {duration:.1f} Tagen"),
                        help_text=Help(
                            "Verfügbare Platzhalter: {duration}, {duration_days}, {hostname}"
                        ),
                    ),
                ),
            },
        )


# Automatische Registrierung – Checkmk 2.4
auto_downtime_flexible_params = AutoDowntimeFlexibleParams()