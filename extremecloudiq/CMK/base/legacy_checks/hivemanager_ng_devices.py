#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# <<<hivemanager_ng_devices:sep(124)>>>
# osVersion::8.1.2.1|ip::10.8.92.100|hostName::Host-1|lastUpdated::2017-11-08T10:01:43.674Z|activeClients::0|connected::True|serialId::00000000000001
# osVersion::8.1.2.1|ip::10.8.92.130|hostName::Host-2|lastUpdated::2017-11-08T10:01:44.056Z|activeClients::14|connected::True|serialId::00000000000002
# osVersion::8.1.2.1|ip::10.8.92.135|hostName::Host-3|lastUpdated::2017-11-08T10:01:44.153Z|activeClients::12|connected::True|serialId::00000000000003
# osVersion::8.1.2.1|ip::10.8.92.140|hostName::Host-4|lastUpdated::2017-11-08T10:01:44.361Z|activeClients::10|connected::True|serialId::00000000000004
# osVersion::8.1.2.1|ip::10.8.92.145|hostName::Host-5|lastUpdated::2017-11-08T10:01:44.362Z|activeClients::5|connected::True|serialId::00000000000005
# osVersion::8.1.2.1|ip::10.8.92.150|hostName::Host-6|lastUpdated::2017-11-08T10:01:44.638Z|activeClients::13|connected::True|serialId::00000000000006
# osVersion::8.1.2.1|ip::10.8.92.155|hostName::Host-7|lastUpdated::2017-11-08T10:01:44.667Z|activeClients::14|connected::True|serialId::00000000000007
# osVersion::8.1.2.1|ip::10.8.92.160|hostName::Host-8|lastUpdated::2017-11-08T10:01:44.690Z|activeClients::10|connected::True|serialId::00000000000008
# osVersion::6.5.8.1|ip::10.8.95.100|hostName::Host-9|lastUpdated::2017-11-07T22:50:20.425Z|activeClients::9|connected::True|serialId::12345678912345


from cmk.agent_based.legacy.v0_unstable import LegacyCheckDefinition

check_info = {}


def parse_hivemanager_ng_devices(string_table):
    parsed = {}
    for device in string_table:
        data = dict(element.split("::") for element in device)

        data["connected"] = data["connected"] == "True"
        data["activeClients"] = int(data["activeClients"])

        host = data.pop("hostName")
        parsed[host] = data

    return parsed


def inventory_hivemanager_ng_devices(parsed):
    for host in parsed:
        yield host, {}


def check_hivemanager_ng_devices(item, params, parsed):
    device = parsed.get(item)
    if not device:
        yield 2, "No data for device."

    status, connected = 0, device["connected"]
    if connected is not True:
        status = 2
    yield status, "Connected: %s" % connected

    status, clients = 0, device["activeClients"]
    infotext = "active clients: %s" % clients
    warn, crit = params["max_clients"]
    if clients >= crit:
        status = 2
        infotext += f" (warn/crit at {warn}/{crit})"
    elif clients >= warn:
        status = 1
        infotext += f" (warn/crit at {warn}/{crit})"
    perfdata = [("connections", clients, warn, crit)]
    yield status, infotext, perfdata

    informational = [
        ("ip", "IP address"),
        ("serialId", "serial ID"),
        ("osVersion", "OS version"),
        ("lastUpdated", "last updated"),
    ]
    for key, text in informational:
        yield 0, f"{text}: {device[key]}"


check_info["hivemanager_ng_devices"] = LegacyCheckDefinition(
    name="hivemanager_ng_devices",
    parse_function=parse_hivemanager_ng_devices,
    service_name="Client %s",
    discovery_function=inventory_hivemanager_ng_devices,
    check_function=check_hivemanager_ng_devices,
    check_ruleset_name="hivemanager_ng_devices",
    check_default_parameters={
        "max_clients": (25, 50),
    },
)