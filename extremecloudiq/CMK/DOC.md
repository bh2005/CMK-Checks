Installation und Konfiguration in Checkmk:

Plugin speichern: Speichere das Skript auf dem Checkmk-Server unter /omd/sites/<site>/local/lib/python3/cmk/base/plugins/agent_based/extremecloudiq_inventory. Ersetze <site> durch den Namen deiner Checkmk-Site.
Ausführbar machen: chmod +x /omd/sites/<site>/local/lib/python3/cmk/base/plugins/agent_based/extremecloudiq_inventory
Umgebungsvariablen setzen: Setze die Umgebungsvariablen XIQ_API_KEY und XIQ_API_SECRET für den Checkmk-Benutzer. Am besten in der Site-Konfiguration: /omd/sites/<site>/etc/environment. Beispiel:
Bash

export XIQ_API_KEY="dein_api_key"
export XIQ_API_SECRET="dein_api_secret"

Nach dem Ändern der Umgebungsvariablen die Site neu starten: omd restart <site>
Regel erstellen: In Checkmk eine neue Regel unter "Discovery rules" -> "Individual program call instead of agent access" erstellen.
Condition: Keine spezielle Bedingung nötig, da das Plugin alle APs inventarisiert.
Execution:
Agent type: "No agent"
Program to execute: /omd/sites/<site>/local/lib/python3/cmk/base/plugins/agent_based/extremecloudiq_inventory
Service Discovery durchführen: Auf den Hosts (die du für die Inventarisierung verwenden möchtest, z.B. einen Dummy-Host oder den Checkmk-Server selbst) eine Service Discovery durchführen.
Erläuterungen:

Das Plugin ruft die AP-Daten über die ExtremeCloud IQ API ab.
Es formatiert die Daten in ein JSON-Format, das Checkmk versteht. Der Serial Number des Accesspoints wird als Key verwendet.
Die Regel in Checkmk sorgt dafür, dass das Plugin ausgeführt wird und die inventarisierten Daten in Checkmk verfügbar sind.
Das Plugin läuft auf dem Checkmk-Server, nicht auf den Access Points selbst.
Es verwendet die requests Bibliothek für HTTP-Anfragen und json für die JSON-Verarbeitung. Stelle sicher, dass diese Bibliotheken auf deinem Checkmk-Server installiert sind (pip3 install requests).
Wichtig: Das Plugin implementiert noch keine Paginierung. Wenn du mehr als 1000 Access Points hast, musst du die API-Abfrage mit Paginierung erweitern. Ich habe das Limit in der URL aber schonmal auf 1000 gesetzt.
Sicherheit: Die API-Schlüssel werden als Umgebungsvariablen gespeichert. Dies ist sicherer als sie direkt im Code zu hinterlegen.