#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
from cmk.gui.config import Config
from cmk.gui.htmllib.html import html
from cmk.gui.http import request
from cmk.gui.painter.v0.painters import match_path_entries_with_item
from cmk.gui.painter.v0 import painters
from cmk.gui.type_defs import Row
from cmk.gui.utils.html import HTML
from cmk.gui.utils.urls import makeuri_contextless
from cmk.gui.view_utils import CellSpec
from cmk.utils.paths import default_config_dir
from cmk.gui.sites import get_site_config

def _get_back_url_data(row):
    url = request.url
    view_name = str(re.findall(r"view_name=\w+", url)[0]).replace("view_name=", "")
    return {
        "site": row["site"],
        "view_name": view_name
    }

def _render_edit_icon_button(data: dict):
    url = makeuri_contextless(request,
                              filename="custom_notes_editor.py",
                              vars_=[
                                     ("type", data.get("type")),
                                     ("item", data.get("item")),
                                     ("host", data.get("host")),
                                     ("site", data.get("site")),
                                     ("view_name", data.get("view_name"))
                                    ]
                              )
    return html.render_a(
        content=HTML(html.render_icon("edit", cssclass="iconbutton"), escape=False),
        href=url,
        target="main",
        title="Edit custom notes",
    )

def _format_item_to_valid_file_name(item: str):
    return item.replace("/", "_slash_").replace(":", "_colon_")


def _my_paint_custom_notes(what: str, row: Row,  config: Config) -> CellSpec:
    host = row["host_name"]
    svc = row.get("service_description")
    if what == "service":
        notes_dir = default_config_dir + "/notes/services"
        dirs = match_path_entries_with_item([Path(notes_dir)], host)
        item = svc
    else:
        dirs = [Path(default_config_dir) / "notes/hosts"]
        item = host
    assert isinstance(item, str)
    item_ = _format_item_to_valid_file_name(item)
    files = sorted(match_path_entries_with_item(dirs, item_), reverse=True)
    contents = []

    def replace_tags(text: str) -> str:
        sitename = row["site"]
        url_prefix = get_site_config(config, sitename)["url_prefix"]
        return (
            text.replace("$URL_PREFIX$", url_prefix)
            .replace("$SITE$", sitename)
            .replace("$HOSTNAME$", host)
            .replace("$HOSTNAME_LOWER$", host.lower())
            .replace("$HOSTNAME_UPPER$", host.upper())
            .replace("$HOSTNAME_TITLE$", host[0].upper() + host[1:].lower())
            .replace("$HOSTADDRESS$", row["host_address"])
            .replace("$SERVICEOUTPUT$", row.get("service_plugin_output", ""))
            .replace("$HOSTOUTPUT$", row.get("host_plugin_output", ""))
            .replace("$SERVICEDESC$", row.get("service_description", ""))
        )

    for f in files:
        contents.append(replace_tags(f.read_text(encoding="utf8").strip()))
    data = {
        "type": what,
        "item": item,
        "host": host,
    }
    data.update(_get_back_url_data(row))
    return "", _render_edit_icon_button(data) + "<hr>".join(contents)


painters._paint_custom_notes = _my_paint_custom_notes