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
    Integer,
    CascadingDropdown,
)

def _valuespec_example_rule():
    return Dictionary(
        title=_("Benutzername und Passwort"),
        help=_("Konfiguration von Benutzername, Passwort, API-URL und Port"),
        elements=[
            ("username", TextAscii(title=_("Benutzername"), help=_("Geben Sie den Benutzernamen ein"))),
            ("password", Password(title=_("Passwort"), help=_("Geben Sie das Passwort ein"))),
            ("api_settings", CascadingDropdown(
                title=_("API-Einstellungen"),
                choices=[
                    ("default", _("Standard-API-Einstellungen"), Dictionary(
                        elements=[
                            ("url", TextAscii(
                                title=_("API URL"),
                                help=_("Die URL der API (Standard: https://api.extremecloudiq.com)"),
                                default_value="https://api.extremecloudiq.com",
                            )),
                            ("port", Integer(
                                title=_("Port"),
                                help=_("Der Port für die API (Standard: 443)"),
                                default_value=443,
                                minvalue=1,
                                maxvalue=65535,
                            )),
                        ],
                    )),
                    ("custom", _("Benutzerdefinierte Einstellungen"), Dictionary(
                        elements=[
                            ("url", TextAscii(
                                title=_("API URL"),
                                help=_("Die URL der API"),
                                allow_empty=False,
                            )),
                            ("port", Integer(
                                title=_("Port"),
                                help=_("Der Port für die API"),
                                default_value=443,
                                minvalue=1,
                                maxvalue=65535,
                            )),
                        ],
                    )),
                ],
                default_value="default",
            )),
        ],
    )

rulespec_registry.register(
    HostRulespec(
        group="datasource_programs",
        name="example_rule",
        valuespec=_valuespec_example_rule,
    )
)