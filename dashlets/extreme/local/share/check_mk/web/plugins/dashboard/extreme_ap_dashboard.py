#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check_MK Custom Dashlet for Extreme Access Points

Provides interactive dashboard for Extreme Cloud IQ Access Points
directly in Check_MK GUI.

Install to: local/share/check_mk/web/plugins/dashboard/extreme_ap_dashboard.py
"""

from typing import Dict, List, Any
import json

from cmk.gui.i18n import _
from cmk.gui.plugins.dashboard.utils import Dashlet, dashlet_registry
from cmk.gui.htmllib.html import html
from cmk.gui.utils.html import HTML
from cmk.gui.valuespec import Dictionary, DropdownChoice, Integer
import cmk.gui.sites as sites
from cmk.gui.exceptions import MKGeneralException


@dashlet_registry.register
class ExtremeAPDashlet(Dashlet):
    """Dashboard showing Extreme Access Point statistics and status"""

    @classmethod
    def type_name(cls):
        return "extreme_ap_overview"

    @classmethod
    def title(cls):
        return _("Extreme Access Points Overview")

    @classmethod
    def description(cls):
        return _("Shows statistics and status of all Extreme Cloud IQ Access Points")

    @classmethod
    def sort_index(cls) -> int:
        return 50

    @classmethod
    def initial_size(cls):
        return (60, 40)  # width, height in grid units

    @classmethod
    def initial_refresh_interval(cls):
        return 60  # seconds

    @classmethod
    def vs_parameters(cls):
        """Configuration options for the dashlet"""
        return Dictionary(
            title=_("Properties"),
            render="form",
            optional_keys=["filter_site", "max_aps"],
            elements=[
                (
                    "filter_site",
                    DropdownChoice(
                        title=_("Filter by Site"),
                        help=_("Show only APs from specific site"),
                        choices=[
                            ("all", _("All Sites")),
                            ("Building-A", _("Building A")),
                            ("Building-B", _("Building B")),
                            ("Outdoor", _("Outdoor")),
                        ],
                        default_value="all",
                    ),
                ),
                (
                    "max_aps",
                    Integer(
                        title=_("Maximum APs to display"),
                        help=_("Limit number of APs shown in detail view"),
                        default_value=20,
                        minvalue=5,
                        maxvalue=100,
                    ),
                ),
            ],
        )

    def _get_ap_data(self) -> Dict[str, Any]:
        """Fetch AP data from Check_MK Livestatus"""
        
        # Get configuration
        filter_site = self._dashlet_spec.get("filter_site", "all")
        
        # Query Livestatus for hosts with Extreme AP services
        query = (
            "GET services\n"
            "Columns: host_name host_address host_state service_description state plugin_output\n"
            "Filter: service_description ~~ Extreme AP\n"
        )
        
        try:
            result = sites.live().query(query)
        except Exception as e:
            return {
                "error": f"Failed to query data: {str(e)}",
                "aps": [],
                "stats": {}
            }
        
        # Process results
        aps_data = {}
        
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
            
            # Parse service data
            if "Status" in service_desc:
                # Parse AP Status output
                # Format: hostname|serial|mac|ip|model|status|connection_state|sw_version|site
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
                # Parse Client data
                # Format: total|radio_2.4|radio_5
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
                # Parse Performance data
                # Format: cpu|memory|uptime|power_mode|poe_power
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
            
            # Store service state
            aps_data[host_name]["services"][service_desc] = {
                "state": state,
                "output": output,
            }
        
        # Filter by site if needed
        if filter_site != "all":
            aps_data = {k: v for k, v in aps_data.items() 
                       if v.get("site", "") == filter_site}
        
        # Calculate statistics
        aps_list = list(aps_data.values())
        stats = {
            "total": len(aps_list),
            "connected": len([ap for ap in aps_list if ap.get("status") == "connected"]),
            "disconnected": len([ap for ap in aps_list if ap.get("status") == "disconnected"]),
            "total_clients": sum(ap.get("clients", 0) for ap in aps_list),
            "high_load": len([ap for ap in aps_list 
                            if ap.get("cpu", 0) > 70 or ap.get("memory", 0) > 70]),
        }
        
        return {
            "aps": aps_list,
            "stats": stats,
            "error": None,
        }

    def show(self):
        """Render the dashlet"""
        data = self._get_ap_data()
        
        if data.get("error"):
            html.show_error(data["error"])
            return
        
        stats = data["stats"]
        aps = data["aps"]
        max_aps = self._dashlet_spec.get("max_aps", 20)
        
        # CSS Styles
        html.write_html(HTML("""
        <style>
            .extreme-dashboard {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 10px;
            }
            .extreme-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
                margin-bottom: 20px;
            }
            .extreme-stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .extreme-stat-card.green {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            }
            .extreme-stat-card.yellow {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }
            .extreme-stat-card.red {
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            }
            .extreme-stat-label {
                font-size: 11px;
                opacity: 0.9;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .extreme-stat-value {
                font-size: 28px;
                font-weight: bold;
            }
            .extreme-stat-sub {
                font-size: 10px;
                opacity: 0.8;
                margin-top: 5px;
            }
            .extreme-ap-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
            }
            .extreme-ap-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                overflow: hidden;
                transition: all 0.2s;
            }
            .extreme-ap-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            .extreme-ap-header {
                padding: 12px;
                background: #f7fafc;
                border-bottom: 2px solid #e2e8f0;
            }
            .extreme-ap-header.connected {
                border-bottom-color: #48bb78;
                background: #f0fff4;
            }
            .extreme-ap-header.disconnected {
                border-bottom-color: #f56565;
                background: #fff5f5;
            }
            .extreme-ap-title {
                font-weight: 600;
                font-size: 13px;
                color: #2d3748;
                margin-bottom: 3px;
            }
            .extreme-ap-site {
                font-size: 11px;
                color: #718096;
            }
            .extreme-ap-body {
                padding: 12px;
            }
            .extreme-ap-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 12px;
                font-size: 11px;
            }
            .extreme-ap-info-item {
                display: flex;
                justify-content: space-between;
            }
            .extreme-ap-info-label {
                color: #718096;
            }
            .extreme-ap-info-value {
                font-weight: 600;
                color: #2d3748;
            }
            .extreme-clients-box {
                background: #ebf8ff;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 12px;
            }
            .extreme-clients-total {
                font-size: 24px;
                font-weight: bold;
                color: #2b6cb0;
                text-align: center;
                margin-bottom: 5px;
            }
            .extreme-clients-split {
                display: flex;
                justify-content: space-around;
                font-size: 11px;
                color: #2c5282;
            }
            .extreme-metric {
                margin-bottom: 10px;
            }
            .extreme-metric-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                font-size: 11px;
            }
            .extreme-metric-label {
                color: #4a5568;
                font-weight: 600;
            }
            .extreme-metric-value {
                font-weight: bold;
            }
            .extreme-metric-value.ok { color: #48bb78; }
            .extreme-metric-value.warn { color: #ed8936; }
            .extreme-metric-value.crit { color: #f56565; }
            .extreme-progress-bar {
                height: 6px;
                background: #e2e8f0;
                border-radius: 3px;
                overflow: hidden;
            }
            .extreme-progress-fill {
                height: 100%;
                transition: width 0.3s ease;
            }
            .extreme-progress-fill.ok { background: #48bb78; }
            .extreme-progress-fill.warn { background: #ed8936; }
            .extreme-progress-fill.crit { background: #f56565; }
            .extreme-status-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
            }
            .extreme-status-badge.connected {
                background: #48bb78;
                color: white;
            }
            .extreme-status-badge.disconnected {
                background: #f56565;
                color: white;
            }
        </style>
        """))
        
        html.open_div(class_="extreme-dashboard")
        
        # Statistics Cards
        html.open_div(class_="extreme-stats")
        
        # Total APs
        html.open_div(class_="extreme-stat-card")
        html.div(stats["total"], class_="extreme-stat-value")
        html.div(_("Total APs"), class_="extreme-stat-label")
        html.div(f"{stats['connected']} online", class_="extreme-stat-sub")
        html.close_div()
        
        # Connected
        html.open_div(class_="extreme-stat-card green")
        html.div(stats["connected"], class_="extreme-stat-value")
        html.div(_("Connected"), class_="extreme-stat-label")
        html.close_div()
        
        # Total Clients
        html.open_div(class_="extreme-stat-card yellow")
        html.div(stats["total_clients"], class_="extreme-stat-value")
        html.div(_("Total Clients"), class_="extreme-stat-label")
        if stats["connected"] > 0:
            avg = round(stats["total_clients"] / stats["connected"])
            html.div(f"Ø {avg} per AP", class_="extreme-stat-sub")
        html.close_div()
        
        # Issues
        issues = stats["disconnected"] + stats["high_load"]
        html.open_div(class_="extreme-stat-card red")
        html.div(issues, class_="extreme-stat-value")
        html.div(_("Issues"), class_="extreme-stat-label")
        html.div(f"{stats['disconnected']} offline", class_="extreme-stat-sub")
        html.close_div()
        
        html.close_div()  # extreme-stats
        
        # AP Grid
        html.open_div(class_="extreme-ap-grid")
        
        for ap in aps[:max_aps]:
            status = ap.get("status", "disconnected")
            
            html.open_div(class_="extreme-ap-card")
            
            # Header
            html.open_div(class_=f"extreme-ap-header {status}")
            html.div(ap.get("hostname", "Unknown"), class_="extreme-ap-title")
            html.div(ap.get("site", "N/A"), class_="extreme-ap-site")
            html.close_div()
            
            # Body
            html.open_div(class_="extreme-ap-body")
            
            # Basic Info
            html.open_div(class_="extreme-ap-info")
            
            html.open_div(class_="extreme-ap-info-item")
            html.span(_("Model"), class_="extreme-ap-info-label")
            html.span(ap.get("model", "N/A"), class_="extreme-ap-info-value")
            html.close_div()
            
            html.open_div(class_="extreme-ap-info-item")
            html.span(_("IP"), class_="extreme-ap-info-label")
            html.span(ap.get("ip", "N/A"), class_="extreme-ap-info-value")
            html.close_div()
            
            html.open_div(class_="extreme-ap-info-item")
            html.span(_("Status"), class_="extreme-ap-info-label")
            badge_class = "connected" if status == "connected" else "disconnected"
            badge_text = _("Online") if status == "connected" else _("Offline")
            html.span(HTML(f'<span class="extreme-status-badge {badge_class}">{badge_text}</span>'))
            html.close_div()
            
            html.open_div(class_="extreme-ap-info-item")
            html.span(_("Software"), class_="extreme-ap-info-label")
            html.span(ap.get("software", "N/A"), class_="extreme-ap-info-value")
            html.close_div()
            
            html.close_div()  # extreme-ap-info
            
            if status == "connected":
                # Clients
                clients = ap.get("clients", 0)
                clients_2_4 = ap.get("clients_2_4", 0)
                clients_5 = ap.get("clients_5", 0)
                
                html.open_div(class_="extreme-clients-box")
                html.div(str(clients), class_="extreme-clients-total")
                html.open_div(class_="extreme-clients-split")
                html.span(f"2.4GHz: {clients_2_4}")
                html.span(f"5GHz: {clients_5}")
                html.close_div()
                html.close_div()
                
                # CPU
                cpu = ap.get("cpu", 0)
                cpu_class = "crit" if cpu > 80 else "warn" if cpu > 60 else "ok"
                
                html.open_div(class_="extreme-metric")
                html.open_div(class_="extreme-metric-header")
                html.span(_("CPU"), class_="extreme-metric-label")
                html.span(f"{cpu:.0f}%", class_=f"extreme-metric-value {cpu_class}")
                html.close_div()
                html.open_div(class_="extreme-progress-bar")
                html.div("", class_=f"extreme-progress-fill {cpu_class}", style=f"width: {cpu}%")
                html.close_div()
                html.close_div()
                
                # Memory
                memory = ap.get("memory", 0)
                mem_class = "crit" if memory > 80 else "warn" if memory > 60 else "ok"
                
                html.open_div(class_="extreme-metric")
                html.open_div(class_="extreme-metric-header")
                html.span(_("Memory"), class_="extreme-metric-label")
                html.span(f"{memory:.0f}%", class_=f"extreme-metric-value {mem_class}")
                html.close_div()
                html.open_div(class_="extreme-progress-bar")
                html.div("", class_=f"extreme-progress-fill {mem_class}", style=f"width: {memory}%")
                html.close_div()
                html.close_div()
            
            html.close_div()  # extreme-ap-body
            html.close_div()  # extreme-ap-card
        
        html.close_div()  # extreme-ap-grid
        
        if len(aps) > max_aps:
            html.div(HTML(f"<p style='text-align: center; margin-top: 15px; color: #718096;'>"
                         f"Showing {max_aps} of {len(aps)} APs</p>"))
        
        html.close_div()  # extreme-dashboard