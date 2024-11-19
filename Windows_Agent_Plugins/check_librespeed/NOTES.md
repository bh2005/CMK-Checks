Hier ist ein PowerShell-Skript, das einen lokalen LibreSpeed-Test ausführt und die Ergebnisse an den Checkmk-Agent übergibt:

1. **Erstelle die Skriptdatei**:
   Speichere das folgende Skript als `check_librespeed.ps1`:

   ```powershell
   # Define the URL of the local LibreSpeed server
   $libreSpeedUrl = "http://localhost:3000/api/v1/speedtest"

   # Perform the speed test
   $response = Invoke-RestMethod -Uri $libreSpeedUrl -Method Get

   # Extract the results
   $downloadSpeed = $response.download
   $uploadSpeed = $response.upload
   $ping = $response.ping

   # Output the results in Checkmk local check format
   Write-Output "0 LibreSpeed_DownloadSpeed download=$downloadSpeed Download Speed: $downloadSpeed Mbps"
   Write-Output "0 LibreSpeed_UploadSpeed upload=$uploadSpeed Upload Speed: $uploadSpeed Mbps"
   Write-Output "0 LibreSpeed_Ping ping=$ping Ping: $ping ms"
   ```

2. **Kopiere das Skript in das Checkmk-Plugin-Verzeichnis**:
   Kopiere die Datei `check_librespeed.ps1` in das Verzeichnis `C:\ProgramData\checkmk\agent\plugins` auf deinem Windows-Host.

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

   Überprüfe die Ausgabe auf den Abschnitt, der die Ergebnisse des LibreSpeed-Tests anzeigt.

### Erklärung:

- **Invoke-RestMethod**: Führt eine HTTP-Anfrage an den lokalen LibreSpeed-Server aus und erhält die Ergebnisse des Geschwindigkeitstests.
- **Write-Output**: Gibt die Ergebnisse im Checkmk-kompatiblen Format aus. Jeder Wert (Download-Geschwindigkeit, Upload-Geschwindigkeit und Ping) wird als separater Check ausgegeben.

Mit diesen Schritten sollte dein PowerShell-Skript als Checkmk-Agent-Plugin funktionieren und die Ergebnisse des LibreSpeed-Tests überwachen.

https://librespeed.org/

https://github.com/librespeed/speedtest
