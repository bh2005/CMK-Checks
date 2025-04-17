```markdown
# xiq_rest_client.py

Dieses Python-Skript interagiert mit der ExtremeCloud IQ (XIQ) API, um verschiedene Informationen abzurufen und diese optional auf der Konsole anzuzeigen, in einer JSON-Datei zu speichern, in einer Redis-Datenbank zu speichern und/oder als CSV-Datei zu exportieren. Es bietet auch Funktionen zur Suche nach Hosts in Redis und zur Abfrage des Location Tree.

## Voraussetzungen

* **Python 3.6 oder höher**
* **requests** Bibliothek (`pip install requests`)
* **redis** Bibliothek (`pip install redis`)
* **csv** Bibliothek (ist Teil der Python-Standardbibliothek)

## Einrichtung

1.  **API-Token:**
    * Sie benötigen einen API-Token für Ihre ExtremeCloud IQ Organisation.
    * Das Skript versucht, den Token aus der Datei `xiq_api_token.txt` im selben Verzeichnis zu lesen.
    * Alternativ können Sie Benutzername und Passwort über die Kommandozeile angeben, um sich einzuloggen und einen neuen Token zu erhalten, der dann in der Datei gespeichert wird.

2.  **Redis (optional):**
    * Wenn Sie die Redis-Funktionen nutzen möchten, stellen Sie sicher, dass ein Redis-Server lokal auf `localhost:6379` läuft oder passen Sie die `REDIS_HOST` und `REDIS_PORT` Variablen im Skript an.

## Verwendung

Führen Sie das Skript über die Kommandozeile aus:

```bash
python xiq_rest_client.py <optionen>
```

### Authentifizierungsoptionen (EINE davon ist erforderlich):

* `-k` oder `--api_key_file <pfad>`: Pfad zur Datei mit dem gespeicherten API-Token (Standard: `xiq_api_token.txt`).
* `-u` oder `--username <benutzername>`: Benutzername für die XIQ API (für erstmaligen Login oder Token-Erneuerung).
* `-p` oder `--password <passwort>`: Passwort für die XIQ API (für erstmaligen Login oder Token-Erneuerung).

### API-Interaktionsoptionen:

* `-s` oder `--server <basis_url>`: Basis-URL der XIQ API (Standard: `https://api.extremecloudiq.com`).
* `--get-devicelist`: Ruft die Liste der Geräte ab.
* `--get-device-by-id <geräte_id>`: Ruft die Details für ein Gerät mit der angegebenen ID ab.
* `--get-device-by-hostname <hostname>`: Ruft die Details für ein Gerät mit dem angegebenen Hostnamen aus Redis ab.
* `-f` oder `--find-hosts`: Sucht Hosts in Redis basierend auf optionalen Kriterien.
    * `-m` oder `--managed_by <wert>`: Optional: Filter für `managed_by` bei der Redis-Suche.
    * `-l` oder `--location_part <teil_des_namens>`: Optional: Teil des Location-Namens für die Redis-Suche.
    * `--hostname-filter <hostname>`: Optional: Hostname für die Redis-Suche.
* `--get-device-status <location_id>`: Ruft die Gerätestatusübersicht für die angegebene Location-ID ab.
* `--get-locations-tree`: Ruft den Location Tree von der API ab, gibt ihn auf der Konsole aus und speichert ihn in Redis (Datenbank 1).
* `--find-location <suchbegriff>`: Sucht nach einer Location im Location Tree (Redis Datenbank 1) und gibt `unique_name` und `id` aus.

### Ausgabeoptionen:

* `-o` oder `--output_file <dateiname>`: Dateiname für die Ausgabe der Geräteliste (JSON, Standard: `XiqDeviceList.json`).
* `--store-redis`: Speichert die Geräteinformationen in Redis (Datenbank 0).
* `--show-pretty`: Zeigt eine vereinfachte Ausgabe der Geräte (id, hostname, mac, ip) auf der Konsole.
* `--output-csv <dateiname>`: Dateiname für die Ausgabe der Geräteliste als CSV.
* `-v` oder `--verbose`: Ausführliche Ausgabe aktivieren (Debug-Level-Logging).

## Beispiele

* **Einloggen und API-Token speichern:**
    ```bash
    python xiq_rest_client.py -u meinbenutzer -p meinpasswort
    ```

* **Geräteliste abrufen und als JSON speichern:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --get-devicelist -o devices.json
    ```

* **Geräteliste abrufen und vereinfacht auf der Konsole anzeigen:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --get-devicelist --show-pretty
    ```

* **Gerät mit der ID `12345` abrufen:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --get-device-by-id 12345
    ```

* **Geräteinformationen für den Hostnamen `mydevice` aus Redis abrufen:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --get-device-by-hostname mydevice
    ```

* **Hosts in Redis suchen, die von `ExtremeCloud IQ` verwaltet werden und `floor1` im Location-Namen haben:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt -f -m "ExtremeCloud IQ" -l "floor1"
    ```

* **Gerätestatusübersicht für die Location-ID `98765` abrufen:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --get-device-status 98765
    ```

* **Location Tree abrufen und in Redis speichern:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --get-locations-tree
    ```

* **Nach einer Location mit dem Namensteil `LOC257` suchen:**
    ```bash
    python xiq_rest_client.py -k xiq_api_token.txt --find-location LOC257
    ```

## Redis Datenbanken

Das Skript verwendet zwei Redis-Datenbanken:

* **Datenbank 0 (Standard):** Wird verwendet, um Geräteinformationen zu speichern, die von der `/devices` API abgerufen werden. Die Schlüssel haben das Format `xiq:device:<hostname>`.
* **Datenbank 1:** Wird verwendet, um den Location Tree zu speichern, der von der `/locations/tree` API abgerufen wird. Der Schlüssel ist `xiq:locations:tree`.

## Fehlerbehandlung

Das Skript enthält grundlegende Fehlerbehandlung für API-Aufrufe, JSON-Verarbeitung, Dateizugriff und Redis-Verbindungen. Bei API-Fehlern werden detaillierte Fehlermeldungen ausgegeben.

## Hinweise

* Behandeln Sie Ihren API-Token sicher und geben Sie ihn nicht an Dritte weiter.
* Seien Sie vorsichtig bei der Verwendung von Befehlen wie `KEYS *` in großen Redis-Produktionsumgebungen, da diese die Serverleistung beeinträchtigen können. Erwägen Sie die Verwendung von `SCAN` für eine schrittweise Iteration.
* Die Struktur der von der XIQ API zurückgegebenen Daten kann sich ändern. Passen Sie das Skript bei Bedarf an.
```