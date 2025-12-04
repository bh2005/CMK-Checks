#!/usr/bin/env python3
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Check: ExtremeCloud IQ Controller - Access Points

# sample output:
# <<<netextreme_xiq_controller_ap:sep(0)>>>
# [
#     {
#         'name': 'Haus A 404', 
#         'power': 0.0, 
#         'uptime': 10300892, 
#         'radio1_clients': 1, 
#         'radio2_clients': 0, 
#         'clients': 1, 
#         'status': 'InService'
#     }, 
#     {...}
# ]


import ast
import itertools

from cmk.agent_based.v2 import AgentSection, check_levels, CheckPlugin, get_rate, get_value_store, Metric, Service, State, render, Result
from datetime import datetime, timezone


def parse_netextreme_xiq_controller_ap(string_table):

    parsed = []
    flatlist = list(itertools.chain.from_iterable(string_table))
    
    for f in flatlist:
        i = ast.literal_eval(f)
        parsed.append(i)

    return parsed


def discover_netextreme_xiq_controller_ap(section):
    for ap in section:
        if ap['status'] != 'Unknown':
            yield Service(item = f"{ap['name']}")


def check_netextreme_xiq_controller_ap(item, params, section):

    map_status = {
        "critical": "Critical",
        "InService": "In-Service",
        "InServiceTrouble": "In-Service Trouble",
        "Unknown": "Unknown",
        "Upgrading": "Upgrading",
    }

    for ap in section:

        if f"{ap['name']}" != item:
            continue

        # status: InServce, Upgrading, Unknown, critical
        if ap['status'] == 'InService':
            yield Result(state=State(params["state_ap_inservice"]), summary=f"Status: {map_status.get(ap['status'])}")
        
        else:
            if ap['status'] == 'Upgrading':
                yield Result(state=State(params["state_ap_uprading"]), summary=f"Status: {map_status.get(ap['status'])}")
            elif ap['status'] == 'InServiceTrouble':
                yield Result(state=State(params["state_ap_inservicetrouble"]), summary=f"Status: {map_status.get(ap['status'])}")
            elif ap['status'] == 'critical':
                yield Result(state=State(params["state_ap_critical"]), summary=f"Status: {map_status.get(ap['status'])}")
            else:
                yield Result(state=State.UNKNOWN, summary=f"Status: {ap['status']}")
            return None

        # uptime
        yield from check_levels(
            ap['uptime'],
            label="Uptime",
            render_func=lambda v: f'{render.timespan(v)}',
            metric_name="netextreme_xiq_controller_uptime",
            boundaries=(0, None)
        )

        # clients
        yield from check_levels(
            ap['clients'],
            label="Clients",
            levels_upper=params["ap_clients_levels_upper"],
            render_func=lambda v: int(v),
            metric_name="netextreme_xiq_controller_ap_clients",
            boundaries=(0, None)
        )

        # power
        # If Power <= 0, then this hardware type can't read the power.
        # Typical Extreme Networks: simply outputting 0 for a value that can't be determined...
        if ap['power'] > 0:
            yield from check_levels(
                ap['power'],
                label="Power",
                levels_upper=params["ap_power_levels_upper"],
                render_func=lambda v: f'{v} W',
                metric_name="netextreme_xiq_controller_ap_power",
                boundaries=(0, None)
            )
        
        

    return None


agent_section_netextreme_xiq_controller_ap = AgentSection(
    name = "netextreme_xiq_controller_ap",
    parse_function = parse_netextreme_xiq_controller_ap,
)


check_plugin_netextreme_xiq_controller_ap = CheckPlugin(
    name = "netextreme_xiq_controller_ap",
    service_name = "AP %s",
    discovery_function = discover_netextreme_xiq_controller_ap,
    check_function = check_netextreme_xiq_controller_ap,
    check_default_parameters = {
        "state_ap_inservice": 0,
        "state_ap_uprading": 0,
        "state_ap_inservicetrouble": 1,
        "state_ap_critical": 2,
        "ap_clients_levels_upper": ('no_levels', None),
        "ap_power_levels_upper": ('no_levels', None),
    },
    check_ruleset_name = "netextreme_xiq_controller_ap",
)
