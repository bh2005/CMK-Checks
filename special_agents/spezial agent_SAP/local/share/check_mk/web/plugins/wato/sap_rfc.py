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

def _valuespec_special_agents_spa_rfc():
    return Dictionary(
        elements=[
            ("ashost", TextAscii(title=_("Hostname"), allow_empty=False)),
            ("sysnr", TextAscii(title=_("System No"), allow_empty=False)),
            ("client", TextAscii(title=_("Client No"), allow_empty=False)),
            ("user", TextAscii(title=_("User"), allow_empty=False)),           
            ("passwd", PasswordSpec(title=_("Password"), allow_empty=False, hidden=True)),
            ("function_module", TextAscii(title=_("Function Module"), allow_empty=False)),            
        ],
        optional_keys=False,
        title=_("Connection Parameters"),
    )

rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourcePrograms,
        name="special_agents:sap_rfc",
        valuespec=_valuespec_special_agents_sap_rfc,
    ))
    