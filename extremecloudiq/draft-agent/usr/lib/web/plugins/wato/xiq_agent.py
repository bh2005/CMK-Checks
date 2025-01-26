#!/usr/bin/env python3

# XIQ Extreme Cloud settings



from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    Password,
)

def _valuespec_example_rule():
    return Dictionary(
        elements=[
            ("username", TextAscii(title=_("Benutzername"), help=_("Geben Sie den Benutzernamen ein"))),
            ("password", Password(title=_("Passwort"), help=_("Geben Sie das Passwort ein"))),
        ],
        title=_("Benutzername und Passwort"),
        help=_("Konfiguration von Benutzername und Passwort"),
    )

rulespec_registry.register(
    HostRulespec(
        group="datasource_programs",
        name="example_rule",
        valuespec=_valuespec_example_rule,
    )
)