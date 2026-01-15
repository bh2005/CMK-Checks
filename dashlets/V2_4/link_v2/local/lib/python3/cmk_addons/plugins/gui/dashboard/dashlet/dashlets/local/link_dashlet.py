#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkDashlet – Checkmk 2.4.0p2 (CEE)

Erzeugt klickbare Links/Buttons zu Dashboards, Views, externen URLs oder bettet
 eine URL als <iframe> ein.

Kombiniertes Icon-Konzept:
 - icon_mode: "emoji" | "theme" | "custom" | "css"
 - theme_icon_path: Bild relativ zum Web-Root (Option A / Theme-Asset)
 - custom_icon_file: Bild unter images/icons/...
 - icon_class: CSS-Iconklasse (z. B. aus einer mitgelieferten icons.css)

Ablageort (CMK >= 2.4):
  ~/local/lib/python3/cmk_addons/plugins/gui/dashboard/dashlet/dashlets/link_dashlet.py
"""
from __future__ import annotations

from cmk.gui.i18n import _
from cmk.gui.htmllib.html import html
from cmk.gui.utils.html import HTML
from cmk.gui.valuespec import (
    CascadingDropdown,
    Dictionary,
    DropdownChoice,
    TextInput,
    TextAreaUnicode,
)
from cmk.gui.dashboard.dashlet.base import Dashlet
from cmk.gui.dashboard.type_defs import DashletConfig, DashletSize


class LinkDashletConfig(DashletConfig):
    pass


class LinkDashlet(Dashlet[LinkDashletConfig]):
    # --- Identity -----------------------------------------------------------
    @classmethod
    def type_name(cls) -> str:
        return "link_dashlet"

    @classmethod
    def title(cls) -> str:
        return _("Link / Button")

    @classmethod
    def description(cls) -> str:
        return _("Clickable link or button to dashboard, view, or URL")

    @classmethod
    def sort_index(cls) -> int:
        return 10

    @classmethod
    def initial_size(cls) -> DashletSize:
        return (20, 10)

    @classmethod
    def initial_refresh_interval(cls) -> int:
        return 0  # kein Auto-Refresh

    # --- Parameter-Dialog ---------------------------------------------------
    @classmethod
    def vs_parameters(cls):
        return Dictionary(
            title=_("Properties"),
            render="form",
            optional_keys=["link_description", "link_icon"],
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
                                                choices=[(False, _("Same window")), (True, _("New window/tab"))],
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
                    "link_title",
                    TextInput(
                        title=_("Link Title"),
                        help=_("Text displayed on the button"),
                        size=40,
                        allow_empty=False,
                        default_value="Link",
                    ),
                ),
                (
                    "link_description",
                    TextAreaUnicode(
                        title=_("Description (optional)"),
                        help=_("Additional text shown below title"),
                        rows=2,
                        cols=40,
                    ),
                ),
                (
                    "link_style",
                    DropdownChoice(
                        title=_("Display Style"),
                        choices=[("button", _("Large Button")), ("card", _("Card")), ("minimal", _("Minimal"))],
                        default_value="button",
                    ),
                ),

                # -------------------- Icon-Abschnitt (kombiniert) --------------------
                (
                    "icon_mode",
                    DropdownChoice(
                        title=_("Icon mode"),
                        choices=[
                            ("theme",  _("Theme image (recommended)")),
                            ("emoji",  _("Emoji")),
                            ("custom", _("Custom image (images/icons)")),
                            ("css",    _("CSS icon class")),
                        ],
                        default_value="theme",
                    ),
                ),
                (
                    "link_icon",  # Emoji
                    TextInput(title=_("Emoji (fallback)"), size=10, default_value="📊"),
                ),
                (
                    "theme_icon_path",
                    TextInput(
                        title=_("Theme image path"),
                        help=_("Relative to web root, e.g. 'themes/modern-dark/images/myicon.svg'"),
                        size=80,
                    ),
                ),
                (
                    "custom_icon_file",
                    TextInput(
                        title=_("Custom image path"),
                        help=_("e.g. 'images/icons/my_icon.svg'"),
                        size=80,
                    ),
                ),
                (
                    "icon_class",
                    TextInput(
                        title=_("CSS icon class"),
                        help=_("If 'css' mode, e.g. gg-dashboard (if you ship a CSS icon set)"),
                        size=40,
                    ),
                ),

                (
                    "link_color",
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

    # --- Link-Auflösung -----------------------------------------------------
    def _get_link_data(self) -> tuple[str, str | None, bool]:
        link_config = self._dashlet_spec.get("link_type", ("dashboard", "main"))
        link_type, link_value = link_config[0], link_config[1]

        if link_type == "dashboard":
            return f"dashboard.py?name={link_value}", "_self", False
        if link_type == "view":
            return f"view.py?view_name={link_value}", "_self", False
        if link_type == "url":
            url = link_value.get("url", "#") if isinstance(link_value, dict) else "#"
            tgt = "_blank" if isinstance(link_value, dict) and link_value.get("open_new", True) else "_self"
            return url, tgt, False
        if link_type == "iframe":
            return str(link_value), None, True
        return "#", "_self", False

    # --- Rendering ----------------------------------------------------------
    def show(self) -> None:
        title = self._dashlet_spec.get("link_title", "Link")
        description = self._dashlet_spec.get("link_description", "")
        style = self._dashlet_spec.get("link_style", "button")
        color = self._dashlet_spec.get("link_color", "blue")
        icon_mode = self._dashlet_spec.get("icon_mode", "theme")

        url, target, is_iframe = self._get_link_data()

        color_map = {
            "blue": ("667eea", "764ba2"),
            "green": ("11998e", "38ef7d"),
            "purple": ("a8edea", "fed6e3"),
            "orange": ("f093fb", "f5576c"),
            "red": ("fa709a", "fee140"),
        }
        c1, c2 = color_map.get(color, ("667eea", "764ba2"))

        html.open_div(style="height: 100%; padding: 0; margin: 0;")

        # Scoped CSS pro Dashlet-ID
        html.write_html(f"""
        <style>
            .link-dashlet-{self._dashlet_id} {{
                height: 100%; display:flex; align-items:center; justify-content:center;
                padding:20px; box-sizing:border-box; font-family:inherit;
            }}
            .link-dashlet-{self._dashlet_id} a {{
                text-decoration:none; color:white; display:flex; flex-direction:column;
                align-items:center; justify-content:center; width:100%; height:100%;
                border-radius:12px; background:linear-gradient(135deg, #{c1} 0%, #{c2} 100%);
                transition:all .3s ease; box-sizing:border-box; text-align:center;
            }}
            .link-dashlet-{self._dashlet_id} a:hover {{
                transform: translateY(-6px); box-shadow:0 12px 25px rgba(0,0,0,.25);
            }}
            .link-dashlet-{self._dashlet_id} .icon {{ margin-bottom:12px; font-size:48px; }}
            .link-dashlet-{self._dashlet_id} .title {{ font-weight:bold; margin-bottom:6px; }}
            .link-dashlet-{self._dashlet_id} .desc {{ font-size:13px; opacity:.9; line-height:1.3; }}

            .style-button a {{ padding:30px; font-size:22px; box-shadow:0 8px 20px rgba(0,0,0,.2); }}
            .style-button .title {{ font-size:24px; }}
            .style-button .icon  {{ font-size:60px; }}

            .style-card a {{ padding:20px; box-shadow:0 6px 15px rgba(0,0,0,.15); border:1px solid rgba(255,255,255,.2); }}
            .style-card .title {{ font-size:20px; }}
            .style-card .icon  {{ font-size:50px; }}

            .style-minimal a {{ background:none!important; color:#333!important; padding:10px; border-radius:8px; }}
            .style-minimal a:hover {{ background:rgba(0,0,0,.05)!important; transform:none; box-shadow:none; }}
            .style-minimal .icon  {{ font-size:32px; margin-bottom:8px; }}
            .style-minimal .title {{ font-size:16px; color:#333; }}
            .style-minimal .desc  {{ font-size:12px; color:#666; }}

            .link-dashlet-{self._dashlet_id} iframe {{ width:100%; height:100%; border:none; border-radius:8px; }}
            .link-dashlet-{self._dashlet_id} img.icon-img {{ max-width:72px; max-height:72px; margin-bottom:12px; }}
            .style-minimal img.icon-img {{ max-width:40px; max-height:40px; }}
        </style>
        """)

        # Falls CSS-Iconklasse genutzt werden soll, stylesheet referenzieren
        if icon_mode == "css":
            html.write_html('<link rel="stylesheet" href="skin/css/icons.css">')

        if is_iframe:
            html.write_html(HTML(
                f'<div class="link-dashlet-{self._dashlet_id}" style="padding:0;">'
                f'  <iframe src="{html.attrencode(url)}" allowfullscreen></iframe>'
                f'</div>'
            ))
            html.close_div()
            return

        style_class = f"style-{style}"
        html.open_div(class_=f"link-dashlet-{self._dashlet_id} {style_class}")
        html.open_a(href=url, target=target if target else None)

        # Icon-Rendering je Modus
        if icon_mode == "emoji":
            emoji = self._dashlet_spec.get("link_icon", "")
            if emoji:
                html.div(emoji, class_="icon")
        elif icon_mode == "theme":
            path = self._dashlet_spec.get("theme_icon_path", "")
            if path:
                html.write_html(f'<img class="icon-img" src="{html.attrencode(path)}" alt="">')
        elif icon_mode == "custom":
            path = self._dashlet_spec.get("custom_icon_file", "")
            if path:
                html.write_html(f'<img class="icon-img" src="{html.attrencode(path)}" alt="">')
        elif icon_mode == "css":
            clazz = self._dashlet_spec.get("icon_class", "")
            if clazz:
                html.write_html(f'<span class="{html.attrencode(clazz)} icon" aria-hidden="true"></span>')

        # Text
        html.div(self._dashlet_spec.get("link_title", "Link"), class_="title")
        desc = self._dashlet_spec.get("link_description", "")
        if desc:
            html.div(desc, class_="desc")

        html.close_a()
        html.close_div()
        html.close_div()
