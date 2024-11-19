Hier ist ein PowerShell-Skript, das den Status der Active Directory-Replikation überwacht und für die Verwendung mit dem Checkmk-Agent angepasst ist:

1. **Erstelle die Skriptdatei**:
   Speichere das folgende Skript als `check_ad_replication.ps1`:

   ```powershell
   # Import the Active Directory module
   Import-Module ActiveDirectory

   # Get the replication status for all domain controllers
   $replicationStatus = Get-ADReplicationFailure -Scope Forest

   # Check if there are any replication failures
   if ($replicationStatus.Count -eq 0) {
       Write-Output "0 AD_Replication_Status - All replications are successful."
   } else {
       $failureCount = $replicationStatus.Count
       Write-Output "2 AD_Replication_Status count=$failureCount There are $failureCount replication failures."
   }
   ```

2. **Kopiere das Skript in das Checkmk-Plugin-Verzeichnis**:
   Kopiere die Datei `check_ad_replication.ps1` in das Verzeichnis `C:\ProgramData\checkmk\agent\plugins` auf deinem Windows-Host.

3. **Stelle sicher, dass das Skript ausführbar ist**:
   Überprüfe, ob die Ausführungsrichtlinien für PowerShell-Skripte auf deinem System das Ausführen von Skripten erlauben. Du kannst dies mit dem folgenden Befehl in einer PowerShell-Sitzung überprüfen und ggf. anpassen:

   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope LocalMachine
   ```

4. **Überprüfe die Funktionalität**:
   Stelle sicher, dass der Checkmk-Agent das Skript ausführt und die Ausgabe korrekt an den Checkmk-Server sendet. Du kannst dies testen, indem du den Agent manuell ausführst:

   ```powershell
   C:\Program Files (x86)\checkmk\service\check_mk_agent.exe test
   ```

   Überprüfe die Ausgabe auf den Abschnitt, der den Status der AD-Replikation anzeigt.

### Erklärung:

- **Import-Module ActiveDirectory**: Lädt das Active Directory-Modul, das für die Abfragen benötigt wird.
- **Get-ADReplicationFailure -Scope Forest**: Ruft den Replikationsstatus für alle Domain Controller im Forest ab.
- **Write-Output**: Gibt den Status der Replikation im Checkmk-kompatiblen Format aus. Wenn keine Fehler vorliegen, wird ein OK-Status (0) ausgegeben. Bei Fehlern wird ein kritischer Status (2) mit der Anzahl der Fehler ausgegeben.

Mit diesen Schritten sollte dein PowerShell-Skript als Checkmk-Agent-Plugin funktionieren und den Status der AD-Replikation überwachen