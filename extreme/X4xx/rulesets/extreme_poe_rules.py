#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - PoE Budget Ruleset
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


def _parameter_form_extreme_poe() -> Dictionary:
    return Dictionary(
        title=Title("Extreme Networks PoE Budget Levels"),
        help_text=Help(
            "Thresholds for PoE usage as a percentage of available budget."
        ),
        elements={
            "poe_levels_pct": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("PoE usage levels (% of total budget)"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue(value=(80.0, 90.0)),
                ),
            ),
        },
    )


rule_spec_extreme_poe = CheckParameters(
    name="extreme_poe",
    title=Title("Extreme Networks PoE Power Budget"),
    topic=Topic.POWER,
    parameter_form=_parameter_form_extreme_poe,
    condition=HostCondition(),
)
