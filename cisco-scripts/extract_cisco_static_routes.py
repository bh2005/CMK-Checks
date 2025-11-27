#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cisco Static Routes auslesen per SSH
Erweiterungen: Router aus Datei lesen, Export nach CSV/JSON, CLI-Argumente
"""

import re
import sys
import argparse
import csv
import json
from datetime import datetime
from netmiko import ConnectHandler

# ==================== FUNKTIONEN ZUM DATENMANAGEMENT ====================

def parse_cli_arguments():
    """Definiert und parst Kommandozeilen-Argumente."""
    parser = argparse.ArgumentParser(
        description="Liest statische Routen von Cisco-Geräten via SSH aus."
    )
    
    # Argumente für Konfiguration via CLI
    parser.add_argument("--host", default="192.168.1.1", help="Einzelner Host (Standard: 192.168.1.1)")
    parser.add_argument("-u", "--username", default="admin", help="SSH-Benutzername")
    parser.add_argument("-p", "--password", default="deinpasswort", help="SSH-Passwort")
    parser.add_argument("-e", "--enable-pass", default="deinenablepasswort", help="Optionales Enable-Passwort")
    parser.add_argument("-d", "--device-type", default="cisco_ios", 
                        choices=["cisco_ios", "cisco_xe", "cisco_asa", "cisco_nxos"], 
                        help="Gerätetyp (Standard: cisco_ios)")
    
    # Argumente für die neuen Funktionen
    parser.add_argument("-f", "--file", help="Pfad zur Textdatei mit einer Host-IP pro Zeile")
    parser.add_argument("-x", "--export", choices=["csv", "json"], help="Exportformat (csv oder json)")
    parser.add_argument("-o", "--output-file", default="routes_export.txt", help="Name der Exportdatei (mit Endung)")

    return parser.parse_args()

def load_devices_from_file(filepath, username, password, enable_pass, device_type):
    """Liest Hosts aus einer Datei und erstellt eine Liste von Geräte-Dictionaries."""
    devices = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                host = line.strip()
                if host and not host.startswith('#'):
                    devices.append({
                        "host": host,
                        "username": username,
                        "password": password,
                        "secret": enable_pass,
                        "device_type": device_type,
                    })
        print(f"[INFO] {len(devices)} Geräte aus '{filepath}' geladen.")
    except FileNotFoundError:
        print(f"[FEHLER] Datei '{filepath}' nicht gefunden.")
        sys.exit(1)
    return devices

def save_to_csv(data, filename):
    """Speichert die extrahierten Routen als CSV-Datei."""
    if not data:
        print("[WARN] Keine Daten zum Speichern vorhanden.")
        return
        
    fieldnames = ["hostname", "vrf", "network", "ad", "metric", "nexthop", "interface"]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"[ERFOLG] Daten als CSV in '{filename}' gespeichert.")
    except Exception as e:
        print(f"[FEHLER] Fehler beim Speichern der CSV: {e}")

def save_to_json(data, filename):
    """Speichert die extrahierten Routen als JSON-Datei."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"[ERFOLG] Daten als JSON in '{filename}' gespeichert.")
    except Exception as e:
        print(f"[FEHLER] Fehler beim Speichern der JSON: {e}")

# ==================== NETZWERK & PARSING FUNKTIONEN ====================

def get_static_routes(device: dict) -> str:
    """Stellt eine SSH-Verbindung her und fragt statische Routen ab."""
    
    # Netmiko mit with-Statement für automatische Trennung
    try:
        net_connect = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            username=device["username"],
            password=device["password"],
            secret=device.get("secret"),
            global_delay_factor=2,
        )
    except Exception as e:
        raise ConnectionError(f"Verbindungsfehler zu {device['host']}: {e}")

    with net_connect:
        net_connect.enable()
        print(f"[+] Verbunden mit {device['host']} – hole statische Routen...")
        
        combined_output = ""
        
        # IOS / IOS-XE
        if device["device_type"] in ["cisco_ios", "cisco_xe"]:
            # 1. Globale statische Routen
            global_routes = net_connect.send_command("show ip route static | include ^S")
            
            # 2. VRF statische Routen: Abfrage des vollständigen VRF-Routing-Tabelle-Blocks
            vrf_raw = net_connect.send_command("show ip route vrf * static")
            
            vrf_routes_list = []
            current_vrf = "global" 
            for line in vrf_raw.splitlines():
                # Finde den VRF-Namen (z.B. "Routing Table: myvrf")
                vrf_match = re.search(r"Routing Table: (\S+)", line)
                if vrf_match:
                    current_vrf = vrf_match.group(1)
                
                # Wenn es eine statische Route ist (beginnt mit 'S ')
                if line.strip().startswith('S '):
                    # Präpariere die Zeile für das einfache Parsing, indem der VRF-Name 
                    # als separates Feld vorangestellt wird.
                    vrf_routes_list.append(f"S {current_vrf} {line.strip()[2:]}")
            
            combined_output = global_routes + "\n" + "\n".join(vrf_routes_list)
        
        # ASA / NX-OS (Behält die Original-Logik bei)
        elif device["device_type"] == "cisco_asa":
            combined_output = net_connect.send_command("show route | include S")
        elif device["device_type"] == "cisco_nxos":
            output = net_connect.send_command("show ip route static | include ^\\*")
            vrf_output = net_connect.send_command("show ip route vrf all static | include ^\\*")
            combined_output = output + "\n" + vrf_output

        return combined_output

