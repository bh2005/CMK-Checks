#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Downtime mit REST API - NUR für Remote-Server
Langsamer, benötigt Auth, externe Dependencies
"""

import sys
import requests
from datetime import datetime, timedelta

from cmk.notification_plugins.utils import collect_context


def main():
    raw_context = collect_context()
    
    what = raw_context.get("WHAT")
    state = raw_context.get("HOSTSTATE")
    hostname = raw_context.get("HOSTNAME")
    
    if what != "HOST":
        sys.stdout.write("Nur HOST-Events werden verarbeitet\n")
        return 0
    
    # API-Zugangsdaten
    api_url = raw_context.get("PARAMETER_API_URL", "http://localhost/site/check_mk/api/1.0")
    api_user = raw_context.get("PARAMETER_API_USER", "automation")
    api_key = raw_context.get("PARAMETER_API_KEY", "")
    
    if not api_key:
        sys.stderr.write("Kein API-Key → Abbruch\n")
        return 2
    
    headers = {
        "Authorization": f"Bearer {api_user} {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    try:
        duration_days = float(raw_context.get("PARAMETER_DURATION_DAYS", "2.0"))
    except ValueError:
        duration_days = 2.0
    
    threshold = timedelta(days=duration_days)
    
    # ========================================
    # CASE 1: HOST DOWN
    # ========================================
    if state == "DOWN":
        last_up_unix = raw_context.get("HOSTLASTUPTIME")
        
        if not last_up_unix or not last_up_unix.isdigit():
            sys.stdout.write(f"Keine gültige HOSTLASTUPTIME für {hostname}\n")
            return 0
        
        last_up = datetime.fromtimestamp(int(last_up_unix))
        now = datetime.now()
        duration = now - last_up
        
        if duration < threshold:
            sys.stdout.write(
                f"{hostname} DOWN nur {duration.days}d {duration.seconds//3600}h "
                f"< {duration_days}d → skip\n"
            )
            return 0
        
        # Flexible Downtime (sehr langes Ende = faktisch "kein Ende")
        comment = f"Auto-Downtime: Host DOWN seit > {duration_days} Tagen"
        
        payload = {
            "downtime_type": "host",
            "host_name": hostname,
            "start_time": now.isoformat(),
            "end_time": (now + timedelta(days=3650)).isoformat(),  # 10 Jahre
            "recur": "fixed",
            "comment": comment,
        }
        
        try:
            r = requests.post(
                f"{api_url}/domain-types/downtime/collections/all",
                json=payload,
                headers=headers,
                timeout=10,
            )
            r.raise_for_status()
            downtime_id = r.json().get("id", "unbekannt")
            sys.stdout.write(f"✓ Downtime für {hostname} gesetzt (ID: {downtime_id})\n")
            return 0
        except Exception as e:
            sys.stderr.write(f"✗ API-Fehler beim Setzen: {e}\n")
            return 2
    
    # ========================================
    # CASE 2: HOST UP (RECOVERY)
    # ========================================
    elif state == "UP":
        try:
            # Suche nach Downtimes
            search_url = f"{api_url}/domain-types/downtime/collections/all?host_name={hostname}"
            r = requests.get(search_url, headers=headers, timeout=10)
            r.raise_for_status()
            
            downtimes = r.json().get("value", [])
            deleted = 0
            
            for dt in downtimes:
                dt_id = dt.get("id")
                comment = dt.get("extensions", {}).get("comment", "")
                
                if "Auto-Downtime: Host DOWN seit" in comment:
                    delete_url = f"{api_url}/objects/downtime/{dt_id}"
                    requests.delete(delete_url, headers=headers, timeout=10)
                    deleted += 1
            
            if deleted > 0:
                sys.stdout.write(f"✓ {deleted} Downtime(s) entfernt für {hostname}\n")
            else:
                sys.stdout.write(f"Keine Auto-Downtimes für {hostname}\n")
            
            return 0
        except Exception as e:
            sys.stderr.write(f"✗ API-Fehler beim Löschen: {e}\n")
            return 2
    
    else:
        sys.stdout.write(f"Unbekannter HOSTSTATE: {state}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())