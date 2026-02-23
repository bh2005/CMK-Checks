#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - Hardware Ruleset (CPU & Temperature)
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
    Float,
    LevelDirection,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _parameter_form_extreme_hw() -> Dictionary:
    return Dictionary(
        title=Title("Extreme Networks Hardware Levels"),
        help_text=Help("Thresholds for CPU utilization and temperature."),
        elements={
            "cpu_levels": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("CPU Utilization levels (5 min avg)"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue(value=(70.0, 90.0)),
                ),
            ),
            "temp_levels": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Temperature levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="C"),
                    prefill_fixed_levels=DefaultValue(value=(80.0, 95.0)),
                ),
            ),
        },
    )


rule_spec_extreme_hw = CheckParameters(
    name="extreme_hw",
    title=Title("Extreme Networks Hardware (CPU & Temperature)"),
    topic=Topic.HARDWARE,
    parameter_form=_parameter_form_extreme_hw,
    condition=HostCondition(),
)
