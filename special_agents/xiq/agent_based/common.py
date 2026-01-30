#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
import time


# ---------------------------------------------------------------------------
# Text reinigen (LLDP/CDP Felder)
# ---------------------------------------------------------------------------
def _clean_text(v: str) -> str:
    if not v:
        return ""
    return (
        str(v)
        .replace("(interface name)", "")
        .replace("(mac address)", "")
        .strip()
    )

# ---------------------------------------------------------------------------
# MAC-Addresse robust normalisieren
# ---------------------------------------------------------------------------
def format_mac(raw: str) -> str:
    """
    Universelles Normalisieren von MAC-Adressen.

    Akzeptierte Formate:
      - 4C231A0403D5
      - 4c:23:1a:04:03:d5
      - 4C-23-1A-04-03-D5
      - 4C23.1A04.03D5
      - 4C231A0403D55               (XIQ liefert manchmal 13 Bytes!)
      - 4C:C2:23:31:1A:A0:04:40:03:3D:D5:5  (komplett kaputter API-Wert)

    Rueckgabe:
      Eine 6-Byte MAC im Format AA:BB:CC:DD:EE:FF
      oder der Rohwert, wenn nicht interpretierbar.
    """

    if not raw:
        return ""

    # Nur Hex-Zeichen behalten (0-9, A-F)
    cleaned = "".join(c for c in raw.upper() if c in "0123456789ABCDEF")

    # Zu kurz ? nicht interpretierbar
    if len(cleaned) < 12:
        return raw

    # Zu lang ? XIQ liefert manchmal 13–20 Hex-Zeichen ? auf echte MAC (12 Hex) kürzen
    cleaned = cleaned[:12]

    # In XX:XX:XX:XX:XX:XX formatieren
    return ":".join(cleaned[i:i+2] for i in range(0, 12, 2))

# ---------------------------------------------------------------------------
# Uptime-Kürzel
# ---------------------------------------------------------------------------
def _fmt_uptime(seconds: int) -> str:
    s = max(0, int(seconds or 0))
    d, rem = divmod(s, 86400)
    h, rem = divmod(rem, 3600)
    m, _ = divmod(rem, 60)
    return f"{d}d {h}h {m}m"


# ---------------------------------------------------------------------------
# Uptime aus API interpretieren
# ---------------------------------------------------------------------------
def _uptime_from_input(boot_ts_or_uptime) -> int:
    try:
        v = int(boot_ts_or_uptime)
    except Exception:
        return 0

    if v <= 0:
        return 0

    now = time.time()

    # Millisekunden Timestamp
    if v > 10_000_000_000:
        return max(0, int(now - (v / 1000.0)))

    # Sekunden Timestamp (UNIX)
    if 1_000_000_000 <= v <= 4_000_000_000:
        return max(0, int(now - v))

    # Plausible seconds uptime < 5 Jahre
    if v < 5 * 365 * 24 * 3600:
        return v

    return v


# ---------------------------------------------------------------------------
# Sicheres int
# ---------------------------------------------------------------------------
def _to_int_safe(v: Any, default: int = 0) -> int:
    try:
        if v is None:
            return default
        if isinstance(v, (int, float)):
            return int(v)
        s = str(v).strip()
        if not s:
            return default
        digits = "".join(ch for ch in s if (ch.isdigit() or ch == "-"))
        if digits in ("", "-"):
            return default
        return int(digits)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# Location Kürzen (LOCxxx)
# ---------------------------------------------------------------------------
def _shorten_location_to_loc_leaf(loc: str) -> str:
    if not loc:
        return ""
    parts = [p.strip() for p in loc.split("/") if p.strip()]
    for part in reversed(parts):
        up = part.upper()
        if "LOC" in up:
            idx = up.rfind("LOC")
            return up[idx:]
    return parts[-1] if parts else ""


def extract_location_leaf(loc: str) -> str:
    return _shorten_location_to_loc_leaf(loc)


# ---------------------------------------------------------------------------
# Connected normalisieren
# ---------------------------------------------------------------------------
def norm_connected(val: Any) -> bool:
    """Normalisiert diverse Felder (1/0, yes/no, CONNECTED/DISCONNECTED, usw.) zu bool."""
    if val is None:
        return False
    v = str(val).strip().upper()
    if v in ("1", "TRUE", "YES", "Y", "CONNECTED", "ONLINE"):
        return True
    if v in ("0", "FALSE", "NO", "N", "DISCONNECTED", "OFFLINE"):
        return False
    try:
        return bool(int(v))
    except Exception:
        return False