
# -*- coding: utf-8 -*-
from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    migrate_to_password,
    Password,
    String,
    BooleanChoice,
    Integer,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic

def _parameter_form_xiq():
    return Dictionary(
        title=Title("ExtremeCloud IQ – API Integration"),
        help_text=Help(
            "Dieser Special Agent ruft die ExtremeCloudIQ-REST-API ab und liefert "
            "Daten zu Access Points, Clients, Firmware, Uptime, Locations sowie API-Rate-Limits."
        ),
        elements={
            "url": DictElement(
                parameter_form=String(
                    title=Title("API Base URL"),
                    prefill=DefaultValue("https://api.extremecloudiq.com"),
                ),
            ),
            "username": DictElement(
                parameter_form=String(
                    title=Title("Benutzername"),
                ),
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Passwort"),
                    migrate=migrate_to_password,
                ),
            ),
            "verify_tls": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("TLS-Zertifikate prüfen"),
                    prefill=DefaultValue(True),
                ),
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Timeout (Sekunden)"),
                    prefill=DefaultValue(30),
                ),
            ),
            "proxy_url": DictElement(
                parameter_form=String(
                    title=Title("Proxy Server (optional)"),
                ),
            ),
        },
    )

rule_spec_special_agent_xiq = SpecialAgent(
    name="xiq",
    title=Title("ExtremeCloud IQ new"),
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_xiq,
)
