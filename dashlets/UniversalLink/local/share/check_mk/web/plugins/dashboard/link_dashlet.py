#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check_MK Universal Link Dashlet

Creates clickable links/buttons to other dashboards, external URLs, or views.
Can be styled as button, card, or iframe.

Install to: local/share/check_mk/web/plugins/dashboard/link_dashlet.py
"""

from cmk.gui.i18n import _
from cmk.gui.plugins.dashboard.utils import Dashlet, dashlet_registry
from cmk.gui.htmllib.html import html
from cmk.gui.utils.html import HTML
from cmk.gui.valuespec import (
    Alternative,
    CascadingDropdown,
    Dictionary,
    DropdownChoice,
    FixedValue,
    Integer,
    TextInput,
    TextAreaUnicode,
    Tuple,
)


@dashlet_registry.register
class LinkDashlet(Dashlet):
    """Dashlet that displays a clickable link/button to another dashboard or URL"""

    @classmethod
    def type_name(cls):
        return "link_dashlet"

    @classmethod
    def title(cls):
        return _("Link / Button Dashlet")

    @classmethod
    def description(cls):
        return _("Display a clickable link or button to another dashboard, view, or external URL")

    @classmethod
    def sort_index(cls) -> int:
        return 10

    @classmethod
    def initial_size(cls):
        return (20, 10)  # width, height in grid units

    @classmethod
    def initial_refresh_interval(cls):
        return 0  # No refresh needed for static links

    @classmethod
    def vs_parameters(cls):
        """Configuration options for the dashlet"""
        return Dictionary(
            title=_("Properties"),
            render="form",
            optional_keys=["icon", "background_color", "text_color", "description"],
            elements=[
                (
                    "link_type",
                    CascadingDropdown(
                        title=_("Link Type"),
                        help=_("Choose what type of link to create"),
                        choices=[
                            (
                                "dashboard",
                                _("Internal Dashboard"),
                                Dictionary(
                                    elements=[
                                        (
                                            "dashboard_name",
                                            TextInput(
                                                title=_("Dashboard Name"),
                                                help=_(
                                                    "Name of the dashboard to link to. "
                                                    "Example: main, problems, network_overview"
                                                ),
                                                size=40,
                                            ),
                                        ),
                                    ],
                                    optional_keys=[],
                                ),
                            ),
                            (
                                "view",
                                _("Internal View"),
                                Dictionary(
                                    elements=[
                                        (
                                            "view_name",
                                            TextInput(
                                                title=_("View Name"),
                                                help=_(
                                                    "Name of the view to link to. "
                                                    "Example: allhosts, services, host"
                                                ),
                                                size=40,
                                            ),
                                        ),
                                    ],
                                    optional_keys=[],
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
                                                help=_(
                                                    "Full URL to link to. "
                                                    "Example: https://monitoring.company.com/grafana"
                                                ),
                                                size=60,
                                                regex="^https?://.*",
                                                regex_error=_("URL must start with http:// or https://"),
                                            ),
                                        ),
                                        (
                                            "open_in",
                                            DropdownChoice(
                                                title=_("Open in"),
                                                choices=[
                                                    ("same", _("Same window")),
                                                    ("new", _("New window/tab")),
                                                ],
                                                default_value="new",
                                            ),
                                        ),
                                    ],
                                    optional_keys=[],
                                ),
                            ),
                            (
                                "iframe",
                                _("Embedded iframe"),
                                Dictionary(
                                    elements=[
                                        (
                                            "url",
                                            TextInput(
                                                title=_("URL"),
                                                help=_(
                                                    "URL to embed in iframe. "
                                                    "Note: Some sites prevent iframe embedding."
                                                ),
                                                size=60,
                                            ),
                                        ),
                                    ],
                                    optional_keys=[],
                                ),
                            ),
                        ],
                        default_value="dashboard",
                    ),
                ),
                (
                    "title",
                    TextInput(
                        title=_("Link Title"),
                        help=_("Text displayed on the button/link"),
                        size=40,
                        allow_empty=False,
                    ),
                ),
                (
                    "description",
                    TextAreaUnicode(
                        title=_("Description (optional)"),
                        help=_("Additional description text shown below the title"),
                        rows=2,
                        cols=40,
                    ),
                ),
                (
                    "style",
                    DropdownChoice(
                        title=_("Display Style"),
                        help=_("How to display the link"),
                        choices=[
                            ("button", _("Large Button")),
                            ("card", _("Card with shadow")),
                            ("minimal", _("Minimal link")),
                            ("badge", _("Badge/Tag style")),
                        ],
                        default_value="button",
                    ),
                ),
                (
                    "icon",
                    DropdownChoice(
                        title=_("Icon (optional)"),
                        help=_("Select an icon to display"),
                        choices=[
                            ("", _("No icon")),
                            ("📊", _("📊 Chart/Dashboard")),
                            ("🖥️", _("🖥️ Server/Computer")),
                            ("📈", _("📈 Graph/Trending")),
                            ("🔍", _("🔍 Search/View")),
                            ("⚙️", _("⚙️ Settings")),
                            ("📱", _("📱 Mobile/Device")),
                            ("🌐", _("🌐 Network/Globe")),
                            ("📡", _("📡 Signal/Wireless")),
                            ("🚀", _("🚀 Rocket/Launch")),
                            ("⚡", _("⚡ Lightning/Fast")),
                            ("🎯", _("🎯 Target/Focus")),
                            ("📋", _("📋 List/Document")),
                            ("🔔", _("🔔 Notification")),
                            ("👥", _("👥 Users/Team")),
                            ("🏢", _("🏢 Building")),
                        ],
                        default_value="📊",
                    ),
                ),
                (
                    "background_color",
                    DropdownChoice(
                        title=_("Background Color"),
                        choices=[
                            ("blue", _("Blue")),
                            ("green", _("Green")),
                            ("purple", _("Purple")),
                            ("orange", _("Orange")),
                            ("red", _("Red")),
                            ("gray", _("Gray")),
                            ("gradient-blue", _("Gradient Blue")),
                            ("gradient-green", _("Gradient Green")),
                            ("gradient-purple", _("Gradient Purple")),
                            ("gradient-orange", _("Gradient Orange")),
                        ],
                        default_value="gradient-blue",
                    ),
                ),
                (
                    "text_color",
                    DropdownChoice(
                        title=_("Text Color"),
                        choices=[
                            ("white", _("White")),
                            ("black", _("Black")),
                            ("gray", _("Gray")),
                        ],
                        default_value="white",
                    ),
                ),
            ],
        )

    def _get_link_url(self):
        """Generate the URL based on link type"""
        link_config = self._dashlet_spec.get("link_type", ("dashboard", {}))
        link_type = link_config[0]
        link_data = link_config[1]
        
        if link_type == "dashboard":
            dashboard_name = link_data.get("dashboard_name", "main")
            return f"dashboard.py?name={dashboard_name}", "same"
        
        elif link_type == "view":
            view_name = link_data.get("view_name", "allhosts")
            return f"view.py?view_name={view_name}", "same"
        
        elif link_type == "url":
            url = link_data.get("url", "#")
            open_in = link_data.get("open_in", "new")
            return url, open_in
        
        elif link_type == "iframe":
            return None, None  # iframe handled separately
        
        return "#", "same"

    def show(self):
        """Render the dashlet"""
        title = self._dashlet_spec.get("title", "Link")
        description = self._dashlet_spec.get("description", "")
        style = self._dashlet_spec.get("style", "button")
        icon = self._dashlet_spec.get("icon", "")
        bg_color = self._dashlet_spec.get("background_color", "gradient-blue")
        text_color = self._dashlet_spec.get("text_color", "white")
        
        link_config = self._dashlet_spec.get("link_type", ("dashboard", {}))
        link_type = link_config[0]
        
        # CSS Styles
        html.write_html(HTML("""
        <style>
            .link-dashlet-container {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px;
            }
            .link-dashlet-button {
                text-decoration: none;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                padding: 20px;
                border-radius: 12px;
                transition: all 0.3s ease;
                cursor: pointer;
                text-align: center;
            }
            .link-dashlet-button:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }
            .link-dashlet-card {
                text-decoration: none;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                cursor: pointer;
                text-align: center;
                background: white;
            }
            .link-dashlet-card:hover {
                box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            }
            .link-dashlet-minimal {
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 15px;
                border-radius: 6px;
                transition: all 0.2s ease;
                cursor: pointer;
            }
            .link-dashlet-minimal:hover {
                background: rgba(0,0,0,0.05);
            }
            .link-dashlet-badge {
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: 600;
                transition: all 0.2s ease;
                cursor: pointer;
            }
            .link-dashlet-badge:hover {
                transform: scale(1.05);
            }
            .link-dashlet-icon {
                font-size: 48px;
                margin-bottom: 10px;
            }
            .link-dashlet-icon-small {
                font-size: 24px;
            }
            .link-dashlet-title {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .link-dashlet-title-small {
                font-size: 16px;
                font-weight: 600;
            }
            .link-dashlet-description {
                font-size: 13px;
                opacity: 0.9;
                margin-top: 5px;
            }
            
            /* Colors */
            .bg-blue { background: #3b82f6; }
            .bg-green { background: #10b981; }
            .bg-purple { background: #8b5cf6; }
            .bg-orange { background: #f59e0b; }
            .bg-red { background: #ef4444; }
            .bg-gray { background: #6b7280; }
            .bg-gradient-blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .bg-gradient-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
            .bg-gradient-purple { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
            .bg-gradient-orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            
            .text-white { color: white; }
            .text-black { color: #1f2937; }
            .text-gray { color: #6b7280; }
            
            .link-dashlet-iframe {
                width: 100%;
                height: 100%;
                border: none;
                border-radius: 8px;
            }
        </style>
        """))
        
        # Render based on link type
        if link_type == "iframe":
            # Iframe embed
            iframe_url = link_config[1].get("url", "")
            html.open_div(style="height: 100%;")
            html.write_html(HTML(f'<iframe src="{html.attrencode(iframe_url)}" class="link-dashlet-iframe"></iframe>'))
            html.close_div()
        else:
            # Regular link/button
            url, target = self._get_link_url()
            target_attr = '_blank' if target == 'new' else '_self'
            
            html.open_div(class_="link-dashlet-container")
            
            if style == "button":
                # Large button style
                html.open_a(
                    href=url,
                    target=target_attr,
                    class_=f"link-dashlet-button bg-{bg_color} text-{text_color}"
                )
                if icon:
                    html.div(icon, class_="link-dashlet-icon")
                html.div(title, class_="link-dashlet-title")
                if description:
                    html.div(description, class_="link-dashlet-description")
                html.close_a()
                
            elif style == "card":
                # Card style
                html.open_a(
                    href=url,
                    target=target_attr,
                    class_="link-dashlet-card"
                )
                if icon:
                    html.div(icon, class_="link-dashlet-icon")
                html.div(title, class_=f"link-dashlet-title text-{text_color if text_color != 'white' else 'black'}")
                if description:
                    html.div(description, class_=f"link-dashlet-description text-gray")
                html.close_a()
                
            elif style == "minimal":
                # Minimal link style
                html.open_a(
                    href=url,
                    target=target_attr,
                    class_=f"link-dashlet-minimal text-{text_color if text_color != 'white' else 'black'}"
                )
                if icon:
                    html.span(icon, class_="link-dashlet-icon-small")
                html.open_div()
                html.div(title, class_="link-dashlet-title-small")
                if description:
                    html.div(description, style="font-size: 12px; color: #6b7280;")
                html.close_div()
                html.close_a()
                
            elif style == "badge":
                # Badge style
                html.open_a(
                    href=url,
                    target=target_attr,
                    class_=f"link-dashlet-badge bg-{bg_color} text-{text_color}"
                )
                if icon:
                    html.span(icon, class_="link-dashlet-icon-small")
                html.span(title, style="font-size: 14px;")
                html.close_a()
            
            html.close_div()