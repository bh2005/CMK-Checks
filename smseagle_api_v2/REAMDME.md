.md# smseagle_api_v2.py

Dieses Python-Skript ermöglicht das Versenden von SMS-, TTS- (Text-to-Speech) und Wave-Nachrichten über die SMS Eagle API. Es verwendet die `argparse`-Bibliothek zur Verarbeitung von Kommandozeilenargumenten, die `requests`-Bibliothek für HTTP-Anfragen und die `logging`-Bibliothek zur Protokollierung.

## Voraussetzungen

* Python 3.x
* Die folgenden Python-Bibliotheken:
    * `requests`
    * `json`
    * `argparse`
    * `logging`
    * `logging.handlers`
* Eine `config.json`-Datei mit den API-Zugangsdaten (siehe Abschnitt "Konfiguration").
* Das Kommando `tac` (Bestandteil von `coreutils`), um die Logdatei nach Rotation umzukehren (optional).

## Installation

1.  Speichern Sie das Skript unter einem beliebigen Namen (z.B. `smseagle_api_v2.py`).
2.  Installieren Sie die erforderlichen Python-Bibliotheken:
    ```bash
    pip install requests
    ```
3.  Erstellen Sie eine `config.json`-Datei im selben Verzeichnis wie das Skript (siehe Abschnitt "Konfiguration").
4.  (Optional) Installieren Sie `coreutils` für die Logrotation:
    ```bash
    sudo apt-get install coreutils  # oder ein anderer Befehl, abhängig von Ihrer Distribution
    ```

## Konfiguration

Erstellen Sie eine Datei namens `config.json` im selben Verzeichnis wie das Skript. Fügen Sie die folgenden Schlüssel-Wert-Paare hinzu und ersetzen Sie die Platzhalter durch Ihre tatsächlichen API-Zugangsdaten:

```json
{
  "smseagleip1": "http://IP-Adresse des ersten SMS Eagle Servers/",
  "smseagleip2": "IP-Adresse des zweiten SMS Eagle Servers (optional)",
  "access-token1": "Access Token für den ersten SMS Eagle Server",
  "access-token2": "Access Token für den zweiten SMS Eagle Server (optional)"
}
