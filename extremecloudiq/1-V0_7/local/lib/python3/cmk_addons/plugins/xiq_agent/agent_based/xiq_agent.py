# -*- coding: utf-8 -*-
from typing import Mapping, Any, Iterable

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)

# --- 1. Parser ---

def parse_xiq_login(string_table: StringTable) -> Any:
    if not string_table:
        return None
    # Wir nehmen die rohe Zeile für den Login
    return " ".join(string_table[0])

def parse_xiq_summary(string_table: StringTable) -> Any:
    if not string_table:
        return None
    return {line[0]: line[1] for line in string_table if len(line) >= 2}

def parse_xiq_ap_status(string_table: StringTable) -> Any:
    if not string_table or len(string_table[0]) < 7:
        return None
    row = string_table[0]
    return {
        "sn": row[1], "mac": row[2], "ip": row[3], "model": row[4],
        "connected": row[5] == "1", "state": row[6],
    }

# --- 2. Discovery ---

def discover_xiq_single(section: Any) -> DiscoveryResult:
    yield Service()

# --- 3. Checks ---

def check_xiq_login(section: str) -> Iterable[CheckResult]:
    if "STATUS:OK" in section:
        yield Result(state=State.OK, summary="API Login successful")
    else:
        yield Result(state=State.CRIT, summary=f"API Error: {section}")

def check_xiq_summary(section: Mapping[str, Any]) -> Iterable[CheckResult]:
    ap_count = section.get("access_points", "0")
    yield Result(state=State.OK, summary=f"Managed APs: {ap_count}")

def check_xiq_ap_status(section: Mapping[str, Any]) -> Iterable[CheckResult]:
    state = State.OK if section.get("connected") else State.CRIT
    yield Result(state=state, summary=f"Status: {section.get('state')} ({section.get('model')})")

# --- 4. Registrierung ---

agent_section_xiq_login = AgentSection(
    name="extreme_cloud_iq_login",
    parse_function=parse_xiq_login,
)

check_plugin_xiq_login = CheckPlugin(
    name="xiq_agent_login",
    sections=["extreme_cloud_iq_login"],
    service_name="Extreme Cloud IQ Login",
    discovery_function=discover_xiq_single,
    check_function=check_xiq_login,
)

agent_section_xiq_summary = AgentSection(
    name="extreme_summary",
    parse_function=parse_xiq_summary,
)

check_plugin_xiq_summary = CheckPlugin(
    name="xiq_agent_summary",
    sections=["extreme_summary"],
    service_name="Extreme Cloud Summary",
    discovery_function=discover_xiq_single,
    check_function=check_xiq_summary,
)

agent_section_xiq_ap = AgentSection(
    name="extreme_ap_status",
    parse_function=parse_xiq_ap_status,
)

check_plugin_xiq_ap = CheckPlugin(
    name="xiq_agent_ap_status",
    sections=["extreme_ap_status"],
    service_name="AP Status",
    discovery_function=discover_xiq_single,
    check_function=check_xiq_ap_status,
)