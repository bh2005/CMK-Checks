# HowTo: Verwendung des xiq_rest_client2.py Skripts

Dieses Dokument beschreibt die Verwendung des `xiq_rest_client2.py` Skripts zur Interaktion mit der ExtremeCloud IQ (XIQ) API und zur Interaktion mit in Redis gespeicherten Daten.

## Voraussetzungen

* **Python 3:** Das Skript ist in Python 3 geschrieben. Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist.
* **Requests Python Bibliothek:** Das Skript verwendet die `requests` Bibliothek für HTTP-Anfragen. Installieren Sie diese mit pip:
    ```bash
    pip install requests
    ```
* **Redis Python Bibliothek:** Für die Interaktion mit Redis ist die `redis` Bibliothek erforderlich:
    ```bash
    pip install redis
    ```
* **API-Token oder XIQ-Zugangsdaten:** Sie benötigen entweder einen gültigen XIQ API-Token oder Ihre XIQ-Benutzername und Passwort für die Authentifizierung.
* **Redis Server (optional):** Einige Funktionen des Skripts erfordern einen laufenden Redis-Server.

## Konfiguration

### API-Authentifizierung

Das Skript bietet verschiedene Möglichkeiten zur API-Authentifizierung:

1.  **API-Token-Datei (empfohlen):** Speichern Sie Ihren API-Token in einer Datei (standardmäßig `xiq_api_token.txt`). Der Pfad kann mit der Option `-k` oder `--api_key_file` angegeben werden.
2.  **Benutzername und Passwort:** Sie können Ihren XIQ-Benutzernamen (`-u` oder `--username`) und Ihr Passwort (`-p` oder `--password`) direkt in der Befehlszeile angeben.
3.  **Erstellung einer .env-Datei:** Mit der Option `--create-env` können Sie eine `.env`-Datei mit Ihren Benutzername und Passwort erstellen.

### Redis-Verbindung

Die Redis-Verbindungsinformationen sind im Skript in den Variablen `REDIS_HOST`, `REDIS_PORT` und `REDIS_DEVICE_DB` (für Geräte) bzw. Datenbank 1 (für den Location Tree) konfiguriert. Passen Sie diese bei Bedarf im Skript an.

## Verwendung

Das Skript wird über die Befehlszeile aufgerufen und bietet verschiedene Optionen für die Interaktion mit der XIQ API und Redis.

```bash
python xiq_rest_client2.py [OPTIONEN]
```

### Optionen

#### Authentifizierungsgruppe

* `-k`, `--api_key_file <PFAD>`: Pfad zur API-Token-Datei (Standard: `xiq_api_token.txt`).
* `-u`, `--username <BENUTZERNAME>`: Benutzername für die XIQ API.
* `-p`, `--password <PASSWORT>`: Passwort für die XIQ API.
* `--create-env`: Erstellt eine `.env`-Datei mit den angegebenen Benutzername und Passwort.

#### API-Abruf-Gruppe

* `-s`, `--server <URL>`: Basis-URL der XIQ API (Standard: `https://api.extremecloudiq.com`).
* `--get-devicelist`: Ruft die Liste der Geräte ab.
* `--get-device-by-id <GERÄTE-ID>`: Ruft die Details für ein Gerät mit der angegebenen ID ab.
* `--get-device-details-by-hostname <HOSTNAME>`: Ruft die Details für ein Gerät mit dem angegebenen Hostnamen ab (ID wird aus Redis abgerufen).
* `-pp`, `--pretty-print`: Ausgabe der Geräte-Details im lesbaren Format (gilt für `--get-device-by-id` und `--get-device-details-by-hostname`).
* `--get-device-status <LOCATION-ID>`: Ruft die Gerätestatusübersicht für die angegebene Location-ID ab.
* `--get-locations-tree`: Ruft den Location Tree ab und speichert ihn in Redis (db=1).
* `--find-location <SUCHBEGRIFF>`: Sucht nach einer Location im Location Tree (Redis db=1) und gibt `unique_name` und `id` aus.

#### Redis-Interaktions-Gruppe

