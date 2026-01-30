# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Mapping, Any, Iterable, Tuple
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
)

# Dieser Check erwartet die Uptime in der Section "extreme_ap_status".
# Mögliche Felder:
#   - "uptime"              (Sekunden oder Millisekunden)
#   - "uptime_seconds"      (Sekunden)
#   - "uptime_ms"           (Millisekunden)
#   - String-Form: "1d 2h 3m 4s", "2h 5m", "45m", "30s"
#
# Service: "XIQ AP Uptime" (ein Service pro Piggyback-AP-Host)


def discover_xiq_ap_uptime(section: Mapping[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def _parse_uptime_to_seconds(raw: Any) -> int:
    """Versucht, Uptime auf Sekunden zu normalisieren."""
    if raw is None:
        return 0

    # Zahlen als Sekunden/Millisekunden
    # - direkte int/float
    try:
        # float erlaubt String-Zahlen wie "12345.0"
        val = float(raw)
        if val <= 0:
            return 0
        # Heuristik: sehr große Werte können Millisekunden sein
        # > 10 Jahre in Sekunden ist unrealistisch => ms
        # (10 Jahre ~ 315360000 s)
        if val > 315360000:
            return int(val / 1000.0)
        return int(val)
    except Exception:
        pass

    # Spezifische bekannte Felder-Varianten
    # Falls raw ein Mapping ist (manche APIs verschachteln)
    if isinstance(raw, dict):
        for k in ("uptime_seconds", "seconds", "value", "uptime"):
            if k in raw:
                return _parse_uptime_to_seconds(raw[k])
        if "uptime_ms" in raw:
            return int(float(raw["uptime_ms"]) / 1000.0)

    # String-Parsing: "1d 2h 3m 4s", "2h 5m", "45m", "30s"
    if isinstance(raw, str):
        s = raw.strip().lower()
        if not s:
            return 0

        # Falls es eine reine Zahl als String ist
        try:
            val = float(s)
            if val > 315360000:
                return int(val / 1000.0)
            return int(val)
        except Exception:
            pass

        total = 0
        num = ""
        for ch in s:
            if ch.isdigit():
                num += ch
                continue
            # Trennzeichen oder Einheiten verarbeiten
            if num:
                try:
                    v = int(num)
                except Exception:
                    v = 0
                if ch == "d":
                    total += v * 86400
                    num = ""
                    continue
                if ch == "h":
                    total += v * 3600
                    num = ""
                    continue
                if ch == "m":
                    total += v * 60
                    num = ""
                    continue
                if ch == "s":
                    total += v
                    num = ""
                    continue
                # Sonstiger Separator (z. B. Leerzeichen, /, :)
                # lasse num stehen, falls noch Einheit folgt
            # ignorierbare Zeichen: Leerzeichen, Kommas etc.
        # Falls am Ende noch eine Zahl ohne Einheit übrig bleibt, nimm Sekunden
        if num:
            try:
                total += int(num)
            except Exception:
                pass
        return total

    # Fallback
    return 0


def _fmt_dhms(secs: int) -> str:
    """Formatiert Sekunden als 'Xd Yh Zm Ws' (ohne 0-Anteile)."""
    if secs <= 0:
        return "0s"
    d, r = divmod(secs, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s and not parts:
        # Wenn alles andere 0 ist, zeige Sekunden
        parts.append(f"{s}s")
    return " ".join(parts) if parts else "0s"


def _evaluate_levels(uptime_s: int, warn_min: int, crit_min: int) -> Tuple[State, str]:
    """Bewertet minimale Uptime-Schwellen. Niedriger als Schwellwert -> WARN/CRIT."""
    # Beachte: Kleinere Werte sind schlechter (frischer Reboot)
    if uptime_s <= 0:
        return State.UNKNOWN, "keine Uptime-Daten"
    if uptime_s < crit_min:
        return State.CRIT, f"uptime { _fmt_dhms(uptime_s) } < crit { _fmt_dhms(crit_min) }"
    if uptime_s < warn_min:
        return State.WARN, f"uptime { _fmt_dhms(uptime_s) } < warn { _fmt_dhms(warn_min) }"
    return State.OK, f"uptime { _fmt_dhms(uptime_s) }"


def check_xiq_ap_uptime(
    params: Mapping[str, Any],
    section: Mapping[str, Any],
) -> Iterable[CheckResult]:
    if not section:
        yield Result(state=State.UNKNOWN, summary="Keine Uptime-Daten vorhanden")
        return

    # Schwellwerte (minimale Uptime) – Standard: WARN < 6h, CRIT < 1h
    warn_min = int((params or {}).get("min_uptime_warn", 6 * 3600))
    crit_min = int((params or {}).get("min_uptime_crit", 1 * 3600))

    # Quellen prüfen: bevorzugt "uptime_seconds", dann "uptime", dann "uptime_ms"
    raw = (
        section.get("uptime_seconds")
        or section.get("uptime")
        or section.get("uptime_ms")
        or section.get("ap_uptime")
    )

    uptime_s = _parse_uptime_to_seconds(raw)
    state, msg = _evaluate_levels(uptime_s, warn_min, crit_min)

    # Summary + Metrik
    yield Result(state=state, summary=msg)
    if uptime_s >= 0:
        yield Metric("uptime", uptime_s)


check_plugin_xiq_ap_uptime = CheckPlugin(
    name="xiq_ap_uptime",
    sections=["extreme_ap_status"],  # muss zur AP-Status-Section passen
    service_name="XIQ AP Uptime",
    discovery_function=discover_xiq_ap_uptime,
    check_function=check_xiq_ap_uptime,
    check_default_parameters={
        "min_uptime_warn": 6 * 3600,  # 6h
        "min_uptime_crit": 1 * 3600,  # 1h
    },
    check_ruleset_name="xiq_ap_uptime_levels",
)
