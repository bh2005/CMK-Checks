#!/usr/bin/env python3
#-*- encoding: utf-8
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Ruleset: ExtremeCloud IQ Controller


from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import DefaultValue, DictElement, Dictionary, Integer, MultipleChoice, MultipleChoiceElement, String, Password, validators
from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent


def _valuespec_special_agent_netextreme_xiq_controller():
    return Dictionary(
        elements={
            "username": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                    help_text=Help("User ID for web login"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    help_text=Help("Password for the user"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
                required=True,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("TCP Port"),
                    help_text=Help("Port number for API connection"),
                    prefill=DefaultValue(5825),
                    custom_validate=(
                        validators.NumberInRange(min_value=1, max_value=65535),
                    ),
                ),
                required=True,
            ),
            "sections": DictElement(
                parameter_form=MultipleChoice(
                    title=Title("Get information about..."),
                    elements=[
                        MultipleChoiceElement(
                            name="ap", title=Title("Access Points"),
                        ),
                        MultipleChoiceElement(
                            name="site", title=Title("Sites (Locations)"),
                        ),
                        MultipleChoiceElement(
                            name="wlan", title=Title("WLANs"),
                        ),
                    ],
                    prefill=DefaultValue(
                        [
                            "ap",
                            "site",
                            "wlan",
                        ]
                    ),
                    show_toggle_all=True,
                ),
            ),
        },
    )


rule_spec_netextreme_xiq_controller = SpecialAgent(
    name="netextreme_xiq_controller",
    title=Title("ExtremeCloud IQ Controller"),
    topic=Topic.NETWORKING,
    parameter_form=_valuespec_special_agent_netextreme_xiq_controller,
)