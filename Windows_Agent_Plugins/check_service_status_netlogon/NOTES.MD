Hier ist ein PowerShell-Skript, das den Status von SYSVOL und Netlogon überwacht und für die Verwendung mit dem Checkmk-Agent angepasst ist:

1. **Erstelle die Skriptdatei**:
   Speichere das folgende Skript als `check_sysvol_netlogon.ps1`:

   ```powershell
   # Überprüfe den Status von SYSVOL und Netlogon

   # Funktion zur Überprüfung des Dienststatus
   function Check-ServiceStatus {
       param (
           [string]$serviceName
       )
       $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
       if ($service -and $service.Status -eq 'Running') {
           Write-Output "0 $serviceName - $serviceName is running."
       } else {
           Write-Output "2 $serviceName - $serviceName is not running."
       }
   }

   # Überprüfe den SYSVOL-Dienst
   Check-ServiceStatus -serviceName 'Netlogon'

   # Überprüfe den Netlogon-Dienst
   Check-ServiceStatus -serviceName 'Netlogon'
   ```

2. **Kopiere das Skript in das Checkmk-Plugin-Verzeichnis**:
   Kopiere die Datei `check_sysvol_netlogon.ps1` in das Verzeichnis `C:\ProgramData\checkmk\agent\plugins` auf deinem Windows-Host.

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

   Überprüfe die Ausgabe auf den Abschnitt, der den Status von SYSVOL und Netlogon anzeigt.

### Erklärung:

- **Check-ServiceStatus**: Eine Funktion, die den Status eines angegebenen Dienstes überprüft und den Status im Checkmk-kompatiblen Format ausgibt.
- **Get-Service**: Ruft den Status des angegebenen Dienstes ab.
- **Write-Output**: Gibt den Status des Dienstes aus. Wenn der Dienst läuft, wird ein OK-Status (0) ausgegeben. Wenn der Dienst nicht läuft, wird ein kritischer Status (2) ausgegeben.

Mit diesen Schritten sollte dein PowerShell-Skript als Checkmk-Agent-Plugin funktionieren und den Status von SYSVOL und Netlogon überwachen.