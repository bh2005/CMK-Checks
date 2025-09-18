## xiq_redis_client.py

### Grundlegende Nutzung

Diese Optionen sind für die Anmeldung und das Abrufen von Gerätedaten essenziell.

  * `--login`, `-l`: Löst einen neuen Anmeldevorgang aus, um ein frisches API-Token zu erhalten und zu speichern.
  * `--username [NAME]` und `--password [PASSWORT]`: Wird in Verbindung mit `--login` verwendet, um sich bei der ExtremeCloud™ IQ API anzumelden. Alternativ können diese Informationen in einer `.env`-Datei gespeichert werden.
  * `--get-devicelist`: Ruft eine paginierte Liste aller Geräte aus Ihrer ExtremeCloud™ IQ-Umgebung ab und gibt sie auf der Konsole aus. Dies ist die Hauptfunktion des Skripts.
  * `--output-file [DATEIPFAD]`: Speichert die abgerufene Geräteliste als JSON-Datei.
  * `--output-csv-file [DATEIPFAD]`: Speichert die abgerufene Geräteliste als CSV-Datei, die sich gut für Tabellenkalkulationen eignet.
  * `--store-redis`: Speichert die abgerufene Geräteliste in der Redis-Datenbank `db0`. Dies ist eine Voraussetzung für die `--find-hosts`-Funktion.

-----

### Suchen und Filtern (aus Redis)

Diese Optionen ermöglichen die schnelle Suche in der bereits in Redis gespeicherten Gerätedatenbank. Sie müssen zuvor `--store-redis` ausgeführt haben.

  * `--find-hosts`, `-f`: Aktiviert den Suchmodus. Sie müssen mindestens einen der folgenden Filter verwenden.
  * `--hostname-filter [WERT]`: Findet Geräte, deren Hostname den angegebenen Teilstring enthält.
  * `--location-part [WERT]`: Findet Geräte, die sich an einem bestimmten Standort befinden.
  * `--managed-by [WERT]`: Findet Geräte, die von einer bestimmten Entität verwaltet werden.
  * `--device-function [WERT]`: Findet Geräte basierend auf ihrer Funktion (z.B. "AP" für Access Point, "Switch" für Switch).
  * `--exact-match`: Ändert das Verhalten der Filter von einer "Teilstring-Suche" zu einer "exakten Übereinstimmung".

-----

### Standort- und Statusabfragen

Diese Optionen dienen der Abfrage von standortspezifischen Daten und Gerätestatistiken.

  * `--get-locations-tree`: Ruft die vollständige Standortstruktur aus der API ab, gibt sie auf der Konsole aus und speichert sie in der Redis-Datenbank `db1`.
  * `--get-location-info [NAME]`: Sucht in der Redis-Datenbank `db1` nach dem Namen eines Standortes und gibt dessen ID und eindeutigen Namen aus.
  * `--get-device-status [ID]`: Ruft eine Statusübersicht aller Geräte an einem bestimmten Standort ab. Die ID erhalten Sie über die Option `--get-location-info`.

-----

### Zusätzliche Optionen

  * `--show-pretty`: Gibt die Ausgabe in einem für Menschen leichter lesbaren Format aus.
  * `--verbose`: Aktiviert eine detailliertere Protokollierung (Logging) zur Fehlersuche.
  * `--api-key-file [DATEIPFAD]`: Gibt den Pfad zur Datei an, in der das API-Token gespeichert ist. Standard ist `.api_token`.
  * `--serverRoot [URL]`: Ändert die Basis-URL der ExtremeCloud™ IQ API. Standardmäßig verwendet das Skript die URL aus der `.env`-Datei.

-----

### Beispiele für die Anwendung

#### Beispiel 1: Geräte abrufen und in Redis speichern

```sh
# Meldet sich an, ruft die Geräteliste ab und speichert sie in Redis (db0)
python xiq_redis_client.py --login --store-redis
```

#### Beispiel 2: In Redis nach einem spezifischen Switch suchen

```sh
# Sucht in der zuvor gespeicherten Redis-Datenbank nach einem Switch mit "sw-de" im Hostnamen
python xiq_redis_client.py --find-hosts --hostname-filter "sw-de" --device-function "Switch" --show-pretty
```

#### Beispiel 3: Standort-ID finden und Gerätestatus abrufen

```sh
# Ruft zuerst den Standortbaum ab und speichert ihn in Redis (db1)
python xiq_redis_client.py --get-locations-tree

# Sucht dann nach der ID des Standorts "Frankfurt"
python xiq_redis_client.py --get-location-info "Frankfurt"

# Nutzt die gefundene ID, um den Gerätestatus für diesen Standort abzurufen
python xiq_redis_client.py --get-device-status [ID_VON_FRANKFURT]
```