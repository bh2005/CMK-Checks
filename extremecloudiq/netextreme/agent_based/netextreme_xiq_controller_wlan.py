#!/usr/bin/env python3
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Check: ExtremeCloud IQ Controller - WLANs

import ast
import itertools

from cmk.agent_based.v2 import AgentSection, check_levels, CheckPlugin, get_rate, get_value_store, Metric, Service, State, render, Result
from datetime import datetime, timezone


def parse_netextreme_xiq_controller_wlan(string_table):

    parsed = []
    flatlist = list(itertools.chain.from_iterable(string_table))
    
    for f in flatlist:
        i = ast.literal_eval(f)
        parsed.append(i)

    return parsed


def discover_netextreme_xiq_controller_wlan(section):
    for service in section:
        if service['status'] == 'enabled':
            yield Service(item = f"{service['serviceName']}")


def check_netextreme_xiq_controller_wlan(item, params, section):

    for service in section:
        
        inOctets_rate = 0
        outOctets_rate = 0

        if f"{service['serviceName']}" != item:
            continue
            
        # ssid
        yield Result(state=State.OK, summary="SSID: %s" %(service['ssid']))
        
        # clients
        yield from check_levels(
            service['clients'],
            label="Clients",
            levels_upper=params["levels_upper"],
            render_func=lambda v: int(v),
            metric_name="netextreme_xiq_controller_clients",
            boundaries=(0, None)
        )

    return None


agent_section_netextreme_xiq_controller_wlan = AgentSection(
    name = "netextreme_xiq_controller_wlan",
    parse_function = parse_netextreme_xiq_controller_wlan,
)


check_plugin_netextreme_xiq_controller_wlan = CheckPlugin(
    name = "netextreme_xiq_controller_wlan",
    service_name = "WLAN %s",
    discovery_function = discover_netextreme_xiq_controller_wlan,
    check_function = check_netextreme_xiq_controller_wlan,
    check_default_parameters = {
        "levels_upper": ('no_levels', None),
    },
    check_ruleset_name = "netextreme_xiq_controller_wlan",
)
