# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Ruleset for RAPID Server Special Agent
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Based on Redfish ruleset by Andreas Doehler (Yogibaer75)

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    Password,
    Checkbox,
)
from cmk.gui.plugins.wato import (
    RulespecGroupCheckParametersApplications,
    register_check_parameters,
)

def _parameter_valuespec_rapid():
    return Dictionary(
        elements=[
            ("host", 
             TextInput(
                 title=_("RAPID Server Host"),
                 help=_("Hostname or IP address of the RAPID Server"),
                 allow_empty=False,
             )),
            ("username",
             TextInput(
                 title=_("Username"),
                 help=_("API username for RAPID Server"),
                 allow_empty=False,
             )),
            ("password",
             Password(
                 title=_("Password"),
                 help=_("API password for RAPID Server"),
                 allow_empty=False,
             )),
            ("no_cert_check",
             Checkbox(
                 title=_("Disable SSL verification"),
                 label=_("Disable SSL certificate verification"),
                 default_value=False,
             )),
        ],
        required_keys=["host", "username", "password"],
        title=_("RAPID Server Parameters"),
    )

register_check_parameters(
    RulespecGroupCheckParametersApplications,
    "rapid",
    _("RAPID Server Special Agent"),
    _parameter_valuespec_rapid,
    match_type="dict",
)
