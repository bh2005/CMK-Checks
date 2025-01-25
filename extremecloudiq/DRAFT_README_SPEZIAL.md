# Checkmk Spezialagent für ExtremeCloud IQ

Dieser Ordner enthält die Dateien, die zur Überwachung von ExtremeCloud IQ (XIQ) mit Checkmk benötigt werden. Er besteht aus einem Agenten, einer Inventory-Funktion und einem Check.

## Installation

1.  **Voraussetzungen:**
    *   Ein funktionierender Checkmk-Server.
    *   Python 3 auf dem Checkmk-Server.
    *   Das `requests` Python-Modul muss installiert sein: `pip3 install requests`
    * Das Modul `keyring` sollte installiert sein: `pip3 install keyring` (Empfohlen, aber optional für die erste Einrichtung)

2.  **Dateien kopieren:**
    *   Kopiere die Datei `agent_based/xiq` nach `/usr/lib/check_mk_agent/plugins/special/xiq`.
    *   Kopiere die Datei `inventory/xiq` nach `~/local/lib/check_mk/inventory/xiq_devices` (oder `/omd/sites/<site>/local/lib/check_mk/inventory/xiq_devices` in OMD).
    *   Kopiere die Datei `checks/xiq` nach `~/local/lib/check_mk/checks/xiq_device` (oder `/omd/sites/<site>/local/lib/check_mk/checks/xiq_device` in OMD).

3.  **Dateien ausführbar machen:**
    ```bash
    chmod +x /usr/lib/check_mk_agent/plugins/special/xiq
    ```

4.  **Checkmk-Dienst neu starten (optional, aber empfohlen):**
    ```bash
    omd restart <site> # OMD
    systemctl restart check-mk-agent # systemd
    ```

## Konfiguration

Es gibt zwei Möglichkeiten, die API-Zugangsdaten zu konfigurieren:

**a) Empfohlene Methode arbeite ich noch dran:**


**b) Alternative Methode (mit Umgebungsvariablen - Nur für Testzwecke!):**

Diese Methode sollte *nur* für Testzwecke verwendet werden, da die Speicherung des API-Schlüssels in Umgebungsvariablen unsicher ist.

1.  **Umgebungsvariablen setzen:** Setze die folgenden Umgebungsvariablen auf dem Checkmk-Server:

    ```bash
    export XIQ_API_SECRET="DEIN_API_SCHLÜSSEL"
    export ADMIN_MAIL="[entfernte E-Mail-Adresse]"
    export XIQ_PASS="DEIN_PASSWORT"
    ```

    Es wird *dringend* empfohlen, diese Variablen *nicht* dauerhaft in der `.bashrc` oder ähnlichen Dateien zu speichern. 

2. **Checkmk Host Konfiguration:**
    * Erstelle einen neuen Host in Checkmk.
    * Wähle den Agententyp "Spezialagenten" aus.
    * Wähle den `xiq` Agenten aus.
    * Gib in den Agenten Einstellungen den Hostnamen und den XIQ Benutzernamen an. Beispiel: `mein_xiq_host mein_xiq_benutzer`

## Verwendung

Nach der Installation und Konfiguration sollten die neuen Services automatisch in Checkmk erkannt werden. Du kannst dann Regeln für die Überwachung der Geräte konfigurieren, z.B. für den Verbindungsstatus (`connected`) oder die Uptime (`system_up_time`).

## Funktionsweise

Der Agent ruft die ExtremeCloud IQ API ab und gibt die Geräteinformationen im Checkmk-Format aus. Die Inventory-Funktion erstellt für jedes Gerät einen eigenen Service, benannt nach dem Hostnamen des Geräts. Der Check `xiq_device` zeigt detaillierte Informationen zu jedem Gerät an, einschließlich ID, Seriennummer, MAC-Adresse, Funktion, Uptime und vielem mehr.

## Bekannte Probleme

*   Bei Problemen mit der API-Verbindung überprüfe die Logdatei `/var/log/check_mk/xiq_agent.log` für detailliertere Fehlermeldungen.

## Lizenz

Die Skripte in diesem Ordner werden ohne jegliche Gewährleistung bereitgestellt. Es gibt keine explizite Lizenz.

## Kontakt

Bei Fragen oder Problemen wende dich bitte an [deine_kontaktadresse@example.com].