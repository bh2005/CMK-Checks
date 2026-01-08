#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check_MK 2.4 Compatible Link Dashlet

Creates clickable links/buttons to other dashboards, external URLs, or views.

Install to: local/lib/check_mk/gui/plugins/dashboard/link_dashlet.py
(Note the different path for CMK 2.4!)
"""

from cmk.gui.i18n import _
from cmk.gui.type_defs import HTTPVariables
from cmk.gui.htmllib.html import html
from cmk.gui.utils.html import HTML
from cmk.gui.valuespec import (
    CascadingDropdown,
    Dictionary,
    DropdownChoice,
    TextInput,
    TextAreaUnicode,
)

try:
    # Check_MK 2.4 API
    from cmk.gui.dashboard.dashlet import Dashlet, dashlet_registry
    from cmk.gui.dashboard.type_defs import DashletConfig, DashletId
except ImportError:
    # Fallback for older versions
    from cmk.gui.plugins.dashboard.utils import Dashlet, dashlet_registry


@dashlet_registry.register
class LinkDashlet(Dashlet):
    """Dashlet that displays a clickable link/button"""

    @classmethod
    def type_name(cls):
        return "link_dashlet"

    @classmethod
    def title(cls):
        return _("Link / Button")

    @classmethod
    def description(cls):
        return _("Clickable link or button to dashboard, view, or URL")

    @classmethod
    def sort_index(cls):
        return 10

    @classmethod
    def initial_size(cls):
        return (20, 10)

    @classmethod
    def is_resizable(cls):
        return True

    @classmethod
    def initial_refresh_interval(cls):
        return False  # No refresh needed

    @classmethod
    def vs_parameters(cls):
        return Dictionary(
            title=_("Properties"),
            render="form",
            optional_keys=["description", "icon"],
            elements=[
                (
                    "link_type",
                    CascadingDropdown(
                        title=_("Link Type"),
                        choices=[
                            (
                                "dashboard",
                                _("Check_MK Dashboard"),
                                TextInput(
                                    title=_("Dashboard Name"),
                                    help=_("Name of the dashboard (from URL: dashboard.py?name=XXX)"),
                                    size=40,
                                ),
                            ),
                            (
                                "view",
                                _("Check_MK View"),
                                TextInput(
                                    title=_("View Name"),
                                    help=_("Name of the view (e.g., allhosts, allservices)"),
                                    size=40,
                                ),
                            ),
                            (
                                "url",
                                _("External URL"),
                                Dictionary(
                                    elements=[
                                        (
                                            "url",
                                            TextInput(
                                                title=_("URL"),
                                                help=_("Full URL (must start with http:// or https://)"),
                                                size=60,
                                            ),
                                        ),
                                        (
                                            "open_new",
                                            DropdownChoice(
                                                title=_("Open in"),
                                                choices=[
                                                    (False, _("Same window")),
                                                    (True, _("New window/tab")),
                                                ],
                                                default_value=True,
                                            ),
                                        ),
                                    ],
                                    optional_keys=[],
                                ),
                            ),
                            (
                                "iframe",
                                _("Embedded (iframe)"),
                                TextInput(
                                    title=_("URL to embed"),
                                    help=_("URL to embed in iframe. Note: Not all sites allow embedding."),
                                    size=60,
                                ),
                            ),
                        ],
                        default_value=("dashboard", "main"),
                    ),
                ),
                (
                    "title",
                    TextInput(
                        title=_("Link Title"),
                        help=_("Text displayed on the button"),
                        size=40,
                        allow_empty=False,
                        default_value="Link",
                    ),
                ),
                (
                    "description",
                    TextAreaUnicode(
                        title=_("Description (optional)"),
                        help=_("Additional text shown below title"),
                        rows=2,
                        cols=40,
                    ),
                ),
                (
                    "style",
                    DropdownChoice(
                        title=_("Display Style"),
                        choices=[
                            ("button", _("Large Button")),
                            ("card", _("Card")),
                            ("minimal", _("Minimal")),
                        ],
                        default_value="button",
                    ),
                ),
                (
                    "icon",
                    DropdownChoice(
                        title=_("Icon"),
                        choices=[
                            ("", _("No icon")),
                            ("📊", "📊 Dashboard"),
                            ("🖥️", "🖥️ Server"),
                            ("📈", "📈 Graph"),
                            ("🔍", "🔍 Search"),
                            ("⚙️", "⚙️ Settings"),
                            ("🌐", "🌐 Network"),
                            ("📡", "📡 Wireless"),
                            ("🚀", "🚀 Launch"),
                            ("⚡", "⚡ Fast"),
                            ("📋", "📋 List"),
                        ],
                        default_value="📊",
                    ),
                ),
                (
                    "color",
                    DropdownChoice(
                        title=_("Color Theme"),
                        choices=[
                            ("blue", _("Blue")),
                            ("green", _("Green")),
                            ("purple", _("Purple")),
                            ("orange", _("Orange")),
                            ("red", _("Red")),
                        ],
                        default_value="blue",
                    ),
                ),
            ],
        )

    def _get_link_data(self):
        """Get URL and target based on configuration"""
        link_config = self._dashlet_spec.get("link_type", ("dashboard", "main"))
        link_type = link_config[0]
        link_value = link_config[1]
        
        if link_type == "dashboard":
            url = f"dashboard.py?name={link_value}"
            target = "_self"
            is_iframe = False
        elif link_type == "view":
            url = f"view.py?view_name={link_value}"
            target = "_self"
            is_iframe = False
        elif link_type == "url":
            url = link_value.get("url", "#")
            target = "_blank" if link_value.get("open_new", True) else "_self"
            is_iframe = False
        elif link_type == "iframe":
            url = link_value
            target = None
            is_iframe = True
        else:
            url = "#"
            target = "_self"
            is_iframe = False
        
        return url, target, is_iframe

    def show(self):
        """Render the dashlet"""
        title = self._dashlet_spec.get("title", "Link")
        description = self._dashlet_spec.get("description", "")
        style = self._dashlet_spec.get("style", "button")
        icon = self._dashlet_spec.get("icon", "")
        color = self._dashlet_spec.get("color", "blue")
        
        url, target, is_iframe = self._get_link_data()
        
        # Color mappings
        color_map = {
            "blue": ("667eea", "764ba2"),
            "green": ("11998e", "38ef7d"),
            "purple": ("a8edea", "fed6e3"),
            "orange": ("f093fb", "f5576c"),
            "red": ("fa709a", "fee140"),
        }
        
        c1, c2 = color_map.get(color, ("667eea", "764ba2"))
        
        # Styles
        html.open_div(style="height: 100%; padding: 0; margin: 0;")
        
        html.write_html(HTML(f"""
        <style>
            .link-dashlet-{self.dashlet_id} {{
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px;
                box-sizing: border-box;
            }}
            .link-dashlet-{self.dashlet_id} a {{
                text-decoration: none;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                padding: 20px;
                border-radius: 12px;
                background: linear-gradient(135deg, #{c1} 0%, #{c2} 100%);
                color: white;
                transition: all 0.3s ease;
                cursor: pointer;
                text-align: center;
                box-sizing: border-box;
            }}
            .link-dashlet-{self.dashlet_id} a:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }}
            .link-dashlet-{self.dashlet_id} .icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .link-dashlet-{self.dashlet_id} .title {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .link-dashlet-{self.dashlet_id} .desc {{
                font-size: 13px;
                opacity: 0.9;
            }}
            .link-dashlet-{self.dashlet_id} iframe {{
                width: 100%;
                height: 100%;
                border: none;
                border-radius: 8px;
            }}
        </style>
        """))
        
        if is_iframe:
            # Render iframe
            html.write_html(HTML(f"""
            <div class="link-dashlet-{self.dashlet_id}" style="padding: 0;">
                <iframe src="{html.attrencode(url)}"></iframe>
            </div>
            """))
        else:
            # Render link/button
            html.open_div(class_=f"link-dashlet-{self.dashlet_id}")
            html.open_a(href=url, target=target if target else None)
            
            if icon:
                html.div(icon, class_="icon")
            html.div(title, class_="title")
            if description:
                html.div(description, class_="desc")
            
            html.close_a()
            html.close_div()
        
        html.close_div()