#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json
from collections.abc import Mapping
from typing import Any

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

Section = Mapping[str, Any]


def parse_exchange_packages(string_table: StringTable) -> Section:
    section = {}
    for line in string_table:
        package = json.loads(line[0])
        section[package["package_name"]] = package
    return section


agent_section_packages = AgentSection(
    name="exchange_packages",
    parse_function=parse_exchange_packages,
)


def discover_exchange_package(section: Section) -> DiscoveryResult:
    for package_name, item_data in section.items():
        yield Service(item=package_name, parameters={"enabled": item_data["enabled"]})


def check_exchange_package(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if (item_data := section.get(item)) is None:
        return

    downloads = item_data["downloads"]
    yield Result(state=State.OK, summary=f"Downloads: {downloads}")
    yield Metric("downloads", downloads)

    if item_data["enabled"] != params["enabled"]:
        yield Result(
            state=State.CRIT, summary="Exchange packages state does not have expected state"
        )

    yield from check_levels(
        value=float(item_data["average_rating"]),
        levels_lower=params["rating_threshold"],
        metric_name="average_rating",
    )


check_plugin_exchange_package = CheckPlugin(
    name="exchange_packages",
    service_name="Exchange Package %s",
    check_function=check_exchange_package,
    discovery_function=discover_exchange_package,
    check_ruleset_name="exchange_packages",
    check_default_parameters={"enabled": False, "rating_threshold": ("fixed", (4.0, 3.0))},
)


# NEW: example for inventory plugin


agent_section_exchange_packages_summary = AgentSection(
    name="exchange_packages_summary",
    parse_function=parse_exchange_packages,
)


def inventory_exchange_summary(section: Section) -> InventoryResult:
    for package_name, package_info in section.items():
        yield TableRow(
            path=["software", "applications", "exchange", "packages"],
            key_columns={"name": package_name},
            inventory_columns={
                "created_at": package_info["created_at"],
                "author": package_info["author"],
            },
            status_columns={"enabled": package_info["enabled"]},
        )


inventory_plugin_exchange_packages = InventoryPlugin(
    name="exchange_packages_summary",
    inventory_function=inventory_exchange_summary,
)
