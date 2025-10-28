#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import argparse
import sys
import time

# Nagios Exit Codes
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

# --- Konfiguration ---
API_BASE_URL = "https://api.extremecloudiq.com"
API_ENDPOINT = f"{API_BASE_URL}/devices" # Beliebiger GET-Endpunkt

def check_xiq_api_limits(token, warning_percent, critical_percent):
    """
    Führt einen API-Aufruf durch und prüft die Rate Limits für Nagios.
    """
    if not token:
        print(f"UNKNOWN: API-Token fehlt.")
        return STATE_UNKNOWN

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    status_code = STATE_OK
    status_text = "OK"
    perf_data = ""

    try:
        # Führe den GET-Request durch
        response = requests.get(API_ENDPOINT, headers=headers, timeout=10)

        # ------------------------------------------------
        # 1. API-Status prüfen (Timeout, Server-Fehler)
        # ------------------------------------------------
        if response.status_code == 429:
            # Spezieller Fall: Limit bereits überschritten
            status_code = STATE_CRITICAL
            status_text = "CRITICAL - Rate Limit Überschritten (429)"
            
            limit_remaining = int(response.headers.get("RateLimit-Remaining", 0))
            limit_reset = int(response.headers.get("RateLimit-Reset", 0))
            
            print(f"{status_text}: Verbleibende Anfragen: {limit_remaining}. Reset in {limit_reset}s. | remaining={limit_remaining};;; reset={limit_reset}s")
            return status_code

        elif not 200 <= response.status_code < 300:
            status_code = STATE_UNKNOWN
            status_text = f"UNKNOWN - API Fehler: HTTP Status {response.status_code}"
            print(f"{status_text}. | status_code={response.status_code}")
            return status_code

        # ------------------------------------------------
        # 2. Rate-Limit-Header auslesen und Metriken berechnen
        # ------------------------------------------------
        
        # Werte aus den Headern abrufen
        limit_limit_str = response.headers.get("RateLimit-Limit")
        limit_remaining_str = response.headers.get("RateLimit-Remaining")
        limit_reset_str = response.headers.get("RateLimit-Reset")
        
        if not (limit_limit_str and limit_remaining_str and limit_reset_str):
            status_code = STATE_UNKNOWN
            print(f"UNKNOWN: Rate-Limit-Header fehlen in der Antwort.")
            return status_code

        # Limit-Wert parsen (z.B. "7500;w=3600")
        try:
            max_requests = int(limit_limit_str.split(';')[0])
            remaining_requests = int(limit_remaining_str)
            reset_seconds = int(limit_reset_str)
        except ValueError:
            status_code = STATE_UNKNOWN
            print(f"UNKNOWN: Konnte Rate-Limit-Werte nicht parsen. Header-Werte: {limit_limit_str}, {limit_remaining_str}")
            return status_code

        # Berechnung der Nutzung in Prozent
        usage_percent = round((1 - (remaining_requests / max_requests)) * 100, 2)
        remaining_percent = round((remaining_requests / max_requests) * 100, 2)
        
        # ------------------------------------------------
        # 3. Schwellenwerte prüfen
        # ------------------------------------------------

        # CRITICAL-Schwellenwert prüfen (Basis: Verbleibende Anfragen in Prozent)
        if remaining_percent <= critical_percent:
            status_code = STATE_CRITICAL
            status_text = "CRITICAL"
        # WARNING-Schwellenwert prüfen
        elif remaining_percent <= warning_percent:
            status_code = STATE_WARNING
            status_text = "WARNING"
        else:
            status_code = STATE_OK
            status_text = "OK"

        # ------------------------------------------------
        # 4. Ausgabe für Nagios formatieren (Einzeiler + Performance Data)
        # ------------------------------------------------
        
        # Hauptausgabe
        output_message = (
            f"{status_text} - API Limit: {remaining_requests} Anfragen ({remaining_percent:.2f}%) verbleibend "
            f"(Genutzt: {usage_percent:.2f}%). Reset in {reset_seconds}s."
        )

        # Performance Data (wichtig für Graphen)
        # Format: 'label'=wertUOM;warn;crit;min;max
        perf_data = (
            f"'remaining_requests'={remaining_requests};{int(max_requests * warning_percent / 100)};{int(max_requests * critical_percent / 100)};0;{max_requests} "
            f"'remaining_percent'={remaining_percent:.2f}%;{warning_percent};{critical_percent};0;100 "
            f"'reset_seconds'={reset_seconds}s;;"
        )
        
        print(f"{output_message}|{perf_data}")
        return status_code

    except requests.exceptions.Timeout:
        print(f"CRITICAL: API-Verbindung Timeout nach 10 Sekunden. | status_code=2")
        return STATE_CRITICAL
    except requests.exceptions.RequestException as e:
        print(f"UNKNOWN: Verbindungs- oder Request-Fehler: {e}. | status_code=3")
        return STATE_UNKNOWN
    except Exception as e:
        print(f"UNKNOWN: Ein unerwarteter Fehler ist aufgetreten: {e}. | status_code=3")
        return STATE_UNKNOWN


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nagios Check für ExtremeCloud IQ API Rate Limit.")
    parser.add_argument("-t", "--token", required=True, help="Der ExtremeCloud IQ API Access Token (P-Key).")
    # Schwellenwerte werden auf den PROZENTSATZ DER VERBLEIBENDEN ANFRAGEN angewandt.
    # z.B.: -w 20 bedeutet WARNING, wenn weniger als 20% der Anfragen verbleiben (80% genutzt)
    parser.add_argument("-w", "--warning", type=float, default=20.0, help="Schwellenwert (Prozent der verbleibenden Anfragen) für WARNING. Standard: 20%%")
    parser.add_argument("-c", "--critical", type=float, default=5.0, help="Schwellenwert (Prozent der verbleibenden Anfragen) für CRITICAL. Standard: 5%%")

    args = parser.parse_args()
    
    # Stellen Sie sicher, dass die Schwellenwerte für Nagios Sinn ergeben (W > C)
    if args.warning < args.critical:
        # Nagios-Konvention: Warning muss "besser" sein als Critical (d.h. höher)
        # Hier ist ein niedrigerer Wert KRITISCHER. Wir tauschen sie für die Logik.
        args.warning, args.critical = args.critical, args.warning

    exit_code = check_xiq_api_limits(args.token, args.warning, args.critical)
    sys.exit(exit_code)