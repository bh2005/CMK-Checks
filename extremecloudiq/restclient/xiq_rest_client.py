#!/usr/bin/env python3

import requests
import logging
from argparse import ArgumentParser
import json
import os
from typing import Optional, List, Dict, Any
import time
import datetime
import redis  # Importiere das Redis-Modul
import csv   # Importiere das csv-Modul

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

XIQ_BASE_URL = "https://api.extremecloudiq.com"
API_KEY_FILE = "xiq_api_token.txt"
PAGE_SIZE = 100
REDIS_HOST = 'localhost'  # Standard-Host für Redis
REDIS_PORT = 6379        # Standard-Port für Redis
REDIS_DB = 0             # Standard-Datenbank in Redis

def load_api_token(filename: str = API_KEY_FILE) -> Optional[str]:
    """Lädt den API-Token aus der angegebenen Datei."""
    try:
        with open(filename, "r") as f:
            return f.readline().strip()
    except FileNotFoundError:
        log.warning(f"API-Token-Datei '{filename}' nicht gefunden.")
        return None
    except IOError as e:
        log.error(f"Fehler beim Lesen der API-Token-Datei '{filename}': {e}")
        return None

def get_xiq_api_token(base_url: str, username: str, password: str) -> Optional[str]:
    """Loggt sich bei der ExtremeCloud IQ API ein und ruft den API-Token ab."""
    url = f"{base_url}/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}
    try:
        log.info(f"Sende Login-Anfrage an: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        api_token = json_response.get("access_token")
        if api_token:
            log.info("API-Token erfolgreich abgerufen.")
            return api_token
        else:
            log.error("Fehler: API-Token nicht in der Antwort gefunden.")
            log.debug(f"Antwortkörper: {json.dumps(json_response, indent=4)}")
            return None
    except requests.exceptions.RequestException as e:
        log.error(f"Fehler bei der Login-Anfrage: {e}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Fehler beim Decodieren der JSON-Antwort: {e}")
        return None

def save_api_token(token: str, filename: str = API_KEY_FILE) -> None:
    """Speichert den API-Token in einer lokalen Datei."""
    try:
        with open(filename, "w") as f:
            f.write(token)
        log.info(f"API-Token erfolgreich in '{filename}' gespeichert.")
    except IOError as e:
        log.error(f"Fehler beim Speichern des API-Tokens in '{filename}': {e}")

def format_mac_address(mac: Optional[str]) -> Optional[str]:
    """Formatiert eine 12-stellige MAC-Adresse mit Doppelpunkten."""
    if mac and len(mac) == 12:
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    return mac

def calculate_uptime(timestamp_ms):
    """Calculates the uptime between a given timestamp and the current time.

    Args:
        timestamp_ms: The timestamp in milliseconds.

    Returns:
        A string in the format "days, hours:minutes:seconds" or None in case of an error.
    """
    if not isinstance(timestamp_ms, (int, float)):
        return None

    try:
        current_time_ms = int(time.time() * 1000)
        uptime_ms = current_time_ms - int(timestamp_ms)

        if uptime_ms < 0:
            return "Timestamp is in the future"

        uptime_delta = datetime.timedelta(milliseconds=uptime_ms)
        days = uptime_delta.days
        if days > 2000:
            return "offline"
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} days, {hours:02}:{minutes:02}:{seconds:02}"
    except OverflowError:
        return "Uptime too large for timedelta"
    except TypeError:
        return None

def process_device(device: Dict[str, Any]) -> Dict[str, Any]:
    """Verarbeitet ein einzelnes Geräteobjekt und formatiert MAC-Adresse und Uptime."""
    if 'mac_address' in device:
        device['mac_address'] = format_mac_address(device['mac_address'])
    if 'system_up_time' in device:
        device['uptime'] = calculate_uptime(device['system_up_time'])
    return device

