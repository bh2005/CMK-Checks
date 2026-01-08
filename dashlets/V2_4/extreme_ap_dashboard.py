#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check_MK 2.4 Compatible Extreme AP Dashlet

Install to: local/lib/check_mk/gui/plugins/dashboard/extreme_ap_dashboard.py
"""

from typing import Dict, List, Any
import json

from cmk.gui.i18n import _
from cmk.gui.htmllib.html import html
from cmk.gui.utils.html import HTML
from cmk.gui.valuespec import Dictionary, DropdownChoice, Integer

try:
    # Check_MK 2.4 API
    from cmk.gui.dashboard.dashlet import Dashlet, dashlet_registry
    import cmk.gui.sites as sites
except ImportError:
    # Fallback for older versions
    from cmk.gui.plugins.dashboard.utils import Dashlet, dashlet_registry
    import cmk.gui.sites as sites


@dashlet_registry.register
class ExtremeAPDashlet(Dashlet):
    """Dashboard showing Extreme Access Point statistics"""

    @classmethod
    def type_name(cls):
        return "extreme_ap_overview"

    @classmethod
    def title(cls):
        return _("Extreme Access Points")

    @classmethod
    def description(cls):
        return _("Overview of Extreme Cloud IQ Access Points")

    @classmethod
    def sort_index(cls):
        return 50

    @classmethod
    def initial_size(cls):
        return (60, 40)

    @classmethod
    def is_resizable(cls):
        return True

    @classmethod
    def initial_refresh_interval(cls):
        return 60

    @classmethod
    def vs_parameters(cls):
        return Dictionary(
            title=_("Properties"),
            render="form",
            optional_keys=["filter_site", "max_aps"],
            elements=[
                (
                    "filter_site",
                    DropdownChoice(
                        title=_("Filter by Site"),
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
                        title=_("Maximum APs"),
                        default_value=20,
                        minvalue=5,
                        maxvalue=100,
                    ),
                ),
            ],
        )

    def _get_ap_data(self) -> Dict[str, Any]:
        """Fetch AP data from Livestatus"""
        filter_site = self._dashlet_spec.get("filter_site", "all")
        
        query = (
            "GET services\n"
            "Columns: host_name host_address host_state service_description state plugin_output\n"
            "Filter: service_description ~~ Extreme AP\n"
        )
        
        try:
            with sites.live() as live:
                result = live.query(query)
        except Exception as e:
            return {
                "error": f"Query failed: {str(e)}",
                "aps": [],
                "stats": {}
            }
        
        aps_data = {}
        
        for row in result:
            host_name = row[0]
            host_address = row[1]
            host_state = row[2]
            service_desc = row[3]
            state = row[4]
            output = row[5]
            
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
            
            aps_data[host_name]["services"][service_desc] = {
                "state": state,
                "output": output,
            }
        
        if filter_site != "all":
            aps_data = {k: v for k, v in aps_data.items() 
                       if v.get("site", "") == filter_site}
        
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
        
        # Use unique ID for this dashlet instance
        dashlet_id = self.dashlet_id
        
        html.write_html(HTML(f"""
        <style>
            .extreme-dash-{dashlet_id} {{
                font-family: -apple-system, sans-serif;
                padding: 10px;
                height: 100%;
                overflow-y: auto;
            }}
            .extreme-stats-{dashlet_id} {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
                margin-bottom: 20px;
            }}
            .extreme-stat-{dashlet_id} {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .extreme-stat-{dashlet_id}.green {{
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            }}
            .extreme-stat-{dashlet_id}.yellow {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            .extreme-stat-{dashlet_id}.red {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            }}
            .extreme-stat-label-{dashlet_id} {{
                font-size: 11px;
                opacity: 0.9;
                text-transform: uppercase;
            }}
            .extreme-stat-value-{dashlet_id} {{
                font-size: 28px;
                font-weight: bold;
                margin: 5px 0;
            }}
            .extreme-ap-grid-{dashlet_id} {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 15px;
            }}
            .extreme-ap-card-{dashlet_id} {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                overflow: hidden;
                transition: all 0.2s;
            }}
            .extreme-ap-card-{dashlet_id}:hover {{
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }}
            .extreme-ap-header-{dashlet_id} {{
                padding: 12px;
                background: #f7fafc;
                border-bottom: 2px solid #e2e8f0;
            }}
            .extreme-ap-header-{dashlet_id}.connected {{
                border-bottom-color: #48bb78;
                background: #f0fff4;
            }}
            .extreme-ap-header-{dashlet_id}.disconnected {{
                border-bottom-color: #f56565;
                background: #fff5f5;
            }}
            .extreme-ap-title-{dashlet_id} {{
                font-weight: 600;
                font-size: 13px;
                color: #2d3748;
            }}
            .extreme-ap-site-{dashlet_id} {{
                font-size: 11px;
                color: #718096;
            }}
            .extreme-ap-body-{dashlet_id} {{
                padding: 12px;
            }}
            .extreme-clients-{dashlet_id} {{
                background: #ebf8ff;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 12px;
                text-align: center;
            }}
            .extreme-clients-total-{dashlet_id} {{
                font-size: 24px;
                font-weight: bold;
                color: #2b6cb0;
            }}
            .extreme-clients-split-{dashlet_id} {{
                font-size: 11px;
                color: #2c5282;
                margin-top: 5px;
            }}
            .extreme-metric-{dashlet_id} {{
                margin-bottom: 10px;
            }}
            .extreme-metric-header-{dashlet_id} {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                font-size: 11px;
            }}
            .extreme-progress-{dashlet_id} {{
                height: 6px;
                background: #e2e8f0;
                border-radius: 3px;
                overflow: hidden;
            }}
            .extreme-progress-fill-{dashlet_id} {{
                height: 100%;
                transition: width 0.3s ease;
            }}
            .extreme-progress-fill-{dashlet_id}.ok {{ background: #48bb78; }}
            .extreme-progress-fill-{dashlet_id}.warn {{ background: #ed8936; }}
            .extreme-progress-fill-{dashlet_id}.crit {{ background: #f56565; }}
        </style>
        """))
        
        html.open_div(class_=f"extreme-dash-{dashlet_id}")
        
        # Stats
        html.open_div(class_=f"extreme-stats-{dashlet_id}")
        
        html.open_div(class_=f"extreme-stat-{dashlet_id}")
        html.div(str(stats["total"]), class_=f"extreme-stat-value-{dashlet_id}")
        html.div(_("Total APs"), class_=f"extreme-stat-label-{dashlet_id}")
        html.close_div()
        
        html.open_div(class_=f"extreme-stat-{dashlet_id} green")
        html.div(str(stats["connected"]), class_=f"extreme-stat-value-{dashlet_id}")
        html.div(_("Connected"), class_=f"extreme-stat-label-{dashlet_id}")
        html.close_div()
        
        html.open_div(class_=f"extreme-stat-{dashlet_id} yellow")
        html.div(str(stats["total_clients"]), class_=f"extreme-stat-value-{dashlet_id}")
        html.div(_("Total Clients"), class_=f"extreme-stat-label-{dashlet_id}")
        html.close_div()
        
        issues = stats["disconnected"] + stats["high_load"]
        html.open_div(class_=f"extreme-stat-{dashlet_id} red")
        html.div(str(issues), class_=f"extreme-stat-value-{dashlet_id}")
        html.div(_("Issues"), class_=f"extreme-stat-label-{dashlet_id}")
        html.close_div()
        
        html.close_div()  # stats
        
        # AP Grid
        html.open_div(class_=f"extreme-ap-grid-{dashlet_id}")
        
        for ap in aps[:max_aps]:
            status = ap.get("status", "disconnected")
            
            html.open_div(class_=f"extreme-ap-card-{dashlet_id}")
            
            html.open_div(class_=f"extreme-ap-header-{dashlet_id} {status}")
            html.div(ap.get("hostname", "Unknown"), class_=f"extreme-ap-title-{dashlet_id}")
            html.div(ap.get("site", "N/A"), class_=f"extreme-ap-site-{dashlet_id}")
            html.close_div()
            
            html.open_div(class_=f"extreme-ap-body-{dashlet_id}")
            
            if status == "connected":
                clients = ap.get("clients", 0)
                clients_2_4 = ap.get("clients_2_4", 0)
                clients_5 = ap.get("clients_5", 0)
                
                html.open_div(class_=f"extreme-clients-{dashlet_id}")
                html.div(str(clients), class_=f"extreme-clients-total-{dashlet_id}")
                html.div(f"2.4GHz: {clients_2_4} | 5GHz: {clients_5}", 
                        class_=f"extreme-clients-split-{dashlet_id}")
                html.close_div()
                
                cpu = ap.get("cpu", 0)
                cpu_class = "crit" if cpu > 80 else "warn" if cpu > 60 else "ok"
                
                html.open_div(class_=f"extreme-metric-{dashlet_id}")
                html.open_div(class_=f"extreme-metric-header-{dashlet_id}")
                html.span(_("CPU"))
                html.span(f"{cpu:.0f}%")
                html.close_div()
                html.open_div(class_=f"extreme-progress-{dashlet_id}")
                html.div("", class_=f"extreme-progress-fill-{dashlet_id} {cpu_class}", 
                        style=f"width: {cpu}%")
                html.close_div()
                html.close_div()
                
                memory = ap.get("memory", 0)
                mem_class = "crit" if memory > 80 else "warn" if memory > 60 else "ok"
                
                html.open_div(class_=f"extreme-metric-{dashlet_id}")
                html.open_div(class_=f"extreme-metric-header-{dashlet_id}")
                html.span(_("Memory"))
                html.span(f"{memory:.0f}%")
                html.close_div()
                html.open_div(class_=f"extreme-progress-{dashlet_id}")
                html.div("", class_=f"extreme-progress-fill-{dashlet_id} {mem_class}", 
                        style=f"width: {memory}%")
                html.close_div()
                html.close_div()
            else:
                html.div("⚠️ AP offline", style="text-align: center; padding: 20px; color: #f56565;")
            
            html.close_div()  # body
            html.close_div()  # card
        
        html.close_div()  # grid
        html.close_div()  # container