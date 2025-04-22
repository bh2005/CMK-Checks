
```markdown
# How-To: Interaktion mit der REST API mittels `restclient.py`

Dieses Dokument beschreibt, wie Sie das Python-Skript `restclient.py` verwenden können, um mit einer REST API zu interagieren und Datenbanken, Knoten und Items zu verwalten sowie Prozessdaten zu lesen und zu schreiben.

## Voraussetzungen

* **Python 3.6 oder höher** ist auf Ihrem System installiert.
* Die folgenden Python-Bibliotheken sind installiert (verwenden Sie `pip` zur Installation):
  ```bash
  pip install requests jsonschema tenacity
  ```
* Sie benötigen einen **API-Schlüssel** für die REST API.

## Einrichtung

1.  **Speichern Sie das Skript:** Speichern Sie den bereitgestellten Python-Code in einer Datei namens `restclient.py` auf Ihrem System.

2.  **API-Schlüssel:** Stellen Sie sicher, dass Sie Ihren API-Schlüssel kennen. Sie können ihn auf zwei Arten angeben:
    * **Über die Kommandozeile:** Verwenden Sie die Option `-k` oder `--apiKey`.
    * **Als Umgebungsvariable:** Setzen Sie die Umgebungsvariable `API_KEY`.

## Verwendung

Führen Sie das Skript über die Kommandozeile aus:

```bash
python restclient.py <optionen>
```

### Allgemeine Optionen

Diese Optionen können mit allen Aktionen verwendet werden:

* `-s <URL>` oder `--server <URL>`: Die Basis-URL des Servers (z.B., `https://ihrserver:3001`). **Erforderlich**.
* `-k <KEY>` oder `--apiKey <KEY>`: Ihr API-Schlüssel für die Authentifizierung. **Erforderlich**.
* `-db <NAME>` oder `--dbName <NAME>`: Der Name der Zieldatenbank (Standard: `DB1`).
* `-n <NAME>` oder `--nodeName <NAME>`: Der Name des Zielknotens (Standard: `PythonRestClient`).
* `-i <NAME>` oder `--itemName <NAME>`: Der Name des Ziel-Items (Standard: `RandomData-<Zufallszahl>`).
* `-e <COUNT>` oder `--eventsToWrite <COUNT>`: Die Anzahl der zu schreibenden Events (Standard: `10`).
* `--no-proxy`: Deaktiviert die Verwendung von Proxies.
* `--proxy <URL>`: Verwendet den angegebenen Proxy (z.B., `http://benutzer:passwort@host:port`).
* `--verify-ssl`: Aktiviert die SSL-Zertifikatsprüfung (Standard: `True`).
* `--timeout <SEKUNDEN>` oder `--timeout <SEKUNDEN>`: Timeout für API-Anfragen in Sekunden (Standard: `10`).
* `-v` oder `--verbose`: Aktiviert die ausführliche Ausgabe (Debug-Level-Logging).

### Datenbank- und Knotenverwaltung

* `--list-nodes`: Listet alle Knoten in der angegebenen Datenbank mit ihrem Status für Checkmk auf.
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --list-nodes -db MeineDatenbank
    ```

* `--get-node-status <KNOTEN_NAME>`: Ruft den Status eines bestimmten Knotens ab (`all` für alle Knoten).
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --get-node-status MeinKnoten -db MeineDatenbank
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --get-node-status all -db MeineDatenbank
    ```

* `--create-node <NAME>`: Erstellt einen neuen Knoten mit dem angegebenen Namen.
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --create-node NeuerKnoten -db MeineDatenbank
    ```

### Item-Verwaltung

* `--get-item <ID>`: Ruft die Details des Items mit der angegebenen ID ab.
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --get-item 12345 -db MeineDatenbank -n MeinKnoten
    ```

* `--create-item <NAME>`: Erstellt ein neues Item mit dem angegebenen Namen.
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --create-item SensorWert -db MeineDatenbank -n MeinKnoten
    ```

* `--list-items`: Listet alle Items im angegebenen Knoten auf.
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --list-items -db MeineDatenbank -n MeinKnoten
    ```

### Prozessdaten-Verwaltung

* `--write-process-data`: Schreibt zufällige Prozessdaten zum angegebenen Item.
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --write-process-data -db MeineDatenbank -n MeinKnoten -i SensorWert -e 5
    ```

* `--read-process-data --start-time <TIMESTAMP> --end-time <TIMESTAMP>`: Liest Prozessdaten vom angegebenen Item innerhalb des angegebenen Zeitraums. Die Zeitstempel müssen im ISO-Format vorliegen (z.B., `2023-10-26T10:00:00`).
    ```bash
    python restclient.py -s https://ihrserver:3001 -k ihr_api_schlüssel --read-process-data -db MeineDatenbank -n MeinKnoten -i SensorWert --start-time "2024-04-22T09:00:00" --end-time "2024-04-22T09:05:00"
    ```

## Beispiele

* **Auflisten aller Knoten und deren Status:**
    ```bash
    python restclient.py -s https://ihrserver:3001 -k mein_geheimer_schlüssel --list-nodes -db ProduktionsDB
    ```

* **Abrufen des Status eines bestimmten Knotens:**
    ```bash
    python restclient.py -s https://ihrserver:3001 -k mein_geheimer_schlüssel --get-node-status OPC_UA_Server -db TestDB
    ```

* **Erstellen eines neuen Items im Standardknoten:**
    ```bash
    python restclient.py -s https://ihrserver:3001 -k mein_geheimer_schlüssel --create-item TemperaturSensor -db Messwerte
    ```

* **Schreiben von 100 zufälligen Prozessdaten zum Item "Druck" im Knoten "Verarbeitung":**
    ```bash
    python restclient.py -s https://ihrserver:3001 -k mein_geheimer_schlüssel --write-process-data -db Steuerung -n Verarbeitung -i Druck -e 100
    ```

* **Lesen von Prozessdaten des Items "Durchfluss" zwischen zwei Zeitpunkten:**
    ```bash
    python restclient.py -s https://ihrserver:3001 -k mein_geheimer_schlüssel --read-process-data -db Analyse -n Datenlogger --itemName Durchfluss --start-time "2024-04-21T12:00:00" --end-time "2024-04-21T13:00:00"
    ```

## Fehlerbehandlung

Das Skript verwendet das `logging`-Modul, um Informationen und Fehler auszugeben. Achten Sie auf Meldungen in der Konsole, insbesondere wenn etwas nicht wie erwartet funktioniert. Die Option `-v` oder `--verbose` kann zusätzliche Details für die Fehlersuche liefern.

## Hinweise

* Passen Sie die Datenbank-, Knoten- und Item-Namen sowie die Server-URL und den API-Schlüssel an Ihre spezifische REST API an.
* Behandeln Sie Ihren API-Schlüssel vertraulich.
* Lesen Sie die Dokumentation Ihrer REST API, um die korrekten Endpunkte und Datenformate zu verstehen.
```
