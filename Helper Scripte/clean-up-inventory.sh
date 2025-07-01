#!/bin/bash

# Funktion zur Anzeige der Hilfe
show_help() {
  echo "Verwendung: $0 [Tage]"
  echo "Löscht Dateien im Verzeichnis /opt/omd/sites/\$site/var/check_mk/inventory_archive/, die älter als die angegebene Anzahl von Tagen sind."
  echo "Standardwert für Tage ist 30."
  echo "Beispiel: $0 45"
  exit 1
}

# Überprüfe, ob das Hilfeargument angegeben wurde
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  show_help
fi

# Standardwert für Tage ist 30
days=${1:-30}

# Hole die Namen der Sites
sites=$(omd sites | awk '{print $1}')

# Initialisiere Zähler und Speicherplatz
total_deleted_files=0
total_freed_space=0

# Iteriere über die Sites und lösche die Dateien
for site in $sites; do
  archive_dir="/opt/omd/sites/$site/var/check_mk/inventory_archive/"
  echo "Verzeichnis: $archive_dir"

  # Finde und lösche Dateien, die älter als die angegebene Anzahl von Tagen sind
  deleted_files=$(find $archive_dir -type f -mtime +$days -exec rm -v {} + | wc -l)
  freed_space=$(du -sb $archive_dir | awk '{print $1}')

  # Aktualisiere die Gesamtwerte
  total_deleted_files=$((total_deleted_files + deleted_files))
  total_freed_space=$((total_freed_space + freed_space))

  echo "Site: $site"
  echo "Gelöschte Dateien: $deleted_files"
  echo "Freigegebener Speicherplatz: $(du -sh $archive_dir | awk '{print $1}')"
  echo
done

# Ausgabe der Gesamtwerte
echo "Gesamt gelöschte Dateien: $total_deleted_files"
echo "Gesamt freigegebener Speicherplatz: $(du -sh /opt/omd/sites | awk '{print $1}')"
