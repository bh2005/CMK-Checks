#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Mapping, Any, Iterable
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
)

def discover_xiq_aps(section: Mapping[str, Any]) -> DiscoveryResult:
    if section and section.get("ap_name"):
        yield Service(item=section["ap_name"])

def check_xiq_ap_clients(item: str, section: Mapping[str, int]) -> Iterable[CheckResult]:
    c24 = int(section.get("clients_24", 0))
    c5  = int(section.get("clients_5",  0))
    c6  = int(section.get("clients_6",  0))
    total = c24 + c5 + c6
    yield Result(state=State.OK, summary=f"{item}: {total} Clients (2.4GHz: {c24}, 5GHz: {c5}, 6GHz: {c6})")
    yield Metric("xiq_clients_24", c24)
    yield Metric("xiq_clients_5",  c5)
    yield Metric("xiq_clients_6",  c6)

check_plugin_xiq_ap_clients = CheckPlugin(
    name="xiq_ap_clients",
    sections=["extreme_ap_clients"],
    service_name="XIQ AP %s Clients",
    discovery_function=discover_xiq_aps,
    check_function=check_xiq_ap_clients,
)
