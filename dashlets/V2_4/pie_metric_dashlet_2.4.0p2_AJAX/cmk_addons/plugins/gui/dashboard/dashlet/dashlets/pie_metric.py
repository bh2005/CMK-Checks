#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PieMetricDashlet – Checkmk 2.4.0p2 CEE

Dashlet-Typ zum Anzeigen eines einfachen Donut/Pie (used vs. free) für beliebige Service-Metriken.
- AJAX-Refresh: Das Dashboard ruft periodisch on_refresh() auf; diese liefert JS zurück,
  das den SVG-Inhalt im Dashlet-Container ersetzt (kein separater Backend-Page-Handler nötig).
- Autocomplete: Für used_metric/free_metric via ContextAutocompleterConfig, analog zum Muster
  aus dem graph-Dashlet (graph.py / available_graph_templates). Hier listen wir die Metriknamen
  des ausgewählten Service aus Livestatus.

Ablageort (CMK >= 2.4):
  ~/local/lib/python3/cmk_addons/plugins/gui/dashboard/dashlet/dashlets/pie_metric.py

(C) 2026 – Beispielcode für Demonstrationszwecke
"""
from __future__ import annotations
from typing import TypedDict

from cmk.gui.i18n import _
from cmk.gui.htmllib.html import html
from cmk.gui.dashboard.dashlet.base import Dashlet
from cmk.gui.dashboard.type_defs import DashletSize
from cmk.gui.type_defs import VisualContext, SingleInfos
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    DropdownChoiceWithHostAndServiceHints,
)
from cmk.gui.utils.autocompleter_config import ContextAutocompleterConfig
from cmk.gui.visuals import livestatus_query_bare

# Autocompleter-Ident (frei wählbar, muss zur Funktion unten passen)
PIE_METRIC_AC_ID = "pie_metric_metric_names"


class PieMetricDashletConfig(TypedDict, total=False):
    host: str
    service: str
    used_metric: str
    free_metric: str
    title: str


class PieMetricDashlet(Dashlet[PieMetricDashletConfig]):
    """Dashlet für simple Used/Free-Donuts aus Service-Metriken.

    Rendering-Strategie:
      * show(): erzeugt einen leeren Container und initialen SVG-Inhalt
      * on_refresh(): berechnet serverseitig aktuelle Werte und gibt JS zurück,
        das den Container per innerHTML neu befüllt (AJAX-Pattern)
    """

    # --- Metadaten ---------------------------------------------------------
    @classmethod
    def type_name(cls) -> str:
        return "pie_metric"

    @classmethod
    def title(cls) -> str:
        return _("Pie metric (used vs. free)")

    @classmethod
    def description(cls) -> str:
        return _("Displays a donut/pie of two metrics (e.g. used vs. free) for a service.")

    @classmethod
    def sort_index(cls) -> int:
        return 25

    @classmethod
    def initial_size(cls) -> DashletSize:
        return (30, 15)

    @classmethod
    def initial_refresh_interval(cls) -> int:
        return 60

    # --- Kontext & Parameter ----------------------------------------------
    @classmethod
    def has_context(cls) -> bool:
        return True

    @classmethod
    def single_infos(cls) -> SingleInfos:
        return ["host", "service"]

    @classmethod
    def vs_parameters(cls):
        return Dictionary(
            title=_("Properties"),
            render="form",
            elements=[
                ("host", TextInput(title=_("Host"))),
                ("service", TextInput(title=_("Service"))),
                (
                    "used_metric",
                    DropdownChoiceWithHostAndServiceHints(
                        title=_("Metric for 'used'"),
                        autocompleter=ContextAutocompleterConfig(
                            ident=PIE_METRIC_AC_ID,
                            strict=False,
                            show_independent_of_context=False,
                            dynamic_params_callback_name="host_and_service_hinted_autocompleter",
                        ),
                        help=_("Type to search metric names (from the selected host/service)."),
                    ),
                ),
                (
                    "free_metric",
                    DropdownChoiceWithHostAndServiceHints(
                        title=_("Metric for 'free'"),
                        autocompleter=ContextAutocompleterConfig(
                            ident=PIE_METRIC_AC_ID,
                            strict=False,
                            show_independent_of_context=False,
                            dynamic_params_callback_name="host_and_service_hinted_autocompleter",
                        ),
                        help=_("Type to search metric names (from the selected host/service)."),
                    ),
                ),
            ],
        )

    # --- Datenbeschaffung --------------------------------------------------
    def _resolve_host_service(self, context: VisualContext) -> tuple[str | None, str | None]:
        host = context.get("host") or self._dashlet_spec.get("host")
        service = context.get("service") or self._dashlet_spec.get("service")
        return host, service

    def _fetch_used_free(self, context: VisualContext) -> tuple[float, float]:
        host, service = self._resolve_host_service(context)
        if not host or not service:
            return (0.0, 0.0)

        rows = livestatus_query_bare(
            "service",
            {"host": host, "service": service},
            ["service_metrics"],
        )
        if not rows:
            return (0.0, 0.0)

        metrics_list = rows[0].get("service_metrics", [])
        metric_map: dict[str, float] = {}
        for t in metrics_list:
            if not t:
                continue
            name = t[0]
            try:
                val = float(t[1]) if len(t) > 1 else 0.0
            except Exception:
                val = 0.0
            metric_map[name] = val

        u_name = self._dashlet_spec.get("used_metric", "")
        f_name = self._dashlet_spec.get("free_metric", "")
        return (float(metric_map.get(u_name, 0.0)), float(metric_map.get(f_name, 0.0)))

    # --- Rendering ---------------------------------------------------------
    def show(self) -> None:
        div_id = f"dashlet_pie_{self._dashlet_id}"
        used, free = self._fetch_used_free(self.context if self.has_context() else {})
        svg = self._render_svg(used, free)
        html.open_div(id_=div_id, style="height:100%;width:100%;display:flex;align-items:center;justify-content:center;")
        html.write_text(svg)
        html.close_div()

    def on_refresh(self) -> str:
        used, free = self._fetch_used_free(self.context if self.has_context() else {})
        svg = self._render_svg(used, free).replace("\", "\\").replace("'", "\'")
        return (
            "(function(){var el=document.getElementById('dashlet_pie_%d');"
            "if(el){el.innerHTML='%s';}})();" % (self._dashlet_id, svg)
        )

    def on_resize(self) -> str:
        return ""

    # --- SVG-Erzeugung -----------------------------------------------------
    def _render_svg(self, used: float, free: float) -> str:
        total = (used + free) if (used + free) > 0 else 1e-6
        pct_used = max(0, min(100, int(round(100.0 * used / total))))
        color = "#16a34a" if pct_used < 70 else ("#f97316" if pct_used < 90 else "#ef4444")
        svg = (
            '<svg viewBox="0 0 42 42" width="100%" height="100%">'
            '<circle cx="21" cy="21" r="15.915" fill="#f2f2f2"/>'
            f'<circle cx="21" cy="21" r="15.915" fill="transparent" stroke="{color}" stroke-width="10" '
            f'stroke-dasharray="{pct_used} {100 - pct_used}" stroke-dashoffset="25"/>'
            f'<text x="21" y="22" text-anchor="middle" style="font: 7px sans-serif; fill: #444;">{pct_used}%</text>'
            '</svg>'
        )
        return svg


def pie_metric_metric_names_autocompleter(config: object, value_entered_by_user: str, params: dict) -> list[tuple[str, str]]:
    ctx: VisualContext = params.get("context", {})
    host = ctx.get("host")
    service = ctx.get("service")
    if not host or not service:
        return []

    try:
        rows = livestatus_query_bare("service", {"host": host, "service": service}, ["service_metrics"])  # type: ignore[arg-type]
    except Exception:
        return []

    if not rows:
        return []

    names: set[str] = set()
    for t in rows[0].get("service_metrics", []):
        if not t:
            continue
        names.add(str(t[0]))

    needle = (value_entered_by_user or "").lower()
    choices: list[tuple[str, str]] = []
    for name in sorted(names):
        if needle in name.lower():
            choices.append((name, name))
    return choices
