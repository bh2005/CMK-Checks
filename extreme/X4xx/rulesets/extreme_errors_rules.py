#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - Interface Egress Errors Ruleset
Checkmk 2.4 - Rulesets API v1

Install path: ~/local/lib/python3/cmk_addons/plugins/extreme_networks/rulesets/
Author: bh2005
License: GPL v2
"""
from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_extreme_errors() -> Dictionary:
    return Dictionary(
        title=Title("Extreme Networks Interface Egress Errors Levels"),
        help_text=Help(
            "Thresholds for egress errors per interface (extremePortEgressErrors). "
            "Only interfaces with errors are auto-discovered."
        ),
        elements={
            "egress_errors_levels": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Egress errors thresholds (absolute)"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="Errors"),
                    prefill_fixed_levels=DefaultValue(value=(10, 50)),
                ),
            ),
        },
    )


rule_spec_extreme_errors = CheckParameters(
    name="extreme_errors",
    title=Title("Extreme Networks Interface Egress Errors"),
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_extreme_errors,
    condition=HostAndItemCondition(item_title=Title("Interface Index")),
)
