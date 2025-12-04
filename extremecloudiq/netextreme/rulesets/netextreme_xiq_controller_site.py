#!/usr/bin/env python3
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Ruleset: ExtremeCloud IQ Controller - WLANs


from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    LevelsType,
    ServiceState,
    SimpleLevels,
    migrate_to_integer_simple_levels,
    validators,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Help,
    HostAndItemCondition,
    Topic,
)


def _parameter_form_netextreme_xiq_controller_site():
    return Dictionary(
        elements={
            'levels_upper': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Maximum Number of clients'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol='Clients'),
                    prefill_levels_type = DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=DefaultValue(value=(100, 200)),
                )
            ),
        }
    )


rule_spec_netextreme_xiq_controller_site = CheckParameters(
    name='netextreme_xiq_controller_site',
    title=Title('Extreme CloudIQ Controller Site Clients'),
    topic=Topic.NETWORKING,
    condition = HostAndItemCondition(item_title=Title("Site")),
    parameter_form=_parameter_form_netextreme_xiq_controller_site,
)
