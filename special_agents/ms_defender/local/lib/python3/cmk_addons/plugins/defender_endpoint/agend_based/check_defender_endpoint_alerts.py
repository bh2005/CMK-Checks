#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check-Plugin: Microsoft Defender for Endpoint Alerts
Ablage: ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/agent_based/defender_endpoint_alerts.py

Erzeugt:
  - "Defender Alerts Summary"    → Gesamtübersicht
  - "Defender Host <Hostname>"   → Ein Service pro betroffenem Host
"""

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
)
from typing import Any


# ---------------------------------------------------------------------------
# Typdefinitionen
# ---------------------------------------------------------------------------

Section = dict  # {"summary": {...}, "alerts": [...], "by_host": {...}}


# ---------------------------------------------------------------------------
# Severity-Mapping
# ---------------------------------------------------------------------------

SEVERITY_STATE = {
    "High":          State.CRIT,
    "Medium":        State.WARN,
    "Low":           State.OK,
    "Informational": State.OK,
}

SEVERITY_ICON = {
    "High":          "🔴",
    "Medium":        "🟡",
    "Low":           "🟢",
    "Informational": "ℹ️",
}


# ---------------------------------------------------------------------------
# Parse-Funktion
# ---------------------------------------------------------------------------

def parse_defender_endpoint_alerts(string_table: StringTable) -> Section:
    parsed: Section = {
        "summary":  {"high": 0, "medium": 0, "low": 0, "informational": 0, "total": 0},
        "alerts":   [],
        "by_host":  {},
    }

    for line in string_table:
        if not line:
            continue
        record_type = line[0]

        if record_type == "SUMMARY" and len(line) >= 6:
            parsed["summary"] = {
                "high":          int(line[1]),
                "medium":        int(line[2]),
                "low":           int(line[3]),
                "informational": int(line[4]),
                "total":         int(line[5]),
            }

        elif record_type == "ALERT" and len(line) >= 10:
            alert = {
                "id":          line[1],
                "severity":    line[2],
                "status":      line[3],
                "host":        line[4],
                "title":       line[5],
                "category":    line[6],
                "age":         line[7],
                "mitre":       line[8],
                "threat_name": line[9] if len(line) > 9 else "",
            }
            parsed["alerts"].append(alert)
            host = alert["host"]
            parsed["by_host"].setdefault(host, []).append(alert)

    return parsed


agent_section_defender_endpoint_alerts = AgentSection(
    name="defender_endpoint_alerts",
    parse_function=parse_defender_endpoint_alerts,
)


# ---------------------------------------------------------------------------
# Service 1: Übersichts-Service
# ---------------------------------------------------------------------------

def discover_defender_summary(section: Section) -> DiscoveryResult:
    if section:
        yield Service(item="Summary")


def check_defender_summary(item: str, params: dict, section: Section) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="Keine Daten vom Special Agent")
        return

    s     = section["summary"]
    high  = s.get("high", 0)
    med   = s.get("medium", 0)
    low   = s.get("low", 0)
    info  = s.get("informational", 0)
    total = s.get("total", 0)

    # Schwellwerte aus WATO-Regel (mit Defaults)
    warn_high   = params.get("warn_high",   1)
    crit_high   = params.get("crit_high",   1)
    warn_medium = params.get("warn_medium", 1)
    crit_medium = params.get("crit_medium", 5)

    if high >= crit_high:
        state = State.CRIT
    elif high >= warn_high or med >= crit_medium:
        state = State.WARN
    elif med >= warn_medium:
        state = State.WARN
    else:
        state = State.OK

    yield Result(
        state=state,
        summary=(
            f"Gesamt: {total} | "
            f"🔴 High: {high} | "
            f"🟡 Medium: {med} | "
            f"🟢 Low: {low} | "
            f"ℹ️ Info: {info}"
        ),
    )

    yield Metric("defender_alerts_high",   high)
    yield Metric("defender_alerts_medium", med)
    yield Metric("defender_alerts_low",    low)
    yield Metric("defender_alerts_total",  total)

    # Details: kritische Alerts auflisten
    critical = [a for a in section["alerts"] if a["severity"] in ("High", "Medium")]
    if critical:
        details = "\nKritische Alerts:\n" + "\n".join([
            f"  {SEVERITY_ICON.get(a['severity'], '')} {a['host']} – "
            f"{a['title']} (seit {a['age']})"
            for a in critical[:20]
        ])
        yield Result(state=State.OK, notice=details)


check_plugin_defender_endpoint_alerts_summary = CheckPlugin(
    name="defender_endpoint_alerts_summary",
    sections=["defender_endpoint_alerts"],
    service_name="Defender Alerts %s",
    discovery_function=discover_defender_summary,
    check_function=check_defender_summary,
    check_default_parameters={
        "warn_high":   1,
        "crit_high":   1,
        "warn_medium": 1,
        "crit_medium": 5,
    },
    check_ruleset_name="defender_endpoint_alerts",
)


# ---------------------------------------------------------------------------
# Service 2: Pro-Host-Service
# ---------------------------------------------------------------------------

def discover_defender_by_host(section: Section) -> DiscoveryResult:
    for hostname in section.get("by_host", {}):
        yield Service(item=hostname)


def check_defender_by_host(item: str, params: dict, section: Section) -> CheckResult:
    alerts = section.get("by_host", {}).get(item)

    if not alerts:
        yield Result(state=State.OK, summary="Keine aktiven Alerts")
        return

    # Schwersten State bestimmen
    worst = State.OK
    for a in alerts:
        s = SEVERITY_STATE.get(a["severity"], State.OK)
        if s.value > worst.value:
            worst = s

    high_c = sum(1 for a in alerts if a["severity"] == "High")
    med_c  = sum(1 for a in alerts if a["severity"] == "Medium")
    low_c  = sum(1 for a in alerts if a["severity"] == "Low")

    parts = []
    if high_c: parts.append(f"🔴 {high_c}x High")
    if med_c:  parts.append(f"🟡 {med_c}x Medium")
    if low_c:  parts.append(f"🟢 {low_c}x Low")

    yield Result(
        state=worst,
        summary=f"{len(alerts)} Alert(s): " + ", ".join(parts),
    )

    # Details: ein Result pro Alert
    for a in sorted(alerts, key=lambda x: x["severity"]):
        icon        = SEVERITY_ICON.get(a["severity"], "")
        mitre_info  = f" | MITRE: {a['mitre']}"  if a["mitre"]       else ""
        threat_info = f" | Threat: {a['threat_name']}" if a["threat_name"] else ""

        yield Result(
            state=SEVERITY_STATE.get(a["severity"], State.OK),
            notice=(
                f"{icon} {a['title']} | Status: {a['status']} | "
                f"Kategorie: {a['category']} | Alter: {a['age']}"
                f"{mitre_info}{threat_info}"
            ),
        )

    yield Metric("defender_host_alerts", len(alerts))


check_plugin_defender_endpoint_alerts_by_host = CheckPlugin(
    name="defender_endpoint_alerts_by_host",
    sections=["defender_endpoint_alerts"],
    service_name="Defender Host %s",
    discovery_function=discover_defender_by_host,
    check_function=check_defender_by_host,
    check_default_parameters={},
)