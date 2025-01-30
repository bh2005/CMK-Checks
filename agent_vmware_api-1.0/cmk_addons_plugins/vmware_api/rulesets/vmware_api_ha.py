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
    ServiceState,
)

from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent, CheckParameters, HostAndItemCondition, HostCondition

def check_parameter_form():
    return Dictionary(
        title=Title("Values"),
        elements={
            "ha_enable_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'HA enabled'"),
                    prefill=DefaultValue(ServiceState.OK),
                ),
                required=True,
            ),
            "ha_disable_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'HA disabled'"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
                required=True,
            ),

            "drs_enable_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'DRS enabled'"),
                    prefill=DefaultValue(ServiceState.OK),
                ),
                required=True,
            ),
            "drs_disable_state": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'DRS disabled'"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
                required=True,
            ),


        }
    )

rule_spec_vmware_api_ha = CheckParameters(
    name="vmware_api_ha",
    title=Title("VMware DRS/HA"),
    parameter_form=check_parameter_form,
    topic=Topic.APPLICATIONS,
    condition=HostCondition(),
)
