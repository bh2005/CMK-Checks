import requests
import json
import os

# ***************************************************************
# SICHERHEITSHINWEIS: Speichern Sie Ihren API-Token NIE direkt
# im Code. Verwenden Sie Umgebungsvariablen oder sichere Vaults.
# Hier wird die Umgebungsvariable 'XIQ_ACCESS_TOKEN' verwendet.
# ***************************************************************

# --- Konfiguration ---
# Basis-URL des ExtremeCloud IQ API Gateways
API_BASE_URL = "https://api.extremecloudiq.com"

# API-Endpunkt, der abgefragt werden soll (z.B. Geräte-Liste)
# Ein einfacher GET-Aufruf ist am besten geeignet.
API_ENDPOINT = f"{API_BASE_URL}/devices"

# API-Token aus einer Umgebungsvariable auslesen
ACCESS_TOKEN = os.environ.get("XIQ_ACCESS_TOKEN")

def check_xiq_api_limits():
    """
    Führt einen API-Aufruf durch und liest die Rate-Limit-Header aus.
    """
    if not ACCESS_TOKEN:
        print("FEHLER: Der XIQ_ACCESS_TOKEN wurde nicht in den Umgebungsvariablen gefunden.")
        print("Bitte setzen Sie die Umgebungsvariable, z.B.: export XIQ_ACCESS_TOKEN='IhrToken'")
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }

    try:
        # Führe den GET-Request durch
        response = requests.get(API_ENDPOINT, headers=headers)

        # Prüfe, ob der Request erfolgreich war
        if response.status_code == 200:
            print("--- ExtremeCloud IQ API Rate Limits (aus HTTP-Headern) ---")
            
            # Rate-Limit-Header auslesen
            limit_limit = response.headers.get("RateLimit-Limit", "Nicht gefunden")
            limit_remaining = response.headers.get("RateLimit-Remaining", "Nicht gefunden")
            limit_reset = response.headers.get("RateLimit-Reset", "Nicht gefunden")

            # Ausgabe formatieren
            print(f"[{'HEADER':<19}]  |  {'WERT':<20}")
            print("-" * 45)
            print(f"[{'RateLimit-Limit':<19}]  |  {limit_limit:<20}")
            print(f"[{'RateLimit-Remaining':<19}]  |  {limit_remaining:<20}")
            print(f"[{'RateLimit-Reset':<19}]  |  {limit_reset:<20} (Sekunden bis Reset)")
            print("-" * 45)

            # Beispielhafte Interpretation des Limits
            if limit_limit != "Nicht gefunden" and ";" in limit_limit:
                try:
                    max_requests, time_window = limit_limit.split(';w=')
                    print(f"\nInterpretation:")
                    print(f"-> Maximales Limit: {max_requests} Anfragen")
                    print(f"-> Zeitfenster: {time_window} Sekunden ({int(time_window)/60/60:.2f} Stunden)")
                except:
                    pass

        elif response.status_code == 429:
            # Spezieller Fall: Limit bereits überschritten (Too Many Requests)
            print("FEHLER (429): Das API-Limit wurde bereits überschritten.")
            
            # Die Header sind oft auch bei 429-Fehlern noch informativ
            limit_remaining = response.headers.get("RateLimit-Remaining", "0")
            limit_reset = response.headers.get("RateLimit-Reset", "Unbekannt")
            
            print(f"-> Verbleibende Anfragen: {limit_remaining}")
            print(f"-> Reset in: {limit_reset} Sekunden")
            print("Bitte warten Sie, bis die Reset-Zeit abgelaufen ist.")

        else:
            # Sonstige Fehler (z.B. 401 Unauthorized, 404 Not Found)
            print(f"FEHLER: API-Anfrage fehlgeschlagen mit Statuscode {response.status_code}")
            # print(f"Antwort-Text (Auszug): {response.text[:200]}") # Optional: Fehlerdetails ausgeben

    except requests.exceptions.RequestException as e:
        print(f"Ein Verbindungsfehler ist aufgetreten: {e}")

if __name__ == "__main__":
    check_xiq_api_limits()