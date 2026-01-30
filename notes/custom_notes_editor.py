#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 11.11.2022, comNET GmbH, Simon Haesler

from pathlib import Path
import os
from cmk.gui.pages import page_registry, Page
from cmk.gui.htmllib.header import make_header
from cmk.gui.htmllib.html import html
from cmk.gui.http import request
from cmk.gui.main_menu import mega_menu_registry
from cmk.gui.page_menu import PageMenu
from cmk.gui.breadcrumb import Breadcrumb, make_simple_page_breadcrumb
from cmk.utils.paths import default_config_dir
from cmk.gui.utils.urls import urlencode


def _redirect(_type, host, item):
    site = request.get_url_input("site")
    view_name = request.get_url_input("view_name")
    
    # Build URL based on type
    if _type == "service":
        # For services: include service parameter
        item_encoded = urlencode(item)
        url = f'view.py?view_name={view_name}&site={site}&host={host}&service={item_encoded}'
    else:
        # For hosts: just host parameter
        url = f'view.py?view_name={view_name}&site={site}&host={host}'
    
    # JavaScript redirect
    html.javascript(f"window.location.href = '{url}';")


def _save_custom_notes(_input: str, file: Path):
    file.write_text(_input.strip())


def _format_item_to_valid_file_name(item: str):
    return item.replace("/", "_slash_").replace(":", "_colon_")


def _get_notes_file_path_obj(_type: str, host: str, item: str):
    if _type == "service":
        return Path(default_config_dir) / "notes/services" / host / item
    else:
        # FIX: Use host instead of item for host notes
        return Path(default_config_dir) / "notes/hosts" / host


def _create_file_dir(file: Path, item: str):
    segments = list(filter(None, str(file).replace(f"/{item}", "").split("/")))
    for segment in segments:
        if not os.path.isdir(segment):
            os.mkdir(segment)
        os.chdir(segment)


@page_registry.register_page("custom_notes_editor")
class CustomNotesEditorPage(Page):
    def _page_menu(self, breadcrumb: Breadcrumb) -> PageMenu:
        return PageMenu(dropdowns=[], breadcrumb=breadcrumb)

    def _render(self, _type: str, item: str, content: str):
        title = f"Edit custom notes for {_type} - {item}"
        breadcrumb = make_simple_page_breadcrumb(mega_menu_registry.menu_monitoring(), title)
        make_header(html, title, breadcrumb, self._page_menu(breadcrumb))
        html.open_form(
            id_="notes_editor_from",
            name="notes_editor",
            action="",
            method="POST",
        )
        html.text_input("notes_edit_text",
                        type_="textarea",
                        size=33,
                        default_value=content)
        html.button(
            varname="apply_btn",
            title="Apply"
        )
        html.end_form()

    def page(self):
        host = request.get_url_input("host")
        _type = request.get_url_input("type")
        item = request.get_url_input("item")
        item_ = _format_item_to_valid_file_name(item)
        file = _get_notes_file_path_obj(_type, host, item_)
        content = ""
        if file.exists():
            content = file.read_text(encoding="utf8").strip()
        else:
            _create_file_dir(file, item_)
            file.touch()
        if request.has_var("apply_btn"):
            _save_custom_notes(request.get_str_input("notes_edit_text"), file)
            _redirect(_type, host, item)
        else:
            self._render(_type, item, content)