def parse_and_print_routes(raw_output: str, hostname: str, all_routes_data: list = None):
    """Parst die rohe Ausgabe, druckt sie und speichert die Ergebnisse in der Liste."""
    
    print(f"\n{'='*60}")
    print(f"STATISCHE ROUTEN AUF {hostname.upper()} – {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    lines = raw_output.strip().splitlines()
    if not lines or "S" not in raw_output and "*" not in raw_output:
        print("Keine statischen Routen gefunden.")
        return

    # Regex für die geparste Ausgabe (Globale Routen: S ...; VRF-Routen: S <VRF> ...)
    pattern = re.compile(
        # Code (S oder *) und optional der VRF-Name
        r"^(?P<code>[S\*] ?)"
        r"(?:(?P<vrf>\S+) )?"               # VRF-Name (z.B. "myvrf" oder "global")
        r"(?P<network>\d+\.\d+\.\d+\.\d+/\d+|\S+)"   # Netzwerk/Prefix
        r"(?: is directly connected)?(?:,)?\s*"   # Optionaler Text für direkt verbundene Netze
        r"(?: \[?(?P<ad>\d+)/(?P<metric>\d+)\]? )?" # AD/Metric
        r"(?:via (?P<nexthop>\S+))?"        # Optionaler Next-Hop
        r"(?:, (?P<interface>\S+))?"
        r"(?:, \S+)?$"
    )

    routes = []
    for line in lines:
        line = line.strip()
        # Überprüfen, ob es eine Route oder ein VRF-Trennzeichen ist
        if not line.startswith(('S ', '* ')): 
            continue
            
        m = pattern.search(line)
        if m:
            route_dict = m.groupdict()
            
            # AD und Metric fehlen oft bei direkt verbundenen Routen
            ad_val = route_dict['ad'] or '1' # Statische Routen haben AD 1
            metric_val = route_dict['metric'] or '-'
            
            # Falls kein VRF-Name gefunden wurde (Globale Route), setze auf 'global'
            vrf_val = route_dict['vrf'] or 'global'
            
            # Wenn Interface gefunden wurde, ist es wahrsch. direkt verbunden.
            # Next-Hop fehlt bei direkt verbundenen Routen oft oder ist die IP der Interface
            nexthop_val = route_dict['nexthop'] or (route_dict['interface'] if route_dict['interface'] else '-')

            # Führe das finale Dictionary zusammen
            final_route = {
                "hostname": hostname,
                "vrf": vrf_val,
                "network": route_dict['network'],
                "ad": ad_val,
                "metric": metric_val,
                "nexthop": nexthop_val,
                "interface": route_dict['interface'] or "-",
            }
            routes.append(final_route)
            
            # Füge der globalen Liste hinzu, wenn sie übergeben wurde
            if all_routes_data is not None:
                all_routes_data.append(final_route)

    # Schöne Tabelle ausgeben
    print(f"{'VRF':<15}{'Prefix':<25}{'AD/Metric':<12}{'Next-Hop':<20}{'Interface':<15}")
    print("-" * 87)
    for r in routes:
        print(f"{r['vrf']:<15}{r['network']:<25}{r['ad']}/{r['metric']:<10}{r['nexthop']:<20}{r['interface']:<15}")

    print(f"\nGesamt: {len(routes)} statische Routen gefunden auf {hostname}.\n")

# ==================== MAIN LOGIK ====================

def main():
    args = parse_cli_arguments()
    all_routes = []
    
    # 1. Liste der Geräte ermitteln
    if args.file:
        # Fall 1: Router aus Datei lesen
        devices = load_devices_from_file(
            args.file, args.username, args.password, args.enable_pass, args.device_type
        )
    else:
        # Fall 2: Einzelnen Router von der Kommandozeile verwenden
        devices = [{
            "host": args.host,
            "username": args.username,
            "password": args.password,
            "secret": args.enable_pass if args.enable_pass else "",
            "device_type": args.device_type,
        }]

    # 2. Routen von allen Geräten abfragen
    if not devices:
        print("[FEHLER] Keine Geräte zum Abfragen gefunden. Bitte Host/Datei angeben.")
        sys.exit(1)
        
    for device in devices:
        try:
            raw_output = get_static_routes(device)
            parse_and_print_routes(raw_output, device["host"], all_routes)
        except ConnectionError as e:
            print(f"[FEHLER] Überspringe {device['host']}: {e}")
        except Exception as e:
            print(f"[FEHLER] Unbekannter Fehler bei {device['host']}: {e}")

    # 3. Optionaler Export
    if args.export == "csv":
        save_to_csv(all_routes, args.output_file)
    elif args.export == "json":
        save_to_json(all_routes, args.output_file)
    elif all_routes and args.export:
        print(f"[FEHLER] Unbekanntes Exportformat '{args.export}'.")
        
if __name__ == "__main__":
    main()