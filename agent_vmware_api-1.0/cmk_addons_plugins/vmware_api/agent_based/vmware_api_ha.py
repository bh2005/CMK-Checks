#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    InventoryPlugin,
    InventoryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
    TableRow,
)

import json

class DRS:
    def __init__(self, section, params):
        self.name = section['name']

        self.drs_summary = 'DRS: enabled' if section['drs_enabled'] else 'DRS: disabled'
        if 'enabled' in self.drs_summary:
            self.drs_state = State(params.get('drs_enable_state', State.OK))
        else:
            self.drs_state = State(params.get('drs_disable_state', State.WARN))

    def check(self):
        return Result(state=self.drs_state, summary=self.drs_summary)

    def __repr__(self):
        return f'{self.drs_summary}'

class HA:
    def __init__(self, section, params):
        self.items = []
        self.name = section['name']

        self.ha_summary = 'HA: enabled' if section['ha_enabled'] else 'HA: disabled'
        if 'enabled' in self.ha_summary:
            self.ha_state = State(params.get('ha_enable_state', State.OK))
        else:
            self.ha_state = State(params.get('ha_disable_state', State.WARN))


    def check(self):
        return Result(state=self.ha_state, summary=self.ha_summary)

    def __repr__(self):
        return f'{self.ha_summary}'


def parse_(stringtable):
    return json.loads(stringtable[0][0])

def discover_vmware_api_ha(section):
    for vmware_api_ha in section:
        item = vmware_api_ha['name']
        yield Service(item=item)

def check_vmware_api_ha(item, params, section):
    print('PARAMS', params)
    for vmware_api_ha in section:
        drs = DRS(vmware_api_ha, params)
        ha = HA(vmware_api_ha, params)
        if drs.name == item:
            yield drs.check()
            yield ha.check()

agent_section_vmware_api_ha = AgentSection(
    name="vmware_api_ha",
    parse_function=parse_,
)

check_plugin_vmware_api_ha = CheckPlugin(
    name="vmware_api_ha",
    service_name="VMware DRS/HA [%s]",
    check_function=check_vmware_api_ha,
    check_default_parameters={},
    check_ruleset_name='vmware_api_ha',
    discovery_function=discover_vmware_api_ha,
)
