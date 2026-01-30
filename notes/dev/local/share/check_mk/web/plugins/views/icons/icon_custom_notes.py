#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Custom Notes Icon for Burger-Menu (Checkmk 2.4)
#

from cmk.gui.plugins.views.icons import Icon, register_icon
from cmk.gui.utils.urls import makeuri_contextless
from cmk.gui.utils.html import HTML
from cmk.gui.globals import request


@register_icon
class CustomNotesIcon(Icon):
    @staticmethod
    def ident() -> str:
        return "custom_notes_icon"

    def title(self, row, what) -> str:
        return "Edit Notes"

    def icon(self, row, what) -> str:
        # Standard-Icon aus CMK: "comment"
        return "comment"

    def url(self, row, what) -> str:
        host = row.get("host_name", "")
        site = row.get("site", "")
        view_name = self._extract_view_name()

        if what == "service":
            svc = row.get("service_description", "")
            return makeuri_contextless(
                request,
                filename="custom_notes_editor",
                vars_=[
                    ("type", "service"),
                    ("host", host),
                    ("item", svc),
                    ("site", site),
                    ("view_name", view_name),
                ],
            )

        # HOST
        return makeuri_contextless(
            request,
            filename="custom_notes_editor",
            vars_=[
                ("type", "host"),
                ("host", host),
                ("item", host),
                ("site", site),
                ("view_name", view_name),
            ],
        )

    def show(self, row, what) -> bool:
        # Immer anzeigen, sowohl bei Host als auch Service
        return True

    def _extract_view_name(self) -> str:
        url = request.url or ""
        import re

        m = re.search(r"view_name=([^&]+)", url)
        return m.group(1) if m else "allhosts"