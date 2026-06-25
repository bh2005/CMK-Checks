#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# comNET GmbH, Simon Haesler (2.1)
# bh2005 (2.4 / 2.5)

from pathlib import Path
import os

from cmk.gui.pages import page_registry, Page, PageEndpoint, PageContext, PageResult
from cmk.gui.htmllib.header import make_header
from cmk.gui.htmllib.html import html
from cmk.gui.http import Request
from cmk.gui.main_menu import main_menu_registry
from cmk.gui.page_menu import PageMenu
from cmk.gui.breadcrumb import Breadcrumb, make_simple_page_breadcrumb
from cmk.utils.paths import default_config_dir
from cmk.gui.utils.urls import urlencode


def _redirect(request: Request, _type: str, host: str, item: str) -> None:
    site = request.get_url_input("site")
    view_name = request.get_url_input("view_name")
    item = urlencode(item)

    if _type == "service":
        url = f'view.py?host={host}&view_name={view_name}&site={site}&service={item}'
    else:
        url = f'view.py?host={host}&view_name={view_name}&site={site}'

    html.javascript(f"let back_link = document.createElement('a');"
                    f"back_link.href = '{url}';"
                    f"back_link.click();")


def _save_custom_notes(_input: str, file: Path) -> None:
    file.write_text(_input.strip())


def _format_item_to_valid_file_name(item: str) -> str:
    return item.replace("/", "_slash_").replace(":", "_colon_")


def _get_notes_file_path_obj(_type: str, host: str, item: str) -> Path:
    if _type == "service":
        return Path(default_config_dir) / "notes/services" / host / item
    else:
        return Path(default_config_dir) / "notes/hosts" / item


def _create_file_dir(file: Path, item: str) -> None:
    segments = list(filter(None, str(file).replace(f"/{item}", "").split("/")))
    for segment in segments:
        if not os.path.isdir(segment):
            os.mkdir(segment)
        os.chdir(segment)


class CustomNotesEditorPage(Page):
    def _page_menu(self, breadcrumb: Breadcrumb) -> PageMenu:
        return PageMenu(dropdowns=[], breadcrumb=breadcrumb)

    def _render(self, request: Request, _type: str, item: str, content: str) -> None:
        title = f"Edit custom notes for {_type} - {item}"
        breadcrumb = make_simple_page_breadcrumb(main_menu_registry.menu_monitoring(), title)
        make_header(html, title, breadcrumb, self._page_menu(breadcrumb))
        html.open_form(
            id_="notes_editor_form",
            name="notes_editor",
            action="",
            method="POST",
        )
        html.text_area("notes_edit_text", content, rows=15, cols=80)
        html.open_p()
        html.input(name="apply_btn", type_="submit", value="Apply", class_="button")
        html.close_p()
        html.close_form()

    def page(self, ctx: PageContext) -> PageResult:
        request = ctx.request
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
            _save_custom_notes(request.get_str_input("notes_edit_text") or "", file)
            _redirect(request, _type, host, item)
        else:
            self._render(request, _type, item, content)

        return None


page_registry.register(PageEndpoint("custom_notes_editor", CustomNotesEditorPage()))
