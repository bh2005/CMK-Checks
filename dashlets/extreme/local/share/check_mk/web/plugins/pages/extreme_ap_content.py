#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CMK 2.5: Iframe content page for ExtremeAPDashlet.
# Replaces the old show() method — renders standalone HTML (no CMK header).
# URL params:  filter_site=all|<site>   max_aps=<n>

from typing import Any

from cmk.gui.i18n import _
from cmk.gui.htmllib.html import html
from cmk.gui.utils.html import HTML
from cmk.gui.pages import Page, PageEndpoint, PageContext, PageResult, page_registry
import cmk.gui.sites as sites


_CSS = """
body{margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f7fafc;}
.extreme-dashboard{padding:10px;}
.extreme-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:20px;}
.extreme-stat-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:15px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);}
.extreme-stat-card.green{background:linear-gradient(135deg,#11998e 0%,#38ef7d 100%);}
.extreme-stat-card.yellow{background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);}
.extreme-stat-card.red{background:linear-gradient(135deg,#fa709a 0%,#fee140 100%);}
.extreme-stat-label{font-size:11px;opacity:.9;margin-bottom:5px;text-transform:uppercase;letter-spacing:.5px;}
.extreme-stat-value{font-size:28px;font-weight:bold;}
.extreme-stat-sub{font-size:10px;opacity:.8;margin-top:5px;}
.extreme-ap-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:15px;}
.extreme-ap-card{background:white;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;transition:all .2s;}
.extreme-ap-card:hover{box-shadow:0 4px 12px rgba(0,0,0,.15);transform:translateY(-2px);}
.extreme-ap-header{padding:12px;background:#f7fafc;border-bottom:2px solid #e2e8f0;}
.extreme-ap-header.connected{border-bottom-color:#48bb78;background:#f0fff4;}
.extreme-ap-header.disconnected{border-bottom-color:#f56565;background:#fff5f5;}
.extreme-ap-title{font-weight:600;font-size:13px;color:#2d3748;margin-bottom:3px;}
.extreme-ap-site{font-size:11px;color:#718096;}
.extreme-ap-body{padding:12px;}
.extreme-ap-info{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;font-size:11px;}
.extreme-ap-info-item{display:flex;justify-content:space-between;}
.extreme-ap-info-label{color:#718096;}
.extreme-ap-info-value{font-weight:600;color:#2d3748;}
.extreme-clients-box{background:#ebf8ff;padding:10px;border-radius:6px;margin-bottom:12px;}
.extreme-clients-total{font-size:24px;font-weight:bold;color:#2b6cb0;text-align:center;margin-bottom:5px;}
.extreme-clients-split{display:flex;justify-content:space-around;font-size:11px;color:#2c5282;}
.extreme-metric{margin-bottom:10px;}
.extreme-metric-header{display:flex;justify-content:space-between;margin-bottom:4px;font-size:11px;}
.extreme-metric-label{color:#4a5568;font-weight:600;}
.extreme-metric-value{font-weight:bold;}
.extreme-metric-value.ok{color:#48bb78;}
.extreme-metric-value.warn{color:#ed8936;}
.extreme-metric-value.crit{color:#f56565;}
.extreme-progress-bar{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;}
.extreme-progress-fill{height:100%;transition:width .3s ease;}
.extreme-progress-fill.ok{background:#48bb78;}
.extreme-progress-fill.warn{background:#ed8936;}
.extreme-progress-fill.crit{background:#f56565;}
.extreme-status-badge{display:inline-block;padding:3px 8px;border-radius:12px;font-size:10px;font-weight:600;text-transform:uppercase;}
.extreme-status-badge.connected{background:#48bb78;color:white;}
.extreme-status-badge.disconnected{background:#f56565;color:white;}
"""


def _get_ap_data(filter_site: str) -> dict[str, Any]:
    query = (
        "GET services\n"
        "Columns: host_name host_address host_state service_description state plugin_output\n"
        "Filter: service_description ~~ Extreme AP\n"
    )
    try:
        result = sites.live().query(query)
    except Exception as exc:
        return {"error": f"Livestatus query failed: {exc}", "aps": [], "stats": {}}

    aps_data: dict[str, Any] = {}
    for row in result:
        host_name, host_address, host_state, service_desc, state, output = row
        if host_name not in aps_data:
            aps_data[host_name] = {
                "hostname": host_name,
                "ip": host_address,
                "host_state": host_state,
                "status": "connected" if host_state == 0 else "disconnected",
                "services": {},
            }
        if "Status" in service_desc:
            parts = output.split("|") if "|" in output else []
            if len(parts) >= 9:
                aps_data[host_name].update({
                    "serial": parts[1],
                    "mac": parts[2],
                    "model": parts[4],
                    "connection_state": parts[6],
                    "software": parts[7],
                    "site": parts[8],
                })
        elif "Clients" in service_desc:
            parts = output.split("|") if "|" in output else []
            if len(parts) >= 3:
                try:
                    aps_data[host_name].update({
                        "clients": int(parts[0]),
                        "clients_2_4": int(parts[1]),
                        "clients_5": int(parts[2]),
                    })
                except (ValueError, IndexError):
                    pass
        elif "Details" in service_desc:
            parts = output.split("|") if "|" in output else []
            if len(parts) >= 5:
                try:
                    aps_data[host_name].update({
                        "cpu": float(parts[0]),
                        "memory": float(parts[1]),
                        "uptime": int(parts[2]),
                    })
                except (ValueError, IndexError):
                    pass
        aps_data[host_name]["services"][service_desc] = {"state": state, "output": output}

    if filter_site != "all":
        aps_data = {k: v for k, v in aps_data.items() if v.get("site", "") == filter_site}

    aps_list = list(aps_data.values())
    stats = {
        "total": len(aps_list),
        "connected": len([a for a in aps_list if a.get("status") == "connected"]),
        "disconnected": len([a for a in aps_list if a.get("status") == "disconnected"]),
        "total_clients": sum(a.get("clients", 0) for a in aps_list),
        "high_load": len([a for a in aps_list if a.get("cpu", 0) > 70 or a.get("memory", 0) > 70]),
    }
    return {"aps": aps_list, "stats": stats, "error": None}


class ExtremeAPContentPage(Page):
    def page(self, ctx: PageContext) -> PageResult:
        request = ctx.request
        filter_site = request.get_str_input("filter_site") or "all"
        try:
            max_aps = int(request.get_str_input("max_aps") or "20")
        except ValueError:
            max_aps = 20

        data = _get_ap_data(filter_site)

        html.write_html(HTML(
            f"<!DOCTYPE html><html><head>"
            f"<meta charset='utf-8'>"
            f"<style>{_CSS}</style>"
            f"</head><body>"
            f"<div class='extreme-dashboard'>"
        ))

        if data.get("error"):
            html.write_html(HTML(f"<p style='color:red;padding:10px'>{data['error']}</p>"))
        else:
            self._render(data["stats"], data["aps"], max_aps)

        html.write_html(HTML("</div></body></html>"))
        return None

    def _render(self, stats: dict, aps: list, max_aps: int) -> None:
        # --- Stat Cards ---
        html.open_div(class_="extreme-stats")

        html.open_div(class_="extreme-stat-card")
        html.div(str(stats["total"]), class_="extreme-stat-value")
        html.div(_("Total APs"), class_="extreme-stat-label")
        html.div(f"{stats['connected']} online", class_="extreme-stat-sub")
        html.close_div()

        html.open_div(class_="extreme-stat-card green")
        html.div(str(stats["connected"]), class_="extreme-stat-value")
        html.div(_("Connected"), class_="extreme-stat-label")
        html.close_div()

        html.open_div(class_="extreme-stat-card yellow")
        html.div(str(stats["total_clients"]), class_="extreme-stat-value")
        html.div(_("Total Clients"), class_="extreme-stat-label")
        if stats["connected"] > 0:
            avg = round(stats["total_clients"] / stats["connected"])
            html.div(f"Ø {avg} per AP", class_="extreme-stat-sub")
        html.close_div()

        issues = stats["disconnected"] + stats["high_load"]
        html.open_div(class_="extreme-stat-card red")
        html.div(str(issues), class_="extreme-stat-value")
        html.div(_("Issues"), class_="extreme-stat-label")
        html.div(f"{stats['disconnected']} offline", class_="extreme-stat-sub")
        html.close_div()

        html.close_div()  # extreme-stats

        # --- AP Cards ---
        html.open_div(class_="extreme-ap-grid")

        for ap in aps[:max_aps]:
            status = ap.get("status", "disconnected")

            html.open_div(class_="extreme-ap-card")

            html.open_div(class_=f"extreme-ap-header {status}")
            html.div(ap.get("hostname", "Unknown"), class_="extreme-ap-title")
            html.div(ap.get("site", "N/A"), class_="extreme-ap-site")
            html.close_div()

            html.open_div(class_="extreme-ap-body")
            html.open_div(class_="extreme-ap-info")

            for label, value in [
                (_("Model"), ap.get("model", "N/A")),
                (_("IP"), ap.get("ip", "N/A")),
                (_("Software"), ap.get("software", "N/A")),
            ]:
                html.open_div(class_="extreme-ap-info-item")
                html.span(label, class_="extreme-ap-info-label")
                html.span(str(value), class_="extreme-ap-info-value")
                html.close_div()

            badge_cls = "connected" if status == "connected" else "disconnected"
            badge_txt = _("Online") if status == "connected" else _("Offline")
            html.open_div(class_="extreme-ap-info-item")
            html.span(_("Status"), class_="extreme-ap-info-label")
            html.write_html(HTML(f'<span class="extreme-status-badge {badge_cls}">{badge_txt}</span>'))
            html.close_div()

            html.close_div()  # extreme-ap-info

            if status == "connected":
                clients = ap.get("clients", 0)
                html.open_div(class_="extreme-clients-box")
                html.div(str(clients), class_="extreme-clients-total")
                html.open_div(class_="extreme-clients-split")
                html.span(f"2.4 GHz: {ap.get('clients_2_4', 0)}")
                html.span(f"5 GHz: {ap.get('clients_5', 0)}")
                html.close_div()
                html.close_div()

                for metric_key, metric_label in [("cpu", _("CPU")), ("memory", _("Memory"))]:
                    val = ap.get(metric_key, 0)
                    css = "crit" if val > 80 else "warn" if val > 60 else "ok"
                    html.open_div(class_="extreme-metric")
                    html.open_div(class_="extreme-metric-header")
                    html.span(metric_label, class_="extreme-metric-label")
                    html.span(f"{val:.0f}%", class_=f"extreme-metric-value {css}")
                    html.close_div()
                    html.open_div(class_="extreme-progress-bar")
                    html.div("", class_=f"extreme-progress-fill {css}", style=f"width:{val}%")
                    html.close_div()
                    html.close_div()

            html.close_div()  # extreme-ap-body
            html.close_div()  # extreme-ap-card

        html.close_div()  # extreme-ap-grid

        if len(aps) > max_aps:
            html.write_html(HTML(
                f"<p style='text-align:center;margin-top:15px;color:#718096'>"
                f"Showing {max_aps} of {len(aps)} APs</p>"
            ))


page_registry.register(PageEndpoint("extreme_ap_content", ExtremeAPContentPage()))
