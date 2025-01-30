#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check VMware certificates via API
"""

#
# Author: muehling.stefan[at]googlemail[dot]com
# Date  : 2023-02-21
#
# CheckMK special agent for VMware API, check certificates
# Requires:
#
#

# Certificate will expire in less then 90 days (expires 2023-04-05)

from collections.abc import Mapping

import json
import time
from typing import List, Dict, Any
from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    InventoryPlugin,
    Metric,
    render,
    Result,
    Service,
    State,
    StringTable,
    TableRow,
)

def parse_vmware_api_certificates(string_table: StringTable):
#    print(' DEBUG:', string_table)
    try:
        agentoutput = string_table
    except json.JSONDecodeError:
        return
    return agentoutput


def discover_vmware_api_certificates(section: List) -> DiscoveryResult:
    #print(section)
    for element in section:
#        print(' DEBUG:', element)
        usage, CN, expires, subject = element
#        print(' DEBUG:', f'{usage} {CN}')
        yield Service(item=f'{usage}')

def check_vmware_api_certificates(item, params: Mapping[str, tuple[float, float]], section: Dict[str, Any]) -> CheckResult:
    # get parameters
#    print(params)
    param_type, [warn, crit] = params['age']
    levels = (param_type, (warn, crit))
    now = int(time.time())

    for element in section:
        usage, CN, expires, subject = element
        expires = float(expires)
        if item == f'{usage}':

            secondsremaining = expires - now
            if secondsremaining < 0:
                infotext = "%s expired %s ago on %s" % ( subject, render.timespan(abs(secondsremaining)),
                                                  time.strftime("%c", time.gmtime(expires)))
            else:
                infotext = "%s expires in %s on %s" % ( subject, render.timespan(secondsremaining),
                                                 time.strftime("%c", time.gmtime(expires)))
            infotext = subject
            if secondsremaining > 0:
                yield from check_levels(secondsremaining,
                    levels_lower=levels,
                    metric_name='lifetime_remaining',
                    label='Lifetime Remaining',
                    render_func=render.timespan,
                    )
            else:
                yield from check_levels(secondsremaining,
                    levels_lower=levels,
                    metric_name='lifetime_remaining',
                    label='Expired',
                    render_func=lambda x: "%s ago" % render.timespan(abs(x)),
                    )

            yield Result(state=State.OK, summary=infotext)
#            print(usage, CN, expires)
#            yield Result(state=State.CRIT, summary=f'Connection failed')
#            yield Result(state=State.OK, summary=f'{usage, CN, expires}')

agent_section_vmware_api_certificates = AgentSection(
    name="vmware_api_certificates",
    parse_function=parse_vmware_api_certificates,
)

check_plugin_vmware_api_certificates = CheckPlugin(
    name="vmware_api_certificates",
    service_name="VMware %s",
    check_function=check_vmware_api_certificates,
    discovery_function=discover_vmware_api_certificates,
    check_default_parameters={'age': ('fixed', (5184000.0, 2592000.0))},
    check_ruleset_name='vmware_api_certificates',
)