def get_device_list_paginated(base_url: str, api_token: str) -> Optional[List[Dict[str, Any]]]:
    """
    Ruft die Liste der Geräte von der ExtremeCloud IQ API paginiert mit der Ansicht 'FULL' ab
    und formatiert MAC-Adresse und Uptime.
    """
    page = 1
    all_devices = []

    while True:
        url = f"{base_url}/devices?page={page}&limit={PAGE_SIZE}&views=FULL"
        headers = {"Authorization": f"Bearer {api_token}"}
        log.info(f"Fetching devices page {page}...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get('data', [])
            if not data:
                log.info("No more devices found.")
                break
            for raw_device in data:
                device = process_device(raw_device)
                all_devices.append(device)
            if len(data) < PAGE_SIZE:
                log.info("Reached the last page of devices.")
                break
            page += 1
            time.sleep(3)
        except requests.exceptions.RequestException as e:
            log.error(f"Error fetching devices page {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            log.error(f"Error decoding JSON response for devices page {page}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error during device list retrieval: {e}")
            return None

    log.info(f"Successfully retrieved and processed {len(all_devices)} devices (using 'FULL' view).")
    return all_devices

def store_devices_in_redis(devices: List[Dict[str, Any]]) -> None:
    """Speichert die Liste der Geräte in einer Redis-Datenbank und verwendet den Hostnamen als Schlüssel."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        for device in devices:
            key = f"xiq:device:{device.get('hostname') or device.get('serial_number') or device.get('mac_address')}"
            r.set(key, json.dumps(device))
        log.info(f"Erfolgreich {len(devices)} Geräte in Redis gespeichert (Schlüssel: Hostname > Seriennummer > MAC-Adresse).")
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis: {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Speichern in Redis: {e}")

def convert_list_to_csv(devices: List[Dict[str, Any]], csv_file: str) -> None:
    """Konvertiert die Liste der Geräte in eine CSV-Datei."""
    if not devices:
        log.warning("Keine Geräte zum Schreiben in die CSV-Datei.")
        return

    fieldnames = [
        "id", "create_time", "update_time", "serial_number", "mac_address",
        "device_function", "product_type", "hostname", "ip_address", "software_version",
        "device_admin_state", "connected", "last_connect_time", "network_policy_name",
        "network_policy_id", "primary_ntp_server_address", "primary_dns_server_address",
        "subnet_mask", "default_gateway", "ipv6_address", "ipv6_netmask", "simulated",
        "display_version", "location_id", "org_id", "org_name", "city_id", "city_name",
        "building_id", "building_name", "floor_id", "floor_name", "country_code",
        "description", "remote_port_id", "remote_system_id", "remote_system_name",
        "local_interface", "system_up_time_raw", "config_mismatch", "managed_by",
        "thread0_eui64", "thread0_ext_mac", "uptime" # Hier wird 'uptime' verwendet
    ]

    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for device in devices:
                locations = device.get("locations", [])
                lldp_cdp_infos = device.get("lldp_cdp_infos", [])

                row = {
                    "id": device.get("id"),
                    "create_time": device.get("create_time"),
                    "update_time": device.get("update_time"),
                    "serial_number": device.get("serial_number"),
                    "mac_address": device.get("mac_address"),
                    "device_function": device.get("device_function"),
                    "product_type": device.get("product_type"),
                    "hostname": device.get("hostname"),
                    "ip_address": device.get("ip_address"),
                    "software_version": device.get("software_version"),
                    "device_admin_state": device.get("device_admin_state"),
                    "connected": device.get("connected"),
                    "last_connect_time": device.get("last_connect_time"),
                    "network_policy_name": device.get("network_policy_name"),
                    "network_policy_id": device.get("network_policy_id"),
                    "primary_ntp_server_address": device.get("primary_ntp_server_address"),
                    "primary_dns_server_address": device.get("primary_dns_server_address"),
                    "subnet_mask": device.get("subnet_mask"),
                    "default_gateway": device.get("default_gateway"),
                    "ipv6_address": device.get("ipv6_address"),
                    "ipv6_netmask": device.get("ipv6_netmask"),
                    "simulated": device.get("simulated"),
                    "display_version": device.get("display_version"),
                    "location_id": device.get("location_id"),
                    "org_id": locations[0].get("id") if locations and len(locations) > 0 else "",
                    "org_name": locations[0].get("name") if locations and len(locations) > 0 else "",
                    "city_id": locations[1].get("id") if locations and len(locations) > 1 else "",
                    "city_name": locations[1].get("name") if locations and len(locations) > 1 else "",
                    "building_id": locations[2].get("id") if locations and len(locations) > 2 else "",
                    "building_name": locations[2].get("name") if locations and len(locations) > 2 else "",
                    "floor_id": locations[3].get("id") if locations and len(locations) > 3 else "",
                    "floor_name": locations[3].get("name") if locations and len(locations) > 3 else "",
                    "country_code": device.get("country_code"),
                    "description": device.get("description"),
                    "remote_port_id": lldp_cdp_infos[0].get("port_id") if lldp_cdp_infos and len(lldp_cdp_infos) > 0 else "",
                    "remote_system_id": lldp_cdp_infos[0].get("system_id") if lldp_cdp_infos and len(lldp_cdp_infos) > 0 else "",
                    "remote_system_name": lldp_cdp_infos[0].get("system_name") if lldp_cdp_infos and len(lldp_cdp_infos) > 0 else "",
                    "local_interface": lldp_cdp_infos[0].get("interface_name") if lldp_cdp_infos and len(lldp_cdp_infos) > 0 else "",
                    "system_up_time_raw": device.get("system_up_time"), # Behalten des rohen Werts bei
                    "config_mismatch": device.get("config_mismatch"),
                    "managed_by": device.get("managed_by"),
                    "thread0_eui64": device.get("thread0_eui64"),
                    "thread0_ext_mac": device.get("thread0_ext_mac"),
                    "uptime": device.get("uptime") # Verwende das berechnete 'uptime'-Feld
                }
                writer.writerow(row)
        log.info(f"Geräteliste erfolgreich in '{csv_file}' gespeichert.")
    except IOError as e:
        log.error(f"Fehler beim Schreiben der Geräteliste in '{csv_file}': {e}")

def main():
    """
    Hauptfunktion des Skripts zum Einloggen (falls nötig), Abrufen der XIQ-Geräteliste (paginiert),
    Ausgeben auf der Konsole (optional reduziert), Speichern in einer JSON-Datei, in Redis und als CSV.
    """
    parser = ArgumentParser(description="Interagiert mit der ExtremeCloud IQ API.")
    auth_group = parser.add_mutually_exclusive_group(required=True)
    auth_group.add_argument("-k", "--api_key_file", dest="api_key_file", help=f"Pfad zur Datei mit dem gespeicherten API-Token (Standard: {API_KEY_FILE})", default=API_KEY_FILE)
    auth_group.add_argument("-u", "--username", dest="username", help="Benutzername für die XIQ API (für erstmaligen Login oder Token-Erneuerung)")
    auth_group.add_argument("-p", "--password", dest="password", help="Passwort für die XIQ API (für erstmaligen Login oder Token-Erneuerung)")
    parser.add_argument("-s", "--server", dest="serverRoot", help="Basis-URL der XIQ API", default=XIQ_BASE_URL)
    parser.add_argument("--get-devicelist", action="store_true", help="Ruft die Liste der Geräte ab.")
    parser.add_argument("-o", "--output_file", dest="output_file", help="Dateiname für die Ausgabe der Geräteliste (JSON, Standard: XiqDeviceList.json)", default="XiqDeviceList.json")
    parser.add_argument("--store-redis", action="store_true", help="Speichert die Geräteinformationen in Redis.")
    parser.add_argument("--show-pretty", action="store_true", help="Zeigt eine vereinfachte Ausgabe der Geräte (id, hostname, mac, ip) auf der Konsole.")
    parser.add_argument("--output-csv", dest="output_csv_file", help="Dateiname für die Ausgabe der Geräteliste als CSV.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe aktivieren")

    args = parser.parse_args()

    if args.verbose:
        log.getLogger().setLevel(logging.DEBUG)
        log.debug("Ausführliche Ausgabe aktiviert.")

    api_token = None

    if args.username and args.password:
        # Login durchführen und Token speichern
        api_token = get_xiq_api_token(args.serverRoot, args.username, args.password)
        if api_token:
            save_api_token(api_token, args.api_key_file)
        else:
            log.error("Fehler beim Abrufen des API-Tokens. Das Skript wird beendet.")
            sys.exit(1)
    else:
        # Token aus Datei laden
        api_token = load_api_token(args.api_key_file)
        if not api_token:
            log.error(f"Kein gültiger API-Token gefunden. Bitte verwenden Sie '-u' und '-p' zum erstmaligen Login.")
            sys.exit(1)

    if args.get_devicelist:
        if api_token:
            device_list = get_device_list_paginated(args.serverRoot, api_token)
            if device_list:
                if args.show_pretty:
                    print("Geräteinformationen:")
                    for device in device_list:
                        print(f"  ID: {device.get('id')}")
                        print(f"  Hostname: {device.get('hostname')}")
                        print(f"  MAC-Adresse: {device.get('mac_address')}")
                        print(f"  IP-Adresse: {device.get('ip_address')}")
                        print("-" * 20)
                else:
                    print(json.dumps(device_list, indent=4))

                if args.output_file:
                    try:
                        with open(args.output_file, 'w') as f:
                            json.dump(device_list, f, indent=4)
                        log.info(f"Geräteliste erfolgreich in '{args.output_file}' gespeichert.")
                    except IOError as e:
                        log.error(f"Fehler beim Schreiben der Geräteliste in '{args.output_file}': {e}")

                if args.store_redis:
                    store_devices_in_redis(device_list)

                if args.output_csv_file:
                    convert_list_to_csv(device_list, args.output_csv_file)
            else:
                log.error("Fehler beim Abrufen der Geräteliste.")
                sys.exit(1)
        else:
            log.error("Kein API-Token vorhanden. Bitte loggen Sie sich zuerst ein oder geben Sie den Pfad zur Token-Datei an.")
            sys.exit(1)

if __name__ == "__main__":
    main()