# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Check Plug-in for RAPID Server Thermal Data
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Based on redfish_fans.py by Andreas Doehler (Yogibaer75)

from typing import Dict, List, Optional, Tuple
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    check_levels,
    register,
    Service,
    Result,
    State,
    Metric,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)
import json

def parse_rapid_thermal(string_table: StringTable) -> Optional[Dict]:
    """Parse the rapid_thermal section from agent output"""
    try:
        # Join all lines and parse as JSON
        json_data = " ".join(" ".join(line) for line in string_table)
        return json.loads(json_data)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing rapid_thermal data: {e}")
        return None

register.agent_section(
    name="rapid_thermal",
    parse_function=parse_rapid_thermal,
)

def discover_rapid_thermal(section: Optional[Dict]) -> DiscoveryResult:
    """Discover services for fans and temperatures"""
    if not section:
        return

    # Discover fans
    for fan in section.get("Fans", []):
        if fan.get("Name") and fan.get("Status", {}).get("State") == "Enabled":
            yield Service(item=f"Fan {fan['Name']}")

    # Discover temperatures
    for temp in section.get("Temperatures", []):
        if temp.get("Name") and temp.get("Status", {}).get("State") == "Enabled":
            yield Service(item=f"Temperature {temp['Name']}")

def check_rapid_thermal(item: str, params: Dict, section: Optional[Dict]) -> CheckResult:
    """Check function for fans and temperatures"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No thermal data available")
        return

    # Check if item is a fan
    if item.startswith("Fan "):
        fan_name = item[len("Fan "):]
        for fan in section.get("Fans", []):
            if fan.get("Name") == fan_name:
                yield from check_fan(fan, params)
                return
        yield Result(state=State.UNKNOWN, summary=f"Fan {fan_name} not found")
        return

    # Check if item is a temperature
    if item.startswith("Temperature "):
        temp_name = item[len("Temperature "):]
        for temp in section.get("Temperatures", []):
            if temp.get("Name") == temp_name:
                yield from check_temperature(temp, params)
                return
        yield Result(state=State.UNKNOWN, summary=f"Temperature {temp_name} not found")
        return

def check_fan(fan: Dict, params: Dict) -> CheckResult:
    """Check a single fan"""
    health = fan.get("Status", {}).get("Health", "Unknown")
    state = fan.get("Status", {}).get("State", "Unknown")
    reading = fan.get("Reading")

    # Map Health to Checkmk state
    health_state = {
        "OK": State.OK,
        "Warning": State.WARN,
        "Critical": State.CRIT,
        "Unknown": State.UNKNOWN,
    }.get(health, State.UNKNOWN)

    summary = f"Status: {health}, State: {state}, Speed: {reading} RPM"
    yield Result(state=health_state, summary=summary)

    # Add metric for fan speed
    if reading is not None:
        yield Metric("fan", reading, levels=(params.get("fan_upper", None), None),
                     boundaries=(params.get("fan_lower", 0), None))

def check_temperature(temp: Dict, params: Dict) -> CheckResult:
    """Check a single temperature sensor"""
    health = temp.get("Status", {}).get("Health", "Unknown")
    state = temp.get("Status", {}).get("State", "Unknown")
    reading = temp.get("ReadingCelsius")

    # Map Health to Checkmk state
    health_state = {
        "OK": State.OK,
        "Warning": State.WARN,
        "Critical": State.CRIT,
        "Unknown": State.UNKNOWN,
    }.get(health, State.UNKNOWN)

    summary = f"Status: {health}, State: {state}, Temperature: {reading} °C"
    yield Result(state=health_state, summary=summary)

    # Check temperature levels
    if reading is not None:
        yield from check_levels(
            reading,
            levels_upper=(params.get("temp_upper", 70), params.get("temp_crit", 80)),
            levels_lower=(None, None),
            metric_name="temp",
            label="Temperature",
            render_func=lambda x: f"{x:.1f} °C",
        )

register.check_plugin(
    name="rapid_thermal",
    service_name="%s",
    discovery_function=discover_rapid_thermal,
    check_function=check_rapid_thermal,
    check_default_parameters={
        "fan_lower": 1000,  # Minimum fan speed
        "fan_upper": 10000,  # Maximum fan speed
        "temp_upper": 70,  # Warning temperature
        "temp_crit": 80,  # Critical temperature
    },
    check_ruleset_name="rapid_thermal",
)
