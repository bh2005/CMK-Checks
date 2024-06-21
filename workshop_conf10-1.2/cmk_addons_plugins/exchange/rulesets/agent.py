#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import Label, Title
from cmk.rulesets.v1.form_specs import DefaultValue, DictElement, Dictionary, Integer
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _parameter_form() -> Dictionary:
    return Dictionary(
        elements={
            # NEW: make number of packages for summary section configurable
            "package_count": DictElement(
                parameter_form=Integer(
                    prefill=DefaultValue(5), label=Label("Number of packages for summary")
                ),
                required=True,
            )
        }
    )


rule_spec_exchange_agent = SpecialAgent(
    name="exchange",
    title=Title("Exchange Agent"),
    parameter_form=_parameter_form,
    topic=Topic.GENERAL,
)
