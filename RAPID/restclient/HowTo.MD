# REST API Client für Time Series Datenbank

Dieses Python-Skript (`dein_skript.py`) ist ein Kommandozeilen-Tool zur Interaktion mit einer REST API einer Time Series Datenbank. Es ermöglicht die Authentifizierung, das Auflisten von Datenbanken und Knoten, das Abrufen des Knotenstatus, das Überprüfen der Existenz von Datenbanken, Knoten und Items sowie das Lesen von Prozessdaten.

## Voraussetzungen

* Python 3.x
* Das `requests`-Modul (`pip install requests`)

## Konfiguration

Das Skript verwendet Kommandozeilenargumente zur Konfiguration. Die wichtigsten Parameter sind:

* `-s` oder `--server`: Die Adresse des Servers (z.B., `https://yourserver:3001`). Standardmäßig `https://localhost:3001`.
* `-k` oder `--apiKey`: Der API-Schlüssel zur Authentifizierung. Dies ist ein Pflichtparameter und kann auch über die Umgebungsvariable `API_KEY` gesetzt werden.
* `-db` oder `--dbName`: Der Name der Zieldatenbank. Standardmäßig `DB1`.
* `-n` oder `--nodeName`: Der Name des Zielknotens. Standardmäßig `PythonRestClient`.
* `-i` oder `--itemName`: Der Name des Ziel-Items. Standardmäßig `RandomData-<Zufallszahl>`.

Weitere Optionen:

* `--no-proxy`: Deaktiviert die Verwendung von Proxy-Einstellungen.
* `--verify-ssl`: Aktiviert die SSL-Zertifikatsprüfung (standardmäßig aktiviert).
* `--list-nodes`: Listet alle Knoten in der angegebenen Datenbank mit ihrem Status auf.
* `--get-node-status <NODE_NAME>`: Ruft den Status eines bestimmten Knotens ab. Verwenden Sie `all`, um den Status aller Knoten abzurufen.
* `--read-process-data`: Liest Prozessdaten vom angegebenen Item.
* `--start-time <TIMESTAMP>`: Startzeit für das Lesen von Prozessdaten im ISO-Format (z.B., `2023-10-26T10:00:00`).
* `--end-time <TIMESTAMP>`: Endzeit für das Lesen von Prozessdaten im ISO-Format.
* `--get-item`: Überprüft, ob das angegebene Item existiert.

## Beispiele zur Verwendung

1.  **Authentifizierung (wird automatisch beim Ausführen anderer Befehle durchgeführt):**

    Stellen Sie sicher, dass der API-Schlüssel korrekt über das `-k` Argument oder die `API_KEY` Umgebungsvariable übergeben wird.

2.  **Auflisten aller Knoten mit Status in einer Datenbank:**

    ```bash
    ./dein_skript.py -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank --list-nodes
    ```

3.  **Abrufen des Status eines bestimmten Knotens:**

    ```bash
    ./dein_skript.py -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank --get-node-status Sensor01
    ```

4.  **Abrufen des Status aller Knoten:**

    ```bash
    ./dein_skript.py -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank --get-node-status all
    ```

5.  **Überprüfen, ob ein bestimmtes Item existiert:**

    ```bash
    ./dein_skript.py -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank -n Sensor01 -i Temperatur --get-item
    ```

6.  **Lesen von Prozessdaten eines Items über einen bestimmten Zeitraum:**

    ```bash
    ./dein_skript.py -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank -n Sensor01 -i Temperatur --read-process-data --start-time "2025-04-15T07:00:00" --end-time "2025-04-15T08:00:00"
    ```

7.  **Deaktivieren der Proxy-Verwendung:**

    ```bash
    ./dein_skript.py --no-proxy -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank --list-nodes
    ```

8.  **Deaktivieren der SSL-Zertifikatsprüfung (Vorsicht!):**

    ```bash
    ./dein_skript.py --verify-ssl false -s https://ihrserver:3001 -k ihr_api_key -db MeineDatenbank --list-nodes
    ```

## Hinweise

* Ersetzen Sie `https://ihrserver:3001` und `ihr_api_key` durch die tatsächliche Serveradresse und Ihren API-Schlüssel.
* Die Zeitstempel für `--start-time` und `--end-time` müssen im ISO-Format angegeben werden.
* Das Skript führt grundlegende Fehlerbehandlung durch, aber es ist ratsam, die Serverantworten und Fehlermeldungen sorgfältig zu prüfen.

## Lizenz

[Hier ggf. Lizenzinformationen einfügen]