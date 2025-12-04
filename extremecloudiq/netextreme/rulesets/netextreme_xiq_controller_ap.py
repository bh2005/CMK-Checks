#!/usr/bin/env python3
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Ruleset: ExtremeCloud IQ Controller - APs


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


def _parameter_form_netextreme_xiq_controller_ap():
    return Dictionary(
        elements={
            
            'state_ap_inservice': DictElement(
                parameter_form=ServiceState(
                    title=Title('State if AP is "In-Service"'),
                    help_text=Help('Default monitoring state if the AP is In-Service.'),
                    prefill=DefaultValue(0)
                )
            ),
            'state_ap_uprading': DictElement(
                parameter_form=ServiceState(
                    title=Title('State if AP is "Upgrading"'),
                    help_text=Help('Default monitoring state if the AP is an upgrade process.'),
                    prefill=DefaultValue(0)
                )
            ),
            'state_ap_inservicetrouble': DictElement(
                parameter_form=ServiceState(
                    title=Title('State if AP is "In-Service Trouble"'),
                    help_text=Help('Default monitoring state if the AP is In-Service Trouble.'),
                    prefill=DefaultValue(1)
                )
            ),
            'state_ap_critical': DictElement(
                parameter_form=ServiceState(
                    title=Title('State if AP is "Critical"'),
                    help_text=Help('Default monitoring state if the AP is Critical.'),
                    prefill=DefaultValue(2)
                )
            ),
            'ap_clients_levels_upper': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Maximum Number of clients'),
                    help_text=Help('Set the upper levels for AP clients.'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol='Clients'),
                    prefill_levels_type = DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=DefaultValue(value=(80, 90)),
                )
            ),
            'ap_power_levels_upper': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('AP Power upper levels'),
                    help_text=Help('Set the upper levels for the AP power in W.'),
                    form_spec_template=Integer(unit_symbol='W'),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(7.0, 8.0)),
                )
            ),
        }
    )


rule_spec_netextreme_xiq_controller_ap = CheckParameters(
    name='netextreme_xiq_controller_ap',
    title=Title('Extreme CloudIQ Controller APs'),
    topic=Topic.NETWORKING,
    condition = HostAndItemCondition(item_title=Title("AP")),
    parameter_form=_parameter_form_netextreme_xiq_controller_ap,
)
