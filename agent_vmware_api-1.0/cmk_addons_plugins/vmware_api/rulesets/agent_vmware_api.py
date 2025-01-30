#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Stefan Mühling <muehling.stefan@googlemail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Help

from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    Integer,
    BooleanChoice,
    MultipleChoice,
    MultipleChoiceElement,
    Password,
    String,
    migrate_to_float_simple_levels,
    migrate_to_password,
    InputHint,
    validators,
    SimpleLevels,
    LevelDirection,
    TimeMagnitude,
    TimeSpan,
)

from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent, CheckParameters, HostAndItemCondition, HostCondition

def agent_parameter_form():
    return Dictionary(
        title=Title("VMware API"),
        elements={
            "username": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                    migrate=migrate_to_password,
                ),
                required=True,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("Advanced - TCP Port number"),
                    help_text=Help(
                        "Port number for connection to the Rest API. Usually 443 (TLS)"
                    ),
                    prefill=DefaultValue(443),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=65535),),
                ),
            ),
            "verify_ssl": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Verify SSL certificate"),
                    label=Help("Verify SSL certificate"),
                    prefill=DefaultValue(True),
                )
            ),
        },
    )


rule_spec_vmware_api = SpecialAgent(
    name="vmware_api",
    title=Title("VMware API"),
    parameter_form=agent_parameter_form,
    topic=Topic.GENERAL,
)
