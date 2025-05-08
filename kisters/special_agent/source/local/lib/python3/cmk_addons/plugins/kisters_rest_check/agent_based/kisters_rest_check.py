# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Check Plug-in for Kisters REST API Check
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Based on https://github.com/bh2005/CMK-Checks/blob/master/kisters/rest-check.py

from typing import List, Optional, Dict
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Service,
    Result,
    State,
    Metric,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    StringTable,
    DiscoveryResult,
    CheckResult,
)

def parse_kisters_rest_check(string_table: StringTable) -> List[Dict[str, str]]:
    """Parse the kisters_rest_check section into a list of instances."""
    instances = []
    current_instance = {}
    for line in string_table:
        if line[0] == "---":
            if current_instance:
                instances.append(current_instance)
                current_instance = {}
        else:
            key, value = line[0].split(": ", 1)
            current_instance[key] = value
    if current_instance:
        instances.append(current_instance)
    return instances

register.agent_section(
    name="kisters_rest_check",
    parse_function=parse_kisters_rest_check,
)

def discover_kisters_rest_check(section: List[Dict[str, str]]) -> DiscoveryResult:
    """Discover services for each instance in the kisters_rest_check section."""
    for instance in section:
        if "instance" in instance:
            yield Service(item=instance["instance"])

def check_kisters_rest_check(item: str, params: Dict, section: List[Dict[str, str]]) -> CheckResult:
    """Check the status and response time for a specific instance."""
    for instance in section:
        if instance.get("instance") != item:
            continue

        status_code = instance.get("status_code", "-1")
        response_time = float(instance.get("response_time", "0"))
        error = instance.get("error")
        pvId = instance.get("pvId")

        # Check status code
        if status_code == "200":
            state = State.OK
            summary = f"Status: OK{pvId and f', pvId: {pvId}' or ''}"
        elif status_code == "-1":
            state = State.CRIT
            summary = f"Error: {error or 'Unknown'}{pvId and f', pvId: {pvId}' or ''}"
        else:
            state = State.CRIT
            summary = f"Status: {status_code}{pvId and f', pvId: {pvId}' or ''}"

        yield Result(state=state, summary=summary)

        # Check response time
        if status_code != "-1":
            warn, crit = params.get("response_time", (1.0, 2.0))
            yield Metric("response_time", response_time, levels=(warn, crit))
            if response_time >= crit:
                yield Result(state=State.CRIT, summary=f"Response time: {response_time:.3f}s (crit at {crit}s)")
            elif response_time >= warn:
                yield Result(state=State.WARN, summary=f"Response time: {response_time:.3f}s (warn at {warn}s)")
            else:
                yield Result(state=State.OK, summary=f"Response time: {response_time:.3f}s")

register.check_plugin(
    name="kisters_rest_check",
    service_name="Kisters REST Check %s",
    discovery_function=discover_kisters_rest_check,
    check_function=check_kisters_rest_check,
    check_default_parameters={"response_time": (1.0, 2.0)},
    check_ruleset_name="kisters_rest_check",
)