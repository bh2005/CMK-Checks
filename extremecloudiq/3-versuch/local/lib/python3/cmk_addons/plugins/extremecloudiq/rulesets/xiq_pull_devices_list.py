#!/usr/bin/env python3
# Shebang needed only for editors
from cmk.rulesets.v1.form_specs import Dictionary, DictElement, Integer, Choice, Text, String, Password, migrate_to_password
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic, Help, Title, DefaultValue

def _formspec():
    return Dictionary(
        title=Title("ExtremeCloud IQ Device List"),
        help_text=Help("This rule is used to configure parameters for the ExtremeCloud IQ device list agent."),
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
            "page": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Page Number"),
                    default=1,
                ),
            ),
            "limit": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Limit"),
                    default=100,
                ),
            ),
            "sort": DictElement(
                required=False,
                parameter_form=Text(
                    title=Title("Sort Field"),
                ),
            ),
            "dir": DictElement(
                required=False,
                parameter_form=Choice(
                    title=Title("Sort Direction"),
                    choices=[
                        ("asc", "Ascending"),
                        ("desc", "Descending"),
                    ],
                ),
            ),
            "where": DictElement(
                required=False,
                parameter_form=Text(
                    title=Title("Filter Criteria"),
                ),
            ),
        }
    )

rule_spec_xiq_device_list = SpecialAgent(
    topic=Topic.NETWORK,
    name="xiq_device_list",
    title=Title("ExtremeCloud IQ Device List"),
    parameter_form=_formspec
)