# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Ruleset for Kisters REST API Check
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Based on https://github.com/bh2005/CMK-Checks/blob/master/kisters/rest-check.py

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Checkbox,
    Dictionary,
    Float,
    HTTPUrl,
    ListOf,
    TextInput,
    Tuple,
)
from cmk.gui.plugins.wato import (
    RulespecGroupCheckParametersApplications,
    register_check_parameters,
)

def _parameter_valuespec_kisters_rest_check():
    """Define parameters for Kisters REST API Check."""
    return Dictionary(
        title=_("Kisters REST API Check"),
        elements=[
            (
                "endpoints",
                ListOf(
                    valuespec=Dictionary(
                        elements=[
                            ("instance", TextInput(title=_("Instance name"), allow_empty=False)),
                            ("url", HTTPUrl(title=_("URL"), allow_empty=False)),
                            ("method", TextInput(title=_("HTTP Method"), default_value="GET")),
                            ("data", TextInput(title=_("POST Data"), allow_empty=True)),
                            ("user", TextInput(title=_("Username"), allow_empty=False)),
                            (
                                "password_id",
                                TextInput(title=_("Password ID (from password store)"), allow_empty=False),
                            ),
                            (
                                "pvId",
                                TextInput(title=_("Parameter ID (pvId)"), allow_empty=False),
                            ),
                        ],
                        optional_keys=["method", "data", "user", "password_id", "pvId"],
                    ),
                    title=_("REST API Endpoints"),
                    help=_("Configure REST API endpoints with instance names, URLs, methods, and optional pvId."),
                ),
            ),
            (
                "response_time",
                Tuple(
                    title=_("Response Time Thresholds"),
                    elements=[
                        Float(title=_("Warning at"), unit="s", default_value=1.0),
                        Float(title=_("Critical at"), unit="s", default_value=2.0),
                    ],
                ),
            ),
        ],
        optional_keys=["endpoints", "response_time"],
    )

register_check_parameters(
    RulespecGroupCheckParametersApplications,
    "kisters_rest_check",
    _("Kisters REST API Check"),
    _parameter_valuespec_kisters_rest_check,
    match_type="dict",
)