#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme Networks - Stacking Ruleset
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
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_extreme_stacking() -> Dictionary:
    return Dictionary(
        title=Title("Extreme Networks Stacking Parameters"),
        help_text=Help(
            "Configures the expected role for a stack slot. "
            "If the actual role differs, WARN is triggered."
        ),
        elements={
            "expected_role": DictElement(
                required=False,
                parameter_form=SingleChoice(
                    title=Title("Expected Role for this Slot"),
                    elements=[
                        SingleChoiceElement(name="1", title=Title("Master")),
                        SingleChoiceElement(name="2", title=Title("Backup")),
                        SingleChoiceElement(name="3", title=Title("Standby")),
                    ],
                    prefill=DefaultValue("3"),
                ),
            ),
        },
    )


rule_spec_extreme_stacking = CheckParameters(
    name="extreme_stacking",
    title=Title("Extreme Networks Stacking"),
    topic=Topic.HARDWARE,
    parameter_form=_parameter_form_extreme_stacking,
    condition=HostAndItemCondition(item_title=Title("Slot ID")),
)
