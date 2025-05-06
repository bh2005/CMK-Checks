#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import time
import urllib3
import ssl
from typing import Dict, Tuple, Optional
import json

# Deaktiviert nur die InsecureRequestWarning, nicht die gesamte SSL-Prüfung
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Mapping der KISTERS Statuscodes zu CheckMK Status und Text
KISTERS_STATUS_MAPPING: Dict[str, Tuple[str, str]] = {
    "2": ("OK", "Wert ist im normalen Bereich"),
    "1": ("WARN", "Wert liegt im Warnbereich"),
    # Füge hier weitere Mappings nach Bedarf hinzu
}

# Pfad zum Zertifikatsordner
CERT_PATH = '/usr/local/share/ca-certificates/'
PROXY_URL = 'YOUR-PROXY:80'
BASE_URL = 'REST_URL'

def create_ssl_context() -> ssl.SSLContext:
    """Erstellt einen sicheren SSL-Kontext mit Zertifikatsprüfung"""
    context = ssl.create_default_context()
    context.load_verify_locations(capath=CERT_PATH)
    return context

def login(session: requests.Session, user: str, password: str) -> bool:
    """Führt den Login durch und gibt Erfolgsstatus zurück"""
    try:
        url = f"{BASE_URL}/auth/login"
        data = {"userName": user, "password": password}
        response = session.post(url, json=data, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"CRITICAL - Login fehlgeschlagen: {e}")
        return False

def time_response(response, *args, **kwargs):
    response.elapsed = response.elapsed.total_seconds()

def get_current_data(session: requests.Session, variable_id: str = "253_0") -> Optional[Tuple[Dict, float]]:
    """Holt die aktuellen Daten für eine Variable und misst die Antwortzeit mit einem Hook"""
    try:
        url = f"{BASE_URL}/procos/dataSources/1/variables/{variable_id}/current"
        response = session.get(url, timeout=10, hooks={'response': time_response})
        response.raise_for_status()
        return response.json(), response.elapsed
    except requests.exceptions.RequestException:
        return None, None

def main():
    if len(sys.argv) < 3:
        print("UNKNOWN - Usage: script.py <benutzername> <passwort>")
        sys.exit(3)

    user, passw = sys.argv[1], sys.argv[2]

    # Konfiguration mit explizitem Proxy und SSL
    session = requests.Session()
    session.proxies = {
        'http': PROXY_URL,
        'https': PROXY_URL,
    }
    session.verify = CERT_PATH  # Aktiviere Zertifikatsprüfung

    # 1. Login durchführen
    if not login(session, user, passw):
        sys.exit(2)

    # 2. Daten abfragen
    data, response_time = get_current_data(session)
    if not data:
        print("CRITICAL - Datenabfrage fehlgeschlagen")
        sys.exit(2)

    try:
        # 3. Daten verarbeiten
        pvId = data.get('pvId', 'N/A')
        value = round(data['valueObject']['value'], 2)
        status_code = str(data['valueObject']['status'])
        last_change_str = data.get('lastChange', 'N/A')
        last_change_adjusted = 'N/A'

        if last_change_str != 'N/A':
            try:
                from datetime import datetime, timedelta
                last_change_dt = datetime.fromisoformat(last_change_str.replace('Z', '+00:00'))
                last_change_adjusted = (last_change_dt + timedelta(hours=2)).isoformat(timespec='seconds')
            except ValueError:
                print(f"UNKNOWN - Fehler beim Parsen des Zeitstempels: {last_change_str}")

        checkmk_status, status_text = KISTERS_STATUS_MAPPING.get(
            status_code,
            ("UNKNOWN", f"Unbekannter Statuscode: {status_code}")
        )

        # 4. Ausgabe für CheckMK
        print(f"{checkmk_status} - KISTERS {pvId}: {status_text}, "
              f"Wert={value} MW, Letzte Änderung={last_change_adjusted}, Antwortzeit={response_time:.3f}s | "
              f"value={value}MW;0;0 response_time={response_time:.3f}s;0;0\n"
              f"<<<\n{json.dumps(data, indent=2)}\n>>>")

        # Exit-Code basierend auf Status
        exit_codes = {"OK": 0, "WARN": 1, "CRIT": 2}
        sys.exit(exit_codes.get(checkmk_status, 3))

    except (KeyError, ValueError) as e:
        print(f"UNKNOWN - Fehler beim Parsen der Daten: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
