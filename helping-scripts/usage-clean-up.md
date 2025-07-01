

# Verwendung des Skripts

## Deutsch

### Beschreibung
Dieses Bash-Skript löscht Dateien im Verzeichnis `/opt/omd/sites/$site/var/check_mk/inventory_archive/`, die älter als die angegebene Anzahl von Tagen sind. Es ist für die Verwendung mit Check_MK/OMD-Systemen gedacht, um Platz im Archivverzeichnis freizugeben.

### Verwendung
```bash
./script.sh [Tage]
```

- **Tage**: (Optional) Anzahl der Tage, nach denen Dateien als veraltet gelten und gelöscht werden. Standardwert ist 30 Tage.
- **Hilfe**: Verwende `-h` oder `--help`, um die Hilfe anzuzeigen.

### Beispiel
```bash
./script.sh 45
```
Löscht alle Dateien, die älter als 45 Tage sind, in den Archivverzeichnissen aller OMD-Sites.

### Ausgabe
Das Skript gibt für jede Site Folgendes aus:
- Verzeichnis, das durchsucht wird.
- Anzahl der gelöschten Dateien.
- Freigegebener Speicherplatz (in lesbarem Format).
Am Ende wird eine Zusammenfassung der gesamt gelöschten Dateien und des freigegebenen Speicherplatzes angezeigt.

### Voraussetzungen
- Das Skript muss mit Root- oder ausreichenden Berechtigungen ausgeführt werden, um Dateien in `/opt/omd/sites` löschen zu können.
- Das `omd`-Kommando muss verfügbar sein, um die Liste der Sites abzurufen.
- Die Befehle `find`, `rm`, `du` und `awk` müssen installiert sein (üblicherweise auf Linux-Systemen vorhanden).

### Hinweise
- **Vorsicht**: Das Skript löscht Dateien unwiderruflich. Stelle sicher, dass du die Konsequenzen verstehst, bevor du es ausführst.
- Überprüfe die Ausgabe, um sicherzustellen, dass nur die gewünschten Dateien gelöscht werden.
- Teste das Skript zunächst mit einem höheren Wert für `Tage`, um die Auswirkungen zu prüfen.

---


## English

### Description
This Bash script deletes files in the directory `/opt/omd/sites/$site/var/check_mk/inventory_archive/` that are older than the specified number of days. It is designed for use with Check_MK/OMD systems to free up space in the archive directory.

### Usage
```bash
./script.sh [days]
```

- **days**: (Optional) Number of days after which files are considered outdated and deleted. The default is 30 days.
- **Help**: Use `-h` or `--help` to display the help message.

### Example
```bash
./script.sh 45
```
Deletes all files older than 45 days in the archive directories of all OMD sites.

### Output
The script outputs the following for each site:
- The directory being processed.
- The number of deleted files.
- The amount of freed storage space (in human-readable format).
At the end, a summary of the total deleted files and freed storage space is displayed.

### Requirements
- The script must be run with root or sufficient permissions to delete files in `/opt/omd/sites`.
- The `omd` command must be available to retrieve the list of sites.
- The commands `find`, `rm`, `du`, and `awk` must be installed (typically available on Linux systems).

### Notes
- **Caution**: The script deletes files permanently. Ensure you understand the consequences before running it.
- Verify the output to confirm that only the intended files are deleted.
- Test the script with a higher `days` value initially to check its impact.

 (Optional) Number of days after which files are considered outdated and deleted. The default is 30 days.
- **Help**: Use `-h` or `--help` to display the help message.

### Example
```bash
./script.sh 45
```
Deletes all files older than 45 days in the archive directories of all OMD sites.

### Output
The script outputs the following for each site:
- The directory being processed.
- The number of deleted files.
- The amount of freed storage space (in human-readable format).
At the end, a summary of the total deleted files and freed storage space is displayed.

### Requirements
- The script must be run with root or sufficient permissions to delete files in `/opt/omd/sites`.
- The `omd` command must be available to retrieve the list of sites.
- The commands `find`, `rm`, `du`, and `awk` must be installed (typically available on Linux systems).

### Notes
- **Caution**: The script deletes files permanently. Ensure you understand the consequences before running it.
- Verify the output to confirm that only the intended files are deleted.
- Test the script with a higher `days` value initially to check its impact.