* `--get-device-by-hostname <HOSTNAME>`: Ruft die Details für ein Gerät mit dem angegebenen Hostnamen aus Redis ab.
* `-f`, `--find-hosts`: Sucht Hosts in Redis basierend auf optionalen Kriterien.
* `-m`, `--managed_by <MANAGED_BY>`: Optional: Filter für `managed_by` bei der Redis-Suche.
* `-l`, `--location-part <LOCATION_PART>`: Optional: Teil des Location-Namens für die Redis-Suche.
* `--hostname-filter <HOSTNAME>`: Optional: Hostname für die Redis-Suche.
* `--device-function <GERÄTEFUNKTION>`: Optional: Filter für die Gerätefunktion (z.B., `AP`, `Switch`).
* `--exact-match`: Verwendet eine exakte Übereinstimmung für die Filter in der Redis-Suche.
* `--store-redis`: Speichert die Geräteinformationen (von `--get-devicelist`) in Redis (db=0).

#### Ausgabe-Optionen

* `-o`, `--output_file <DATEINAME>`: Dateiname für die Ausgabe der Geräteliste (JSON, Standard: `XiqDeviceList.json`).
* `--show-pretty`: Zeigt eine vereinfachte Ausgabe der Geräte (id, hostname, mac, ip) auf der Konsole (für `--get-devicelist`).
* `--output-csv <DATEINAME>`: Dateiname für die Ausgabe der Geräteliste als CSV (für `--get-devicelist`).

#### Sonstige Optionen

* `-v`, `--verbose`: Aktiviert die ausführliche Ausgabe.

### Beispiele

#### API-Abruf

1.  **Geräteliste abrufen und als JSON speichern:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist -o meine_geraete.json
    ```

2.  **Geräteliste abrufen und vereinfacht auf der Konsole anzeigen:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist --show-pretty
    ```

3.  **Geräteliste abrufen und als CSV speichern:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist --output-csv geraete.csv
    ```

4.  **Details für ein Gerät mit der ID `917843101234567` abrufen:**
    ```bash
    ./xiq_rest_client2.py --get-device-by-id 917843101234567
    ```

5.  **Details für ein Gerät mit der ID `917843101234567` abrufen und formatiert ausgeben:**
    ```bash
    ./xiq_rest_client2.py --get-device-by-id 917843101234567 -pp
    ```

6.  **Details für ein Gerät mit dem Hostnamen `mein-ap-01` abrufen (ID aus Redis):**
    ```bash
    ./xiq_rest_client2.py --get-device-details-by-hostname mein-ap-01
    ```

7.  **Details für ein Gerät mit dem Hostnamen `mein-ap-01` abrufen und formatiert ausgeben (ID aus Redis):**
    ```bash
    ./xiq_rest_client2.py --get-device-details-by-hostname mein-ap-01 -pp
    ```

8.  **Gerätestatus für die Location-ID `917843101234568` abrufen:**
    ```bash
    ./xiq_rest_client2.py --get-device-status 917843101234568
    ```

9.  **Den Location Tree abrufen und in Redis speichern:**
    ```bash
    ./xiq_rest_client2.py --get-locations-tree
    ```

10. **Nach einer Location mit dem Namensteil "Büro" suchen:**
    ```bash
    ./xiq_rest_client2.py --find-location Büro
    ```

#### Redis-Interaktion

1.  **Details für ein Gerät mit dem Hostnamen `anderer-ap-02` direkt aus Redis abrufen:**
    ```bash
    ./xiq_rest_client2.py --get-device-by-hostname anderer-ap-02
    ```

2.  **Alle Hosts in Redis anzeigen:**
    ```bash
    ./xiq_rest_client2.py -f
    ```

3.  **Hosts in Redis suchen, die von "on-premise" verwaltet werden:**
    ```bash
    ./xiq_rest_client2.py -f -m on-premise
    ```

4.  **Hosts in Redis suchen, die "Lager" im Location-Namen haben:**
    ```bash
    ./xiq_rest_client2.py -f -l Lager
    ```

5.  **Hosts in Redis suchen mit dem exakten Hostnamen "switch-05":**
    ```bash
    ./xiq_rest_client2.py -f --hostname-filter switch-05 --exact-match
    ```

6.  **Geräteinformationen (nachdem sie mit `--get-devicelist` abgerufen wurden) in Redis speichern:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist --store-redis
    ```

#### Sonstige Optionen

1.  **Ausführliche Ausgabe aktivieren:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist -v
    ./xiq_rest_client2.py --get-device-details-by-hostname mein-ap-01 -pp -v
    ```

## Ausgabe

Die Ausgabe des Skripts hängt von der verwendeten Option ab:

* **`--get-devicelist`:**
    * Ohne weitere Optionen wird eine Liste von Geräteobjekten im JSON-Format auf der Konsole ausgegeben.
    * Mit `-o <DATEINAME>` werden die Geräteinformationen als JSON in die angegebene Datei geschrieben.
    * Mit `--show-pretty` wird eine vereinfachte Liste der Geräte mit ID, Hostname, MAC-Adresse und IP-Adresse auf der Konsole angezeigt.
    * Mit `--output-csv <DATEINAME>` werden die Geräteinformationen als CSV in die angegebene Datei geschrieben (die Spalten können je nach den abgerufenen Daten variieren).

* **`--get-device-by-id <GERÄTE-ID>`:**
    * Gibt die detaillierten Informationen für das angegebene Gerät im JSON-Format auf der Konsole aus.
    * Mit `-pp` wird eine formatierte, besser lesbare Ausgabe der wichtigsten Geräteinformationen angezeigt (ID, Hostname, MAC-Adresse, IP-Adresse, Gerätefunktion, verwaltet von, Standorte).

* **`--get-device-details-by-hostname <HOSTNAME>`:**
    * Ruft zuerst die Geräte-ID für den angegebenen Hostnamen aus Redis ab und fragt dann die API nach den Details. Die Ausgabe ist identisch mit der von `--get-device-by-id`.
    * Mit `-pp` wird ebenfalls die formatierte Ausgabe angezeigt.
    * Wenn die Geräte-ID in Redis nicht gefunden wird, wird eine entsprechende Meldung ausgegeben.

* **`--get-device-status <LOCATION-ID>`:**
    * Gibt eine Übersicht des Gerätestatus für die angegebene Location-ID im JSON-Format auf der Konsole aus. Die genauen Felder können variieren.

* **`--get-locations-tree`:**
    * Gibt eine Erfolgsmeldung aus, wenn der Location Tree erfolgreich von der API abgerufen und in Redis gespeichert wurde. Im Fehlerfall werden Fehlermeldungen angezeigt.

* **`--find-location <SUCHBEGRIFF>`:**
    * Gibt eine Liste der gefundenen Locations aus Redis aus, die den Suchbegriff im Namen enthalten. Für jede gefundene Location werden der `unique_name` und die `id` angezeigt.
    * Wenn keine übereinstimmenden Locations gefunden werden, wird eine entsprechende Meldung ausgegeben.

* **`--get-device-by-hostname <HOSTNAME>` (Redis):**
    * Gibt die detaillierten Informationen für das Gerät mit dem angegebenen Hostnamen direkt aus Redis im JSON-Format auf der Konsole aus.
    * Wenn der Hostname in Redis nicht gefunden wird, wird eine entsprechende Meldung ausgegeben.

* **`-f`, `--find-hosts` (Redis):**
    * Gibt eine Liste der gefundenen Hosts aus Redis aus, die den angegebenen Filterkriterien entsprechen. Für jeden Host werden ID, Hostname, MAC-Adresse, IP-Adresse, verwaltet von, Gerätefunktion und die Liste der Standorte angezeigt.
    * Wenn keine übereinstimmenden Hosts gefunden werden, wird eine entsprechende Meldung ausgegeben.

* **`-v`, `--verbose`:**
    * Aktiviert zusätzliche Meldungen auf der Konsole, die den Ablauf des Skripts und eventuelle Debug-Informationen detaillierter darstellen.

Die genaue Struktur der JSON-Ausgabe kann je nach dem spezifischen API-Endpunkt variieren. Die formatierte Ausgabe (`-pp`) zielt darauf ab, die wichtigsten Geräteinformationen in einer für Menschen leichter lesbaren Form darzustellen.


## Fehlerbehebung

* **Ungültiger API-Token:**
    * Stellen Sie sicher, dass der in der angegebenen Token-Datei (`xiq_api_token.txt` oder der mit `-k` angegebene Pfad) gespeicherte API-Token gültig ist.
    * Überprüfen Sie, ob der Token nicht abgelaufen ist.
    * Wenn Sie Benutzername und Passwort verwenden, stellen Sie sicher, dass diese korrekt sind.
    * Überprüfen Sie die Fehlermeldungen in der Ausgabe des Skripts bezüglich der Authentifizierung.

* **Verbindung zur XIQ API fehlgeschlagen:**
    * Überprüfen Sie Ihre Internetverbindung.
    * Stellen Sie sicher, dass die Basis-URL der XIQ API (`-s` oder Standardwert) korrekt ist.
    * Firewalls oder Proxies könnten die Verbindung verhindern. Überprüfen Sie Ihre Netzwerkeinstellungen.

* **Fehler beim Abrufen von Daten (HTTP-Statuscodes):**
    * Wenn das Skript Fehlermeldungen mit HTTP-Statuscodes (z.B. 401 Unauthorized, 404 Not Found, 500 Internal Server Error) ausgibt, deutet dies auf ein Problem mit der API-Anfrage hin.
        * **401 Unauthorized:** Überprüfen Sie Ihren API-Token oder Ihre Anmeldedaten.
        * **404 Not Found:** Die angeforderte Ressource (z.B. Geräte-ID, Location-ID) existiert möglicherweise nicht. Überprüfen Sie die IDs.
        * **500 Internal Server Error:** Es gab ein serverseitiges Problem bei ExtremeCloud IQ. Versuchen Sie es später erneut.
    * Aktivieren Sie den Verbose-Modus (`-v`), um detailliertere Fehlermeldungen und die gesendeten URLs anzuzeigen.

* **Redis-Verbindungsprobleme:**
    * Wenn Funktionen, die Redis verwenden (`--get-device-by-hostname`, `-f`, `--get-locations-tree`, `--find-location`, `--store-redis`, `--get-device-details-by-hostname`), fehlschlagen:
        * Stellen Sie sicher, dass der Redis-Server läuft und von Ihrem System aus erreichbar ist.
        * Überprüfen Sie die in den Skriptvariablen `REDIS_HOST` und `REDIS_PORT` konfigurierten Verbindungsinformationen.
        * Stellen Sie sicher, dass die Redis Python Bibliothek (`redis`) installiert ist.
        * Überprüfen Sie die Fehlermeldungen bezüglich `redis.exceptions.ConnectionError`.

* **Keine Daten gefunden:**
    * Wenn Abfragen keine Ergebnisse liefern, überprüfen Sie die Suchkriterien (z.B. Geräte-ID, Hostname, Location-Name).
    * Stellen Sie bei der Redis-Suche sicher, dass die Daten tatsächlich in Redis vorhanden sind und die Filter korrekt angewendet werden (verwenden Sie `--exact-match`, falls erforderlich).

* **Fehler beim Speichern in Dateien:**
    * Wenn beim Schreiben in die Ausgabedatei (`-o`, `--output-csv`) Fehler auftreten, überprüfen Sie die Berechtigungen des Skripts, um Dateien im angegebenen Pfad zu erstellen und zu schreiben.
    * Stellen Sie sicher, dass der angegebene Dateiname gültig ist.

* **Unerwartete Fehler:**
    * Aktivieren Sie den Verbose-Modus (`-v`), um detailliertere Informationen über den Skriptablauf und mögliche Python-Fehlermeldungen (Tracebacks) zu erhalten. Diese können bei der Diagnose von Problemen sehr hilfreich sein.

* **Falsche oder unvollständige Ausgabe:**
    * Überprüfen Sie die Dokumentation der XIQ API, um sicherzustellen, dass die erwarteten Datenfelder tatsächlich in der Antwort enthalten sind.
    * Wenn Sie die formatierte Ausgabe (`-pp`) verwenden, beachten Sie, dass nur eine Auswahl der wichtigsten Felder angezeigt wird. Verwenden Sie die Standardausgabe, um alle verfügbaren Daten zu sehen.

Wenn Sie weiterhin Probleme haben, aktivieren Sie den Verbose-Modus (`-v`) und teilen Sie die vollständige Ausgabe des Skripts zusammen mit dem verwendeten Befehl und einer Beschreibung des Problems mit.

## Weiterentwicklung

Mal schauen was die API noch so anbietet
```

