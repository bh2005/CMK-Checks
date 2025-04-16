# How to Use the REST API Client for Checkmk

Dieses Dokument beschreibt die Verwendung des Python-Skripts `restclient3.py` zur Interaktion mit einer REST-API, typischerweise im Kontext von Checkmk-Checks.

## Voraussetzungen

* **Python 3:** Das Skript ist in Python 3 geschrieben. Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist.
* **Abhängigkeiten:** Die folgenden Python-Bibliotheken müssen installiert sein. Sie können diese mit `pip` installieren:
    ```bash
    pip install requests tenacity jsonschema
    ```
* **API-Zugangsdaten:** Sie benötigen die Basis-URL der REST-API und einen gültigen API-Schlüssel.

## Installation (für Checkmk)

1.  **Speichern des Skripts:** Speichern Sie das Skript `restclient3.py` im Verzeichnis für lokale Checkmk-Plugins. Der typische Pfad ist:
    ```
    /opt/omd/sites/<your_site>/local/lib/nagios/plugins/
    ```
    Ersetzen Sie `<your_site>` durch den Namen Ihrer Checkmk-Site.
2.  **Ausführbarmachen:** Stellen Sie sicher, dass das Skript ausführbar ist:
    ```bash
    chmod +x /opt/omd/sites/<your_site>/local/lib/nagios/plugins/restclient3.py
    ```

## Verwendung

Das Skript wird über die Kommandozeile aufgerufen und bietet verschiedene Optionen zur Interaktion mit der REST-API.

### Grundlegende Optionen

* `-s` oder `--server`: Die Basis-URL der REST-API (z.B., `https://yourserver:3001`). **Erforderlich.**
* `-k` oder `--apiKey`: Der API-Schlüssel für die Authentifizierung. Sie können diesen auch als Umgebungsvariable `API_KEY` setzen. **Erforderlich.**
* `-db` oder `--dbName`: Der Name der Zieldatenbank (Standard: `DB1`).
* `-n` oder `--nodeName`: Der Name des Zielknotens (Standard: `PythonRestClient`).
* `-i` oder `--itemName`: Der Name des Ziel-Items (Standard: `RandomData-<Zufallszahl>`).
* `-e` oder `--eventsToWrite`: Die Anzahl der zu schreibenden Events (Standard: `10`).
* `--no-proxy`: Deaktiviert die Verwendung von Proxies (Standard).
* `--proxy <URL>`: Verwendet den angegebenen Proxy (z.B., `http://user:pass@host:port`).
* `--verify-ssl`: Aktiviert die SSL-Zertifikatsprüfung (Standard: `True`). Verwenden Sie `--no-verify-ssl` (falls implementiert, andernfalls entfernen Sie `--verify-ssl` aus den Optionen und fügen Sie `--no-verify-ssl` mit `action='store_false', dest='verify_ssl'`) um die Prüfung zu deaktivieren (nicht empfohlen für Produktionsumgebungen).
* `--timeout <SECONDS>`: Der Timeout für API-Anfragen in Sekunden (Standard: `10`).
* `-v` oder `--verbose`: Aktiviert ausführliche Ausgabe für Debugging-Zwecke.

### Spezifische Aktionen

* `--list-nodes`: Listet alle Knoten in der angegebenen Datenbank mit ihrem Status für Checkmk auf.
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --list-nodes -db MyDatabase
    ```
    Die Ausgabe ist im Checkmk-Format (`<<<local>>>`).

* `--get-node-status <NODE_NAME>`: Ruft den Status eines bestimmten Knotens ab. Verwenden Sie `'all'`, um den Status aller Knoten abzurufen (ebenfalls im Checkmk-Format).
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --get-node-status MyNode -db MyDatabase
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --get-node-status all -db MyDatabase
    ```

* `--read-process-data --start-time <TIMESTAMP> --end-time <TIMESTAMP>`: Liest Prozessdaten vom angegebenen Item innerhalb des gegebenen Zeitraums. Die Zeitstempel müssen im ISO-Format vorliegen (z.B., `2023-10-26T10:00:00`).
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --read-process-data -db MyDatabase -n MyNode -i MyItem --start-time 2023-10-26T10:00:00 --end-time 2023-10-26T11:00:00
    ```

* `--get-item`: Überprüft, ob das angegebene Item existiert und gibt Details im JSON-Format aus.
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --get-item -db MyDatabase -n MyNode -i MyItem
    ```

* `--create-node <NAME>`: Erstellt einen neuen Knoten mit dem angegebenen Namen.
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --create-node NewNode -db MyDatabase
    ```

* `--create-item <NAME>`: Erstellt ein neues Item mit dem angegebenen Namen im angegebenen Knoten.
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --create-item NewItem -db MyDatabase -n MyNode
    ```

* `--write-process-data`: Schreibt zufällige Prozessdaten zum angegebenen Item. Die Anzahl der Events wird mit `-e` oder `--eventsToWrite` gesteuert.
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --write-process-data -db MyDatabase -n MyNode -i MyItem -e 5
    ```

* `--list-items`: Listet alle Items im angegebenen Knoten auf.
    ```bash
    ./restclient3.py -s https://yourserver:3001 -k your_api_key --list-items -db MyDatabase -n MyNode
    ```

### Beispiele für Checkmk

Um das Skript als Checkmk-Check zu verwenden, können Sie es direkt aufrufen und die Ausgabe von Checkmk interpretieren lassen. Zum Beispiel, um den Status aller Knoten in der Datenbank `MyDatabase` zu überwachen:

1.  Erstellen Sie eine neue Regel in Checkmk (z.B. unter "Datasource Programs" oder "Integrations").
2.  Wählen Sie "Programm call instead of agent".
3.  Konfigurieren Sie den Befehl, z.B.:
    ```
    OMD[mysite]:/local/lib/nagios/plugins/restclient3.py -s https://yourserver:3001 -k <your_api_key> --list-nodes -db MyDatabase
    ```
    Ersetzen Sie `<your_api_key>` durch Ihren tatsächlichen API-Schlüssel und `mysite` durch Ihren Checkmk-Sitename.
4.  Stellen Sie sicher, dass die Regel auf die entsprechenden Hosts oder Services angewendet wird.

Checkmk wird die `<<<local>>>`-Sektion in der Ausgabe des Skripts erkennen und die Knotenstatus als Services anzeigen.

## Fehlerbehebung

* **Falsche API-URL oder -Schlüssel:** Stellen Sie sicher, dass die `-s` und `-k` Parameter korrekt sind.
* **Netzwerkprobleme:** Überprüfen Sie die Netzwerkverbindung zum REST-API-Server.
* **Fehlende Abhängigkeiten:** Stellen Sie sicher, dass alle erforderlichen Python-Bibliotheken installiert sind.
* **Server-seitige Fehler:** Überprüfen Sie die Logs des REST-API-Servers auf mögliche Fehler.
* **Verbose-Modus:** Verwenden Sie die `-v` oder `--verbose` Option, um detailliertere Informationen über die API-Anfragen und -Antworten zu erhalten.

## Weiterentwicklung

Dieses Skript kann weiterentwickelt werden, um zusätzliche Funktionen der REST-API zu unterstützen, komplexere Validierungen durchzuführen oder in andere Monitoring-Systeme integriert zu werden. Die Verwendung der `RestClient2`-Klasse bietet eine gute Grundlage für zukünftige Erweiterungen.