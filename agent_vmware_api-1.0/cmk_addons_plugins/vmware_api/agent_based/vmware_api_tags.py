#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check VMware tags via API 
"""

#
# Author: muehling.stefan[at]googlemail[dot]com
# Date  : 2024-02-01
#
# CheckMK special agent for VMware API, check tags 
# Requires: 
#
#

import json
from typing import List, Dict, Any

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

def parse_vmware_api_tags(string_table):
#    print(' DEBUG:', string_table)
    try:
        agentoutput = string_table
    except json.JSONDecodeError:
        return
    return agentoutput


def discovery_vmware_api_tags(section: List) -> DiscoveryResult:
    yield Service()

def check_vmware_api_tags(section: Dict[str, Any]) -> CheckResult:
    if len(section) == 0:
        yield Result(state=State.OK, summary='All VMs are tagged')
    for element in section:
        vm, = element
        yield Result(state=State.CRIT, summary=vm)


agent_section_vmware_api_tags = AgentSection(
    name="vmware_api_tags",
    parse_function=parse_vmware_api_tags,
)

check_plugin_vmware_api_tags = CheckPlugin(
    name="vmware_api_tags",
    service_name="VMs without (backup) tag",
    check_function=check_vmware_api_tags,
    discovery_function=discovery_vmware_api_tags,
)
