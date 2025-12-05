#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XIQ Redis Client
Holt Geräte aus Redis mit flexiblen Filtern:
  --filter-ip               → nur Geräte mit IP-Adresse (nicht None/leer)
  -m --managed_by           → exakter Match auf "managed_by" Feld
  -l --location-part        → Teilstring in Location (z.B. "Berlin", "Office")
  --hostname-filter         → Teilstring in Hostname
  --device-function         → z.B. "AP", "SWITCH", "ROUTER"
"""
import argparse
import json
import sys
from typing import List, Dict, Any, Optional

import redis


# ─── Konfiguration (anpassen falls nötig) ─────────────────────────────────────
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 3
KEY_PATTERN = "ap:*"           # oder "device:*" – je nach deinem Sync-Script
IP_FIELD = "ip_address"        # mögliche Alternativen: current_ip, mgmt_ip
# ─────────────────────────────────────────────────────────────────────────────


def get_redis_client(host: str, port: int, db: int) -> redis.Redis:
    r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    try:
        r.ping()
    except redis.ConnectionError:
        print("<<<check_mk>>>\nSection:redis_connection\n0 \"Redis connection\" - Redis unreachable", file=sys.stderr)
        sys.exit(1)
    return r


def load_all_devices(r: redis.Redis, pattern: str) -> List[Dict[str, Any]]:
    """Lädt alle Geräte aus Redis (SCAN statt KEYS für große DBs)."""
    devices = []
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, match=pattern, count=200)
        for key in keys:
            data = r.hgetall(key)
            if not data:
                continue
            # Falls du im Sync-Script JSON als String speicherst → parsen
            if "json" in data:
                try:
                    data = json.loads(data["json"])
                except json.JSONDecodeError:
                    continue
            devices.append({"key": key, "data": data})
        if cursor == 0:
            break
    return devices


def device_matches(device: Dict[str, Any],
                  ip_field: str,
                  filter_ip: bool,
                  managed_by: Optional[str],
                  location_part: Optional[str],
                  hostname_part: Optional[str],
                  device_function: Optional[str]) -> bool:
    """Prüft, ob ein Gerät alle aktiven Filter erfüllt."""
    d = device["data"]

    # IP-Filter
    if filter_ip:
        ip = d.get(ip_field, "").strip()
        if not ip or ip.lower() in {"none", "null", ""}:
            return False

    # managed_by exakter Match
    if managed_by is not None:
        if d.get("managed_by", "").strip() != managed_by.strip():
            return False

    # Location enthält Teilstring (case-insensitive)
    if location_part is not None:
        loc = d.get("location", "") or d.get("location_name", "") or ""
        if location_part.lower() not in loc.lower():
            return False

    # Hostname enthält Teilstring (case-insensitive)
    if hostname_part is not None:
        hn = d.get("hostname", "") or ""
        if hostname_part.lower() not in hn.lower():
            return False

    # device_function exakter Match
    if device_function is not None:
        if d.get("device_function", "").upper() != device_function.upper():
            return False

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="XIQ → Redis Client für CheckMK mit Filtern")
    parser.add_argument("--redis-host", default=REDIS_HOST, help=f"Redis Host (default: {REDIS_HOST})")
    parser.add_argument("--redis-port", type=int, default=REDIS_PORT, help=f"Redis Port (default: {REDIS_PORT})")
    parser.add_argument("--redis-db", type=int, default=REDIS_DB, help=f"Redis DB (default: {REDIS_DB})")
    parser.add_argument("--key-pattern", default=KEY_PATTERN, help=f"Key-Pattern (default: {KEY_PATTERN})")
    parser.add_argument("--ip-field", default=IP_FIELD, help=f"Feldname für IP-Adresse (default: {IP_FIELD})")

    # ─── Filter-Argumente ──────────────────────
    redis_group = parser.add_argument_group("Filter-Optionen")
    redis_group.add_argument("--filter-ip", action="store_true",
                             help="Nur Geräte mit gültiger IP-Adresse zurückgeben")
    redis_group.add_argument("-m", "--managed_by", dest="managed_by_value",
                             help="Exakter Wert für Feld 'managed_by'")
    redis_group.add_argument("-l", "--location-part", dest="location_name_part",
                             help="Teilstring in Location (z.B. 'Berlin', 'Office')")
    redis_group.add_argument("--hostname-filter", dest="hostname_value",
                             help="Teilstring in Hostname")
    redis_group.add_argument("--device-function", dest="device_function",
                             help="z.B. AP, SWITCH, ROUTER")

    # ─── Output-Optionen ───────────────────────
    parser.add_argument("--json", action="store_true", help="Ausgabe als kompakte JSON-Zeile (CheckMK-kompatibel)")
    parser.add_argument("--pretty", action="store_true", help="Schön formatierter JSON-Output (zum Debuggen)")

    args = parser.parse_args()

    r = get_redis_client(args.redis_host, args.redis_port, args.redis_db)
    all_devices = load_all_devices(r, args.key_pattern)

    filtered_devices = [
        dev for dev in all_devices
        if device_matches(
            dev,
            ip_field=args.ip_field,
            filter_ip=args.filter_ip,
            managed_by=args.managed_by_value,
            location_part=args.location_name_part,
            hostname_part=args.hostname_value,
            device_function=args.device_function,
        )
    ]

    # CheckMK-kompatible Ausgabe
    if args.json or not args.pretty:
        # Eine Zeile → perfekt für Special Agent
        print(json.dumps([dev["data"] for dev in filtered_devices]))
    else:
        # Schön lesbar (für manuelles Testen)
        print(json.dumps([dev["data"] for dev in filtered_devices], indent=2, ensure_ascii=False))

    # Optional: Performance-Daten für CheckMK
    total = len(all_devices)
    shown = len(filtered_devices)
    print(f"P redis_xiq_devices total={total} shown={shown};;;0", file=sys.stderr)


if __name__ == "__main__":
    main()