# HowTo: Verwendung des xiq_redis_client.py Skripts

Dieses Dokument beschreibt die Verwendung des `xiq_redis_client.py` Skripts, um mit den in Redis gespeicherten Daten von ExtremeCloud IQ (XIQ) zu interagieren. Dieses Skript ermöglicht das Suchen und Anzeigen von Hostinformationen, die zuvor von einem anderen Prozess (z.B. einem XIQ-API-Abrufer) in Redis gespeichert wurden.

## Voraussetzungen

* **Python 3:** Das Skript ist in Python 3 geschrieben. Stellen Sie sicher, dass Python 3 auf Ihrem System installiert ist.
* **Redis Python Bibliothek:** Das Skript verwendet die `redis` Python Bibliothek, um mit dem Redis-Server zu kommunizieren. Installieren Sie diese mit pip:
    ```bash
    pip install redis
    ```
* **Redis Server:** Ein laufender Redis-Server, der die XIQ-Daten enthält. Die Host- und Port-Informationen des Redis-Servers müssen im Skript konfiguriert sein (siehe Konfiguration).
* **XIQ-Daten in Redis:** Es wird davon ausgegangen, dass bereits XIQ-Geräteinformationen im Redis-Cache in einem bestimmten Format gespeichert sind. Dieses Skript ist darauf ausgelegt, diese vorhandenen Daten abzufragen.

## Konfiguration

Bevor Sie das Skript verwenden, müssen Sie die Verbindungsinformationen für Ihren Redis-Server im Skript selbst anpassen. Öffnen Sie `xiq_redis_client.py` und suchen Sie die folgenden Variablen am Anfang der Datei:


REDIS_HOST = "localhost"  # Standardmäßig localhost
REDIS_PORT = 6379        # Standardmäßiger Redis-Port
REDIS_DEVICE_DB = 0      # Datenbank für Geräteinformationen


Passen Sie diese Variablen an die Konfiguration Ihres Redis-Servers an.

## Verwendung

Das Skript wird über die Befehlszeile aufgerufen und bietet verschiedene Optionen zum Suchen und Anzeigen von Hostinformationen.

```bash
python xiq_redis_client.py [OPTIONEN]
```

### Optionen

* `-f`, `--find-hosts`: Aktiviert den Suchmodus für Hosts in Redis. Muss verwendet werden, um Suchkriterien anzuwenden.
* `-m`, `--managed_by <MANAGED_BY>`: Filtert Hosts nach dem Wert des Feldes `managed_by` (z.B. `XIQ`).
* `-l`, `--location-part <LOCATION_PART>`: Filtert Hosts, deren Location-Name den angegebenen Teilstring enthält (Groß-/Kleinschreibung wird ignoriert).
* `--hostname-filter <HOSTNAME>`: Filtert Hosts nach dem Hostnamen (Teilstring-Suche, Groß-/Kleinschreibung wird ignoriert).
* `--device-function <DEVICE_FUNCTION>`: Filtert Hosts nach der Gerätefunktion (z.B. `AP`, `Switch`, Groß-/Kleinschreibung wird ignoriert).
* `--exact-match`: Erzwingt eine exakte Übereinstimmung für alle Filterkriterien (`managed_by`, `location-part`, `hostname-filter`, `device-function`). Ohne diese Option wird eine Teilstring-Suche durchgeführt (case-insensitive).
* `-v`, `--verbose`: Aktiviert die ausführliche Ausgabe. Zeigt zusätzliche Debug-Informationen während der Suche an (z.B. die durchsuchten Redis-Keys).

### Beispiele

1.  **Alle Hosts anzeigen:**
    ```bash
    python xiq_redis_client.py -f
    ```

2.  **Hosts suchen, die von "XIQ" verwaltet werden:**
    ```bash
    python xiq_redis_client.py -f -m XIQ
    ```

3.  **Hosts suchen, die den Teilstring "Floor" im Location-Namen haben:**
    ```bash
    python xiq_redis_client.py -f -l Floor
    ```

4.  **Hosts mit dem Hostnamen "my-ap-01" suchen (Teilstring):**
    ```bash
    python xiq_redis_client.py -f --hostname-filter my-ap-01
    ```

5.  **Hosts mit der Gerätefunktion "Switch" suchen (exakte Übereinstimmung):**
    ```bash
    python xiq_redis_client.py -f --device-function Switch --exact-match
    ```

6.  **Hosts suchen, die von "on-prem" verwaltet werden und "Building A" im Location-Namen haben (Teilstring-Suche):**
    ```bash
    python xiq_redis_client.py -f -m on-prem -l "Building A"
    ```

7.  **Ausführliche Suche nach Hosts mit dem Hostnamen "edge-switch-42":**
    ```bash
    python xiq_redis_client.py -f --hostname-filter edge-switch-42 -v
    ```

## Ausgabe

Das Skript gibt eine Liste der gefundenen Hosts auf der Konsole aus. Für jeden übereinstimmenden Host werden die folgenden Informationen angezeigt:

* ID
* Hostname
* MAC-Adresse
* IP-Adresse
* Managed By
* Device Function
* Locations (als Liste der Namen)

## Fehlerbehebung

* **`redis.exceptions.ConnectionError`:** Stellen Sie sicher, dass der Redis-Server läuft und die in den Skriptvariablen `REDIS_HOST` und `REDIS_PORT` angegebenen Verbindungsinformationen korrekt sind.
* **Keine Ausgabe:** Wenn das Skript keine Hosts findet, überprüfen Sie Ihre Suchkriterien und stellen Sie sicher, dass die XIQ-Daten in Redis vorhanden sind und die gesuchten Felder die erwarteten Werte enthalten. Verwenden Sie die Option `-v`, um zu sehen, welche Redis-Keys durchsucht werden.
* **Falsche Filterung:** Überprüfen Sie die Groß-/Kleinschreibung und die Verwendung von `--exact-match`, wenn Ihre Filter nicht die erwarteten Ergebnisse liefern.

## Weiterentwicklung

Dieses Skript bietet eine einfache Möglichkeit, in Redis gespeicherte XIQ-Daten abzufragen. Es kann nach Bedarf erweitert werden, um zusätzliche Filterkriterien, eine formatiertere Ausgabe oder die Interaktion mit anderen Daten in Redis zu ermöglichen.
```

Diese `HowTo.md`-Datei sollte eine gute Grundlage für die Verwendung des `xiq_redis_client.py` Skripts bieten. Du kannst sie bei Bedarf noch weiter anpassen oder ergänzen.