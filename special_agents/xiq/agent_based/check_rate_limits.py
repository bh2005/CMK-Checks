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

def discover_rate_limits(section: Mapping[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()

def check_xiq_rate_limits(section: Mapping[str, Any]) -> Iterable[CheckResult]:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No API rate limit data")
        return

    s = section.get("state")
    if s == "UNLIMITED":
        yield Result(state=State.OK, summary="API has no rate limit headers")
        return

    if s == "NO_RESPONSE":
        yield Result(state=State.CRIT, summary="No HTTP response from XIQ API")
        return

    limit    = section.get("limit") or 0
    rem      = section.get("remaining") or 0
    reset    = section.get("reset_in_seconds") or 0
    window_s = section.get("window_s") or 0
    status   = section.get("status_code")

    # Threshold logic
    state = State.OK
    try:
        if rem and limit:
            ratio = float(rem) / float(limit)
            if ratio < 0.05:
                state = State.CRIT
            elif ratio < 0.10:
                state = State.WARN
    except Exception:
        pass

    # Summary text
    summary = f"Remaining {rem}/{limit}, window {window_s}s"
    yield Result(state=state, summary=summary)

    # --- ONLY TWO METRICS ---
    yield Metric("xiq_api_remaining", rem)
    yield Metric("xiq_api_limit", limit)

check_plugin_xiq_rate_limits = CheckPlugin(
    name="xiq_rate_limits",
    sections=["extreme_cloud_iq_rate_limits"],
    service_name="XIQ API Rate Limits",
    discovery_function=discover_rate_limits,
    check_function=check_xiq_rate_limits,
)
