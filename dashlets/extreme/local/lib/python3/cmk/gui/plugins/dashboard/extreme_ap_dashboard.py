#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CMK 2.5: IFrameDashlet + separate Page (extreme_ap_content.py)
# show() is gone in CMK 2.5 — content is served by the page endpoint.
# When adding the dashlet, set URL to:
#   ../check_mk/extreme_ap_content.py?filter_site=all&max_aps=20

from cmk.gui.dashboard import dashlet_registry
from cmk.gui.dashboard.dashlet.base import IFrameDashlet, RelativeLayoutConstraints, WidgetSize
from cmk.gui.dashboard.type_defs import DashletConfig
from cmk.gui.i18n import _


class ExtremeAPDashletConfig(DashletConfig):
    url: str


class ExtremeAPDashlet(IFrameDashlet[ExtremeAPDashletConfig]):
    """Extreme AP Overview dashlet (CMK 2.5).

    Renders via IFrame. Point URL to:
      ../check_mk/extreme_ap_content.py?filter_site=all&max_aps=20
    """

    @classmethod
    def type_name(cls) -> str:
        return "extreme_ap_overview"

    @classmethod
    def title(cls) -> str:
        return _("Extreme Access Points Overview")

    @classmethod
    def description(cls) -> str:
        return _(
            "Shows statistics and status of all Extreme Cloud IQ Access Points. "
            "Set URL to: ../check_mk/extreme_ap_content.py?filter_site=all&max_aps=20"
        )

    @classmethod
    def sort_index(cls) -> int:
        return 50

    @classmethod
    def relative_layout_constraints(cls) -> RelativeLayoutConstraints:
        return RelativeLayoutConstraints(initial_size=WidgetSize(width=60, height=40))


dashlet_registry.register(ExtremeAPDashlet)
