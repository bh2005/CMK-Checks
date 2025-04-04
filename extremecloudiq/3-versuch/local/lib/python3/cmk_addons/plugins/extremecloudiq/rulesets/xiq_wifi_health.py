#!/usr/bin/env python3
# Shebang needed only for editors
from cmk.rulesets.v1.form_specs import Dictionary, DictElement, Text, String, Password, migrate_to_password
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic, Help, Title, DefaultValue

def _formspec():
    return Dictionary(
        title=Title("ExtremeCloud IQ Wi-Fi Health"),
        help_text=Help("This rule is used to configure parameters for the ExtremeCloud IQ Wi-Fi health agent."),
        elements={
            "xiq_base_url": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("ExtremeCloud IQ Base URL"),
                    prefill=DefaultValue("https://api.extremecloudiq.com"),
                ),
            ),
            "user": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Username for ExtremeCloud IQ API"),
                    prefill=DefaultValue("admin@example.com"),
                ),
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Password for ExtremeCloud IQ API"),
                    migrate=migrate_to_password,
                ),
            ),
            "location_id": DictElement(
                required=True,
                parameter_form=Text(
                    title=Title("Location ID"),
                ),
            ),
        }
    )

rule_spec_xiq_wifi_health = SpecialAgent(
    topic=Topic.NETWORK,
    name="xiq_wifi_health",
    title=Title("ExtremeCloud IQ Wi-Fi Health"),
    parameter_form=_formspec
)