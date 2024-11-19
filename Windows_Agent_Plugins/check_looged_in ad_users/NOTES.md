Um das PowerShell-Skript als Checkmk-Agent-Plugin zu verwenden, kannst du es in eine `.ps1`-Datei umwandeln und sicherstellen, dass es im richtigen Verzeichnis auf deinem Windows-Host liegt. Hier ist eine Schritt-für-Schritt-Anleitung:

1. **Erstelle die Skriptdatei**:
   Speichere das folgende Skript als `check_ad_loggedin_users.ps1`:

   ```powershell
   # Import the Active Directory module
   Import-Module ActiveDirectory

   # Define the AD Controller name
   $ADController = "DeinADControllerName"

   # Get all sessions on the domain controller
   $sessions = Get-WmiObject -Class Win32_LogonSession -ComputerName $ADController

   # Filter for active logon sessions
   $activeSessions = $sessions | Where-Object { $_.LogonType -eq 2 }

   # Get the unique users from the active sessions
   $uniqueUsers = $activeSessions | ForEach-Object {
       $user = Get-WmiObject -Class Win32_LoggedOnUser -Filter "LogonId = '$($_.LogonId)'" -ComputerName $ADController
       $user.Antecedent -match '\\(.+)$' | Out-Null
       $matches[1]
   } | Select-Object -Unique

   # Output the count of unique users
   $uniqueUsersCount = $uniqueUsers.Count
   Write-Output "0 AD_LoggedInUsers count=$uniqueUsersCount Anzahl der aktuell angemeldeten Benutzer: $uniqueUsersCount"
   ```

2. **Kopiere das Skript in das Checkmk-Plugin-Verzeichnis**:
   Kopiere die Datei `check_ad_loggedin_users.ps1` in das Verzeichnis `C:\ProgramData\checkmk\agent\plugins` auf deinem Windows-Host.

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

   Überprüfe die Ausgabe auf den Abschnitt, der die Anzahl der aktuell angemeldeten Benutzer anzeigt.

Mit diesen Schritten sollte dein PowerShell-Skript als Checkmk-Agent-Plugin funktionieren und die Anzahl der aktuell angemeldeten Benutzer überwachen. 