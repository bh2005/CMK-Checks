#!/usr/bin/env python3
# -*- mode: Python; encoding: utf-8; indent-offset: 4; autowrap: nil -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    PasswordSpec,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    HostRulespec,
)

from cmk.gui.plugins.wato.datasource_programs import (
    RulespecGroupDatasourcePrograms,
)

def _valuespec_special_agents_my_rest_api():
    return Dictionary(
        elements=[
            ("uid", TextAscii(title=_("Username"), allow_empty=False)),
            ("pwd", PasswordSpec(title=_("Password"), allow_empty=False, hidden=True)),
            ("url, TextAscii(title=_("URL"), allow_empty=False)),
        ],
        optional_keys=False,
        title=_("REST Parameters"),
    )

rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourcePrograms,
        name="special_agents:my_rest_api",
        valuespec=_valuespec_special_agents_my_rest_api,
    ))