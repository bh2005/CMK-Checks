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

def check_parameter_form():
    return Dictionary(
        title=Title("Values"),
        elements={
            "age": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Age"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=tuple(TimeMagnitude)
                    ),
#                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint(value=(5184000.0, 2592000.0)),
                )
            )
        }
    )

rule_spec_vmware_api_certificates = CheckParameters(
    name="vmware_api_certificates",
    title=Title("VMware certificates"),
    parameter_form=check_parameter_form,
    topic=Topic.APPLICATIONS,
    condition=HostCondition(),
)
