#!/usr/bin/env python3
#
# Author : Alexander Vogel (alexander.vogel.2305@gmail.com)
# Date   : 2025-11-28
# License: GNU General Public License v2
#
# Check: ExtremeCloud IQ Controller - Sites

import ast
import itertools

from cmk.agent_based.v2 import AgentSection, check_levels, CheckPlugin, get_rate, get_value_store, Metric, Service, State, render, Result
from datetime import datetime, timezone


def parse_netextreme_xiq_controller_site(string_table):

    parsed = []
    flatlist = list(itertools.chain.from_iterable(string_table))
    
    for f in flatlist:
        i = ast.literal_eval(f)
        parsed.append(i)

    return parsed


def discover_netextreme_xiq_controller_site(section):
    for site in section:
        yield Service(item = f"{site['name']}")


def check_netextreme_xiq_controller_site(item, params, section):

    for site in section:

        if f"{site['name']}" != item:
            continue

        # clients
        yield from check_levels(
            site['clients'],
            label="Clients",
            levels_upper=params["levels_upper"],
            render_func=lambda v: int(v),
            metric_name="netextreme_xiq_controller_clients",
            boundaries=(0, None)
        )

    return None


agent_section_netextreme_xiq_controller_site = AgentSection(
    name = "netextreme_xiq_controller_site",
    parse_function = parse_netextreme_xiq_controller_site,
)


check_plugin_netextreme_xiq_controller_site = CheckPlugin(
    name = "netextreme_xiq_controller_site",
    service_name = "Site %s",
    discovery_function = discover_netextreme_xiq_controller_site,
    check_function = check_netextreme_xiq_controller_site,
    check_default_parameters = {
        "levels_upper": ('no_levels', None),
    },
    check_ruleset_name = "netextreme_xiq_controller_site",
)
