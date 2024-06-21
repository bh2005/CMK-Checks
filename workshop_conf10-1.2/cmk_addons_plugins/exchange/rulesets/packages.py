#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form() -> Dictionary:
    return Dictionary(
        elements={
            "enabled": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Expected package state"),
                    label=Label("Package expected to be enabled"),
                ),
                required=True,
            ),
            "rating_threshold": DictElement(
                parameter_form=SimpleLevels(
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(),
                    prefill_fixed_levels=DefaultValue(value=(4.0, 3.0)),
                    title=Title("Package rating"),
                ),
                required=True,
            ),
        }
    )


rule_spec_exchange_package = CheckParameters(
    name="exchange_packages",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_form,
    title=Title("Exchange Package"),
    condition=HostAndItemCondition(item_title=Title("Package name")),
)
