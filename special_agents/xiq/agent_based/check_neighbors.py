# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterable, Mapping, Any, List, Set
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

# Erwartete Section-Struktur: Liste von Dicts mit Keys:
# - "hostname"
# - "local_port"
# - "remote_device" oder "remote_name"
# - "remote_port"
# - "management_ip"
# - "mac_address" oder "remote_mac"
# - "port_description"
# Wichtig: Die Keys muessen zum Parser in sections.py passen!


def discover_xiq_ap_neighbors(section) -> DiscoveryResult:
    """Ein Service pro AP (item = hostname) basierend auf der Neighbor-Section."""
    if not section:
        return
    seen: Set[str] = set()
    for e in section:
        host = (e.get("hostname") or "").strip()
        if not host or host in seen:
            continue
        seen.add(host)
        yield Service(item=host)


def _norm_mac(entry: Mapping[str, Any]) -> str:
    """Liefert MAC-Adresse aus mac_address oder remote_mac."""
    mac = entry.get("mac_address")
    if mac:
        return str(mac)
    mac = entry.get("remote_mac")
    if mac:
        return str(mac)
    return "-"


def check_xiq_ap_neighbors(
    item: str,
    params: Mapping[str, Any],
    section,
) -> Iterable[CheckResult]:
    """Kurz-Summary + Long-Details. Niemals nur details ohne summary!"""
    # Keine Daten vorhanden
    if not section:
        yield Result(state=State.OK, summary=f"{item}: keine Nachbarn gemeldet")
        return

    # Nur Zeilen fuer dieses Item (Hostname)
    rows = [e for e in section if ((e.get("hostname") or "").strip() == item)]
    if not rows:
        yield Result(state=State.OK, summary=f"{item}: keine Nachbarn gefunden")
        return

    # Parametrisierung: Felder, Labels, Limit
    fields: List[str] = (params or {}).get("fields") or [
        "local_port",
        "remote_device",
        "remote_port",
        "management_ip",
        "mac_address",
        "port_description",
    ]
    labels = {
        "local_port": "Local Port",
        "remote_device": "Remote Device",
        "remote_name": "Remote Device",
        "remote_port": "Remote Port",
        "management_ip": "Management IP",
        "mac_address": "Remote MAC",
        "remote_mac": "Remote MAC",
        "port_description": "Port Description",
    }
    limit = int((params or {}).get("neighbor_limit", 0))  # 0 = alle

    # Sortierung stabil halten, auch wenn Keys fehlen
    rows.sort(
        key=lambda e: (
            e.get("local_port", "") or "",
            e.get("remote_device", "") or e.get("remote_name", "") or "",
            e.get("remote_port", "") or "",
        )
    )

    # --- IMMER zuerst ein kompaktes Summary ---
    count = len(rows)
    first = rows[0]
    first_remote = first.get("remote_device") or first.get("remote_name") or "-"
    first_local = first.get("local_port") or "-"
    first_remote_port = first.get("remote_port") or "-"
    yield Result(
        state=State.OK,
        summary=f"LLDP/CDP: {count} Nachbar(e), erster: {first_local} -> {first_remote} ({first_remote_port})",
    )

    # --- Long Output ---
    out_lines: List[str] = ["**Nachbarn (LLDP/CDP)**"]
    emitted = 0
    for e in rows:
        if limit and emitted >= limit:
            break

        # Pro Eintrag alle gewuenschten Felder ausgeben
        for k in fields:
            if k in ("mac_address", "remote_mac"):
                v = _norm_mac(e)
            elif k == "remote_device":
                v = e.get("remote_device") or e.get("remote_name")
            else:
                v = e.get(k)

            if v not in (None, ""):
                out_lines.append(f"- {labels.get(k, k)}: {v}")

        out_lines.append("")  # Leerzeile zwischen Nachbarn
        emitted += 1

    details = "\n".join(out_lines).rstrip()

    # Niemals nur details ohne summary: Fuege hier IMMER ein notice hinzu.
    yield Result(
        state=State.OK,
        notice="LLDP/CDP: Details im Langtext",
        details=details,
    )


check_plugin_xiq_ap_neighbors = CheckPlugin(
    name="xiq_ap_neighbors",
    sections=["extreme_device_neighbors"],
    service_name="XIQ AP %s Neighbors",
    discovery_function=discover_xiq_ap_neighbors,
    check_function=check_xiq_ap_neighbors,
    check_default_parameters={
        "fields": [
            "local_port",
            "remote_device",
            "remote_port",
            "management_ip",
            "mac_address",
            "port_description",
        ],
        "neighbor_limit": 0,
    },
    check_ruleset_name="xiq_ap_neighbors_presentation",
)
