#!/usr/bin/env python3

from argparse import ArgumentParser
import json
import logging
import os
import sys
import time
import csv
from typing import List, Dict, Any, Optional
import redis
import requests
from dotenv import load_dotenv

# Umgebungsvariablen laden
load_dotenv()
XIQ_BASE_URL = os.getenv("XIQ_BASE_URL", "https://api.extremecloudiq.com")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_AP_DB = int(os.getenv("REDIS_AP_DB", 3))  # DB 3 für APs
REDIS_LOCATIONS_DB = int(os.getenv("REDIS_LOCATIONS_DB", 1))
PAGE_SIZE = int(os.getenv("PAGE_SIZE", 100))
API_SECRET = None  # Global für den API-Token

log = logging.getLogger(__name__)

def load_api_token(file_path: str) -> Optional[str]:
    """Lädt den API-Token aus einer Datei."""
    try:
        with open(file_path, 'r') as f:
            token = f.readline().strip()
            if token:
                global API_SECRET
                API_SECRET = token
                log.info(f"API-Token erfolgreich aus '{file_path}' geladen.")
                return token
            else:
                log.warning(f"Die Datei '{file_path}' ist leer.")
                return None
    except FileNotFoundError:
        log.warning(f"Die Datei '{file_path}' wurde nicht gefunden.")
        return None
    except Exception as e:
        log.error(f"Fehler beim Lesen der Token-Datei '{file_path}': {e}")
        return None

def save_api_token(token: str, file_path: str):
    """Speichert den API-Token in einer Datei."""
    try:
        with open(file_path, 'w') as f:
            f.write(token)
        log.info(f"API-Token erfolgreich in '{file_path}' gespeichert.")
    except Exception as e:
        log.error(f"Fehler beim Speichern des API-Tokens in '{file_path}': {e}")

def load_credentials_from_env() -> Optional[tuple[str, str]]:
    """Lädt Benutzername und Passwort aus Umgebungsvariablen."""
    username = os.getenv("XIQ_USERNAME")
    password = os.getenv("XIQ_PASSWORD")
    if username and password:
        log.info("Anmeldeinformationen erfolgreich aus der .env-Datei geladen.")
        return username, password
    return None

def save_credentials_to_env(username: str, password: str):
    """Speichert Benutzername und Passwort in einer .env-Datei."""
    try:
        with open(".env", "w") as f:
            f.write(f"XIQ_USERNAME={username}\n")
            f.write(f"XIQ_PASSWORD={password}\n")
        log.info("Anmeldeinformationen erfolgreich in '.env' gespeichert.")
    except Exception as e:
        log.error(f"Fehler beim Schreiben der Anmeldeinformationen in '.env': {e}")

def get_xiq_api_token(base_url: str, username: str, password: str) -> Optional[str]:
    """Loggt sich bei der ExtremeCloud IQ API ein und ruft den API-Token ab."""
    global API_SECRET
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
            API_SECRET = api_token
            return api_token
        else:
            log.error("Fehler: API-Token nicht in der Antwort gefunden.")
            log.debug(f"Antwortkörper: {json.dumps(json_response, indent=4)}")
            return None
    except requests.exceptions.RequestException as e:
        log.error(f"Fehler bei der Login-Anfrage: {e}")
        print(f"Fehler bei der Login-Anfrage: {e}")
        if isinstance(e, requests.exceptions.HTTPError) and response is not None:
            if response.status_code == 401:
                log.error("Authentifizierungsfehler beim Login (401). Falsche Anmeldeinformationen?")
                print("Authentifizierungsfehler beim Login (401). Falsche Anmeldeinformationen?")
            else:
                log.error(f"HTTP-Fehler beim Login (Code: {response.status_code}).")
                print(f"HTTP-Fehler beim Login (Code: {response.status_code}).")
        return None

def get_api_token(args):
    """Lädt den API-Token entweder aus der Datei oder ruft ihn per Login ab."""
    env_credentials = load_credentials_from_env()
    if env_credentials:
        args.username, args.password = env_credentials
    if args.username and args.password:
        token = get_xiq_api_token(args.server, args.username, args.password)
        if token:
            save_api_token(token, args.api_key_file)
        return token
    else:
        return load_api_token(args.api_key_file)

def get_device_list_paginated(base_url: str, api_token: str) -> Optional[List[Dict[str, Any]]]:
    """
    Ruft die Liste der Geräte von der ExtremeCloud IQ API paginiert mit der Ansicht 'FULL' ab
    und filtert nur Access Points (APs).
    """
    page = 1
    all_devices = []
    while True:
        url = f"{base_url}/devices?page={page}&limit={PAGE_SIZE}&views=FULL"
        headers = {"Authorization": f"Bearer {api_token}"}
        log.info(f"Fetching devices page {page} from URL: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get('data', [])
            log.debug(f"Raw API response for page {page}: {json.dumps(data[:2], indent=4)}")
            if not data:
                log.info("No more devices found.")
                break
            for raw_device in data:
                if raw_device.get('device_function') == 'AP':
                    device = process_device(raw_device)
                    all_devices.append(device)
            if len(data) < PAGE_SIZE:
                log.info("Reached the last page of devices.")
                break
            page += 1
            time.sleep(3)
        except requests.exceptions.RequestException as e:
            log.error(f"Error fetching devices page {page}: {e}")
            print(f"Error fetching devices page {page}: {e}")
            if isinstance(e, requests.exceptions.HTTPError) and response is not None:
                if response.status_code == 401:
                    log.warning("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen. Bitte loggen Sie sich erneut ein.")
                    print("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen. Bitte loggen Sie sich erneut ein.")
                else:
                    log.error(f"HTTP-Fehler beim Abrufen der Geräteliste (Seite {page}, Code: {response.status_code}).")
                    print(f"HTTP-Fehler beim Abrufen der Geräteliste (Seite {page}, Code: {response.status_code}).")
            elif isinstance(e, requests.exceptions.ConnectionError):
                log.error(f"Verbindungsfehler beim Zugriff auf die API (Seite {page}): {e}")
                print(f"Verbindungsfehler beim Zugriff auf die API (Seite {page}): {e}")
            else:
                log.error(f"Unerwarteter Fehler beim Abrufen der Geräteliste (Seite {page}): {e}")
                print(f"Unerwarteter Fehler beim Abrufen der Geräteliste (Seite {page}): {e}")
            return None
        except json.JSONDecodeError as e:
            log.error(f"Error decoding JSON response for devices page {page}: {e}")
            print(f"Error decoding JSON response for devices page {page}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error during device list retrieval: {e}")
            print(f"Unexpected error during device list retrieval: {e}")
            return None
    log.info(f"Successfully retrieved {len(all_devices)} APs.")
    return all_devices

def get_device_by_id(base_url: str, api_token: str, device_id: str) -> Optional[Dict[str, Any]]:
    """Ruft die detaillierten Informationen für ein einzelnes Gerät anhand seiner ID ab."""
    url = f"{base_url}/devices/{device_id}?views=FULL"
    headers = {"Authorization": f"Bearer {api_token}"}
    log.info(f"Fetching details for device ID '{device_id}'...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        device_data = response.json()
        if device_data:
            return process_device(device_data)
        else:
            log.warning(f"Device with ID '{device_id}' not found or data is empty.")
            print(f"Device with ID '{device_id}' not found or data is empty.")
            return None
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching details for device ID '{device_id}': {e}")
        print(f"Error fetching details for device ID '{device_id}': {e}")
        return None

def get_ssids_for_multiple_devices(base_url: str, api_token: str, device_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Ruft SSID-Informationen für mehrere Geräte über den /devices/radio-information Endpunkt ab."""
    ssids_by_device = {}
    if not device_ids:
        return ssids_by_device
    # Teile die Geräte-IDs in Batches von maximal 10 (basierend auf limit=10)
    batch_size = 10
    for i in range(0, len(device_ids), batch_size):
        batch_ids = device_ids[i:i + batch_size]
        device_ids_str = ",".join(str(id) for id in batch_ids)
        url = f"{base_url}/devices/radio-information?page=1&limit=10&deviceIds={device_ids_str}&includeDisabledRadio=false"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        try:
            log.info(f"Fetching SSID information for devices {device_ids_str} from URL: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get('data', [])
            log.debug(f"Raw SSID response for devices {device_ids_str}: {json.dumps(data[:1], indent=4)}")
            for device_data in data:
                device_id = str(device_data.get('device_id'))
                ssids = []
                seen_ssids = set()  # Für die Entfernung von Duplikaten
                for radio in device_data.get('radios', []):
                    for wlan in radio.get('wlans', []):
                        ssid_name = wlan.get('ssid', '')
                        if ssid_name and ssid_name not in seen_ssids:
                            ssids.append({
                                'ssid': ssid_name,
                                'ssid_status': wlan.get('ssid_status', ''),
                                'ssid_security_type': wlan.get('ssid_security_type', ''),
                                'bssid': wlan.get('bssid', ''),
                                'network_policy_name': wlan.get('network_policy_name', '')
                            })
                            seen_ssids.add(ssid_name)
                ssids_by_device[device_id] = ssids
            time.sleep(1)  # Kurze Pause zwischen Batches, um API-Rate-Limits zu vermeiden
        except requests.exceptions.RequestException as e:
            log.error(f"Fehler beim Abrufen der SSIDs für Geräte {device_ids_str}: {e}")
        except Exception as e:
            log.error(f"Unerwarteter Fehler beim Abrufen der SSIDs für Geräte {device_ids_str}: {e}")
    return ssids_by_device

def store_ap_data_in_redis(ap_list: List[Dict[str, Any]], api_token: str):
    """Speichert AP-Daten als Redis-Hash in DB 3 mit id als Schlüssel."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_AP_DB, decode_responses=True)
        # Sammle alle Geräte-IDs
        device_ids = [str(ap.get('id', '')) for ap in ap_list if ap.get('id')]
        if not device_ids:
            log.warning("Keine Geräte-IDs gefunden. Keine Daten werden in Redis gespeichert.")
            return
        # Hole SSID-Daten für alle Geräte in Batches
        ssids_by_device = get_ssids_for_multiple_devices(XIQ_BASE_URL, api_token, device_ids)
        # Speichere die kombinierten Daten in Redis
        for ap in ap_list:
            device_id = str(ap.get("id", ""))
            if not device_id:
                log.warning(f"AP ohne ID übersprungen: {ap.get('hostname')}")
                continue
            key = f"ap:{device_id}"  # Verwende id als Schlüssel
            ap_data = {
                'hostname': ap.get('hostname', 'N/A'),
                'ip_address': ap.get('ip_address', 'N/A'),
                'serial_number': ap.get('serial_number', 'N/A'),
                'bssid_mac': ap.get('mac_address', 'N/A'),
                'locations': json.dumps(ap.get('locations', [])),
                'ssids': json.dumps(ssids_by_device.get(device_id, []))
            }
            r.hset(key, mapping=ap_data)
            log.info(f"AP '{ap_data['hostname']}' in Redis (db={REDIS_AP_DB}) gespeichert: {key}")
            log.debug(f"Stored locations for {key}: {ap_data['locations']}")
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_AP_DB}): {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Speichern von APs in Redis: {e}")

def export_redis_to_file(csv_file: Optional[str] = None, json_file: Optional[str] = None):
    """Exportiert alle AP-Daten aus Redis DB 3 in CSV- und/oder JSON-Dateien."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_AP_DB, decode_responses=True)
        ap_data_list = []
        for key in r.scan_iter("ap:*"):
            ap_data = r.hgetall(key)
            if ap_data:
                ap_data['ssids'] = json.loads(ap_data.get('ssids', '[]'))
                # Kompatibilität mit älteren Daten (location statt locations)
                if 'locations' in ap_data:
                    ap_data['locations'] = json.loads(ap_data.get('locations', '[]'))
                elif 'location' in ap_data:
                    ap_data['locations'] = [{'name': ap_data.get('location', 'N/A')}] if ap_data.get('location') else []
                ap_data['id'] = key.split(":")[1]  # Extrahiere ID aus dem Schlüssel (ap:<id>)
                ap_data_list.append(ap_data)

        if not ap_data_list:
            log.warning("Keine AP-Daten in Redis DB 3 gefunden.")
            print("Keine AP-Daten in Redis DB 3 gefunden.")
            return

        # Export nach CSV
        if csv_file:
            try:
                with open(csv_file, 'w', newline='') as f:
                    fieldnames = ['id', 'hostname', 'ip_address', 'serial_number', 'bssid_mac', 'site', 'region', 'country', 'city', 'location', 'floor', 'ssids']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for ap in ap_data_list:
                        locations = ap.get('locations', [])
                        # Zuordnung der Location-Ebenen basierend auf der Hierarchie
                        site = locations[0].get('name', '') if len(locations) > 0 else ''
                        region = locations[1].get('name', '') if len(locations) > 1 else ''
                        country = locations[2].get('name', '') if len(locations) > 2 else ''
                        city = locations[3].get('name', '') if len(locations) > 3 else ''
                        location = locations[4].get('name', '') if len(locations) > 4 else ''
                        floor = locations[5].get('name', '') if len(locations) > 5 else ''
                        writer.writerow({
                            'id': ap.get('id', 'N/A'),
                            'hostname': ap.get('hostname', 'N/A'),
                            'ip_address': ap.get('ip_address', 'N/A'),
                            'serial_number': ap.get('serial_number', 'N/A'),
                            'bssid_mac': ap.get('bssid_mac', 'N/A'),
                            'site': site,
                            'region': region,
                            'country': country,
                            'city': city,
                            'location': location,
                            'floor': floor,
                            'ssids': ','.join([ssid.get('ssid', '') for ssid in ap.get('ssids', [])])
                        })
                log.info(f"AP-Daten erfolgreich in CSV-Datei '{csv_file}' exportiert.")
                print(f"AP-Daten erfolgreich in CSV-Datei '{csv_file}' exportiert.")
            except IOError as e:
                log.error(f"Fehler beim Exportieren der AP-Daten in CSV-Datei '{csv_file}': {e}")
                print(f"Fehler beim Exportieren der AP-Daten in CSV-Datei '{csv_file}': {e}")

        # Export nach JSON
        if json_file:
            try:
                with open(json_file, 'w') as f:
                    json.dump(ap_data_list, f, indent=4)
                log.info(f"AP-Daten erfolgreich in JSON-Datei '{json_file}' exportiert.")
                print(f"AP-Daten erfolgreich in JSON-Datei '{json_file}' exportiert.")
            except IOError as e:
                log.error(f"Fehler beim Exportieren der AP-Daten in JSON-Datei '{json_file}': {e}")
                print(f"Fehler beim Exportieren der AP-Daten in JSON-Datei '{json_file}': {e}")

    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_AP_DB}): {e}")
        print(f"Fehler bei der Verbindung zu Redis (db={REDIS_AP_DB}): {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Exportieren der AP-Daten: {e}")
        print(f"Unerwarteter Fehler beim Exportieren der AP-Daten: {e}")

def get_device_from_redis_by_hostname(hostname: str) -> Optional[Dict[str, Any]]:
    """Ruft AP-Informationen aus Redis anhand des Hostnamens ab."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_AP_DB, decode_responses=True)
        for key in r.scan_iter("ap:*"):
            ap_data = r.hgetall(key)
            if ap_data.get('hostname') == hostname:
                ap_data['ssids'] = json.loads(ap_data.get('ssids', '[]'))
                # Kompatibilität mit älteren Daten
                if 'locations' in ap_data:
                    ap_data['locations'] = json.loads(ap_data.get('locations', '[]'))
                elif 'location' in ap_data:
                    ap_data['locations'] = [{'name': ap_data.get('location', 'N/A')}] if ap_data.get('location') else []
                ap_data['id'] = key.split(":")[1]  # Extrahiere ID aus dem Schlüssel
                return ap_data
        return None
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_AP_DB}): {e}")
        return None
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Abrufen von '{hostname}' aus Redis: {e}")
        return None

def find_hosts(
    managed_by: Optional[str] = None,
    location_part: Optional[str] = None,
    hostname_filter: Optional[str] = None,
    device_function: Optional[str] = None,
    exact_match: bool = False,
    verbose: bool = False
) -> List[Dict[str, Any]]:
    """Sucht APs in Redis basierend auf optionalen Kriterien."""
    if verbose:
        print(f"Redis Host: {REDIS_HOST}, Port: {REDIS_PORT}, DB: {REDIS_AP_DB}")
    matching_devices = []
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_AP_DB, decode_responses=True)
        for key in r.scan_iter("ap:*"):
            if verbose:
                print(f"Gefundener Schlüssel: {key}")
            device = r.hgetall(key)
            if not device:
                continue
            device['ssids'] = json.loads(device.get('ssids', '[]'))
            # Kompatibilität mit älteren Daten
            if 'locations' in device:
                device['locations'] = json.loads(device.get('locations', '[]'))
            elif 'location' in device:
                device['locations'] = [{'name': device.get('location', 'N/A')}] if device.get('location') else []
            device['id'] = key.split(":")[1]  # Extrahiere ID aus dem Schlüssel
            match = True
            if managed_by and managed_by.lower() not in device.get('managed_by', '').lower():
                match = False
            if hostname_filter and hostname_filter.lower() not in device.get('hostname', '').lower():
                match = False
            if location_part:
                # Suche in allen Location-Namen
                location_match = any(
                    location_part.lower() in loc.get('name', '').lower()
                    for loc in device.get('locations', [])
                )
                if not location_match:
                    match = False
            if device_function and device_function.lower() != 'ap':
                match = False
            if match:
                matching_devices.append(device)
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_AP_DB}): {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler bei der Suche in Redis: {e}")
    return matching_devices

def get_device_status_summary(location_id):
    """Ruft die Gerätestatusübersicht für eine Location-ID ab."""
    headers = {"Authorization": f"Bearer {API_SECRET}"}
    try:
        response = requests.get(f"{XIQ_BASE_URL}/locations/{location_id}/device_status_summary", headers=headers)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=4))
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving device status summary for location ID {location_id}: {e}")
        print(f"Error retrieving device status summary for location ID {location_id}: {e}")

def get_locations_tree():
    """Ruft den Location Tree ab und speichert ihn in Redis (db=1)."""
    headers = {"Authorization": f"Bearer {API_SECRET}"}
    url = f"{XIQ_BASE_URL}/locations/tree"
    try:
        log.info(f"Rufe Location Tree ab: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        locations_tree = response.json()
        print(json.dumps(locations_tree, indent=4))
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOCATIONS_DB, decode_responses=True)
        r.set("xiq:locations:tree", json.dumps(locations_tree))
        log.info("Location Tree erfolgreich in Redis (db=1) gespeichert.")
    except requests.exceptions.RequestException as e:
        log.error(f"Fehler beim Abrufen des Location Tree: {e}")
        print(f"Fehler beim Abrufen des Location Tree: {e}")

def get_location_info_by_name(search_name: str) -> Optional[Dict[str, Any]]:
    """Sucht nach einer Location im Location Tree (Redis db=1)."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOCATIONS_DB, decode_responses=True)
        locations_tree_json = r.get("xiq:locations:tree")
        if locations_tree_json:
            locations_tree = json.loads(locations_tree_json)
            def find_location(tree, name):
                if isinstance(tree, dict) and tree.get("uniqueName") == name:
                    return {"unique_name": tree.get("uniqueName"), "id": tree.get("id")}
                elif isinstance(tree, list):
                    for item in tree:
                        result = find_location(item, name)
                        if result:
                            return result
                elif isinstance(tree, dict) and "children" in tree:
                    result = find_location(tree["children"], name)
                    if result:
                        return result
                return None
            return find_location(locations_tree, search_name)
        else:
            log.warning("Location Tree nicht in Redis (db=1) gefunden.")
            print("Location Tree nicht in Redis (db=1) gefunden.")
            return None
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db=1): {e}")
        return None

def process_device(raw_device: Dict[str, Any]) -> Dict[str, Any]:
    """Verarbeitet ein rohes Geräteobjekt, formatiert MAC und berechnet Uptime."""
    device = raw_device.copy()
    mac = device.get("macAddress")
    if mac:
        device["mac_address"] = ":".join(mac[i:i + 2] for i in range(0, len(mac), 2)).lower()
        del device["macAddress"]
    uptime_seconds = device.get("uptime")
    if uptime_seconds is not None:
        device["uptime_readable"] = calculate_uptime(uptime_seconds)
    device["serial_number"] = device.get("serialNumber", "")
    return device

def calculate_uptime(seconds: int) -> str:
    """Berechnet eine lesbare Uptime-Zeichenkette aus Sekunden."""
    try:
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} Tage")
        if hours > 0:
            uptime_parts.append(f"{hours} Stunden")
        if minutes > 0:
            uptime_parts.append(f"{minutes} Minuten")
        if secs > 0 and days == 0 and hours == 0:
            uptime_parts.append(f"{secs} Sekunden")
        return ", ".join(uptime_parts) or "Weniger als eine Sekunde"
    except OverflowError:
        log.error(f"OverflowError bei der Berechnung der Uptime für {seconds} Sekunden.")
        return "Uptime-Berechnungsfehler (Overflow)"
    except TypeError:
        log.error(f"TypeError bei der Berechnung der Uptime für {seconds}.")
        return "Uptime-Berechnungsfehler (Typ)"

def convert_list_to_csv(data: List[Dict[str, Any]], output_file: str):
    """Konvertiert eine Liste von Geräte-Dictionaries in eine CSV-Datei."""
    if not data:
        log.warning("Keine Daten zum Schreiben in die CSV-Datei.")
        print("Keine Daten zum Schreiben in die CSV-Datei.")
        return
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ["id", "hostname", "mac_address", "ip_address", "model", "serialNumber", "uptime_readable", "managed", "site", "region", "country", "city", "location", "floor", "lldp_remote_chassis_id", "lldp_remote_port_id", "cdp_neighbor", "cdp_neighbor_port"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                locations = item.get("locations", [])
                site = locations[0].get("name") if locations and len(locations) > 0 else ""
                region = locations[1].get("name") if locations and len(locations) > 1 else ""
                country = locations[2].get("name") if locations and len(locations) > 2 else ""
                city = locations[3].get("name") if locations and len(locations) > 3 else ""
                location = locations[4].get("name") if locations and len(locations) > 4 else ""
                floor = locations[5].get("name") if locations and len(locations) > 5 else ""
                lldp_cdp_info = item.get("lldp_cdp_infos", [])
                lldp_remote_chassis_id = lldp_cdp_info[0].get("remoteChassisId") if lldp_cdp_info and len(lldp_cdp_info) > 0 else ""
                lldp_remote_port_id = lldp_cdp_info[0].get("remotePortId") if lldp_cdp_info and len(lldp_cdp_info) > 0 else ""
                cdp_neighbor = lldp_cdp_info[0].get("neighborDeviceId") if lldp_cdp_info and len(lldp_cdp_info) > 0 and lldp_cdp_info[0].get("protocol") == "CDP" else ""
                cdp_neighbor_port = lldp_cdp_info[0].get("neighborPortId") if lldp_cdp_info and len(lldp_cdp_info) > 0 and lldp_cdp_info[0].get("protocol") == "CDP" else ""
                writer.writerow({
                    "id": item.get("id"),
                    "hostname": item.get("hostname"),
                    "mac_address": item.get("mac_address"),
                    "ip_address": item.get("ip_address"),
                    "model": item.get("model"),
                    "serialNumber": item.get("serial_number"),
                    "uptime_readable": item.get("uptime_readable"),
                    "managed": item.get("managed"),
                    "site": site,
                    "region": region,
                    "country": country,
                    "city": city,
                    "location": location,
                    "floor": floor,
                    "lldp_remote_chassis_id": lldp_remote_chassis_id,
                    "lldp_remote_port_id": lldp_remote_port_id,
                    "cdp_neighbor": cdp_neighbor,
                    "cdp_neighbor_port": cdp_neighbor_port,
                })
        log.info(f"Geräteliste erfolgreich in '{output_file}' als CSV gespeichert.")
    except IOError as e:
        log.error(f"Fehler beim Schreiben der Geräteliste in '{output_file}' als CSV: {e}")
        print(f"Fehler beim Schreiben der Geräteliste in '{output_file}' als CSV: {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler bei der CSV-Konvertierung: {e}")
        print(f"Unerwarteter Fehler bei der CSV-Konvertierung: {e}")

def handle_get_devicelist(args, api_token):
    """Ruft AP-Daten und speichert sie in Redis DB 3."""
    device_list = get_device_list_paginated(args.server, api_token)
    if device_list:
        if args.show_pretty:
            print("AP-Informationen:")
            for device in device_list:
                print(f"  ID: {device.get('id')}")
                print(f"  Hostname: {device.get('hostname')}")
                print(f"  MAC-Adresse: {device.get('mac_address')}")
                print(f"  IP-Adresse: {device.get('ip_address')}")
                print(f"  Seriennummer: {device.get('serial_number')}")
                locations = device.get('locations', [])
                print(f"  Locations:")
                for loc in locations:
                    print(f"    - {loc.get('name', 'N/A')} (ID: {loc.get('id', 'N/A')})")
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
            store_ap_data_in_redis(device_list, api_token)
        if args.output_csv_file:
            convert_list_to_csv(device_list, args.output_csv_file)
    else:
        log.error("Fehler beim Abrufen der AP-Liste.")
        sys.exit(1)

def handle_get_device_by_id(args, api_token):
    """Ruft Details für ein Gerät mit der angegebenen ID ab."""
    device_data = get_device_by_id(args.server, api_token, args.device_id)
    if device_data:
        print(json.dumps(device_data, indent=4))
    else:
        log.error(f"Fehler beim Abrufen der Details für Gerät mit ID '{args.device_id}'.")
        sys.exit(1)

def handle_get_device_by_hostname(args):
    """Ruft AP-Details aus Redis basierend auf Hostname ab."""
    device = get_device_from_redis_by_hostname(args.hostname)
    if device:
        print(json.dumps(device, indent=4))
    else:
        log.warning(f"Keine AP-Informationen für Hostname '{args.hostname}' in Redis gefunden.")
        print(f"Keine AP-Informationen für Hostname '{args.hostname}' in Redis gefunden.")

def handle_find_hosts(args, verbose):
    """Sucht APs in Redis basierend auf Filtern."""
    matching_devices = find_hosts(
        args.managed_by_value,
        args.location_name_part,
        args.hostname_value,
        args.device_function,
        args.exact_match,
        verbose
    )
    if matching_devices:
        print("Gefundene Access Points:")
        for device in matching_devices:
            print(f"  Hostname: {device.get('hostname')}")
            print(f"  IP-Adresse: {device.get('ip_address')}")
            print(f"  Seriennummer: {device.get('serial_number')}")
            print(f"  BSSID-MAC: {device.get('bssid_mac')}")
            print(f"  Locations:")
            for loc in device.get('locations', []):
                print(f"    - {loc.get('name', 'N/A')} (ID: {loc.get('id', 'N/A')})")
            print(f"  SSIDs: {', '.join([ssid['ssid'] for ssid in device.get('ssids', [])])}")
            print("-" * 20)
    else:
        print("Keine APs gefunden, die den Kriterien entsprechen.")

def handle_get_device_status(args, api_token):
    """Ruft Gerätestatus für eine Location-ID ab."""
    if api_token:
        get_device_status_summary(args.location_id)
    else:
        log.error("Kein API-Token vorhanden.")
        sys.exit(1)

def handle_get_locations_tree(api_token):
    """Ruft den Location Tree ab."""
    if api_token:
        get_locations_tree()
    else:
        log.error("Kein API-Token vorhanden.")
        sys.exit(1)

def handle_find_location(args):
    """Sucht nach einer Location im Location Tree."""
    location = get_location_info_by_name(args.search_location)
    if location:
        print(f"Unique Name: {location.get('unique_name')}")
        print(f"ID: {location.get('id')}")
    else:
        print(f"Keine Location mit dem Suchbegriff '{args.search_location}' gefunden.")

def handle_get_device_details_by_hostname(args, api_token):
    """Ruft AP-Details von der API basierend auf Hostname aus Redis."""
    device = get_device_from_redis_by_hostname(args.hostname_details)
    if device:
        device_id = device.get('id')
        if device_id:
            device_details = get_device_by_id(args.server, api_token, device_id)
            if device_details:
                print(json.dumps(device_details, indent=4))
            else:
                print(f"Fehler beim Abrufen der Details für Gerät mit ID '{device_id}'.")
        else:
            print(f"Keine ID für Hostname '{args.hostname_details}' gefunden.")
    else:
        print(f"Keine AP-Informationen für Hostname '{args.hostname_details}' in Redis gefunden.")

def handle_export_redis(args):
    """Exportiert AP-Daten aus Redis DB 3 in CSV- und/oder JSON-Dateien."""
    export_redis_to_file(args.export_db_csv, args.export_db_json)

def main():
    parser = ArgumentParser(description="Interagiert mit der ExtremeCloud IQ API für AP-Daten.")
    auth_group = parser.add_argument_group('Authentifizierung')
    auth_group.add_argument("-k", "--api_key_file", default="xiq_api_token.txt", help="Pfad zur API-Token-Datei.")
    auth_group.add_argument("-u", "--username", help="Benutzername für die XIQ API.")
    auth_group.add_argument("-p", "--password", help="Passwort für die XIQ API.")
    auth_group.add_argument("--create-env", action="store_true", help="Erstellt .env-Datei mit Benutzername und Passwort.")

    api_group = parser.add_argument_group('API-Abruf')
    api_group.add_argument("-s", "--server", default=XIQ_BASE_URL, help="Basis-URL der XIQ API.")
    api_group.add_argument("--get-aps", action="store_true", help="Ruft die Liste der Access Points und speichert in Redis (db=3).")
    api_group.add_argument("--get-device-by-id", dest="device_id", help="Ruft Details für ein Gerät mit der angegebenen ID ab.")
    api_group.add_argument("--get-device-details-by-hostname", dest="hostname_details", help="Ruft Details für ein Gerät mit dem Hostnamen ab.")
    api_group.add_argument("--get-device-status", dest="location_id", help="Ruft Gerätestatusübersicht für eine Location-ID ab.")
    api_group.add_argument("--get-locations-tree", action="store_true", help="Ruft den Location Tree ab.")
    api_group.add_argument("--find-location", dest="search_location", help="Sucht nach einer Location im Location Tree.")

    redis_group = parser.add_argument_group('Redis-Interaktion')
    redis_group.add_argument("--get-device-by-hostname", dest="hostname", help="Ruft AP-Details aus Redis basierend auf Hostname.")
    redis_group.add_argument("-f", "--find-hosts", action="store_true", help="Sucht APs in Redis mit Filtern.")
    redis_group.add_argument("-m", "--managed_by", dest="managed_by_value", help="Filter für 'managed_by'.")
    redis_group.add_argument("-l", "--location-part", dest="location_name_part", help="Filter für Location-Namen.")
    redis_group.add_argument("--hostname-filter", dest="hostname_value", help="Filter für Hostname.")
    redis_group.add_argument("--device-function", dest="device_function", help="Filter für Gerätefunktion (z.B. AP).")
    redis_group.add_argument("--exact-match", action="store_true", help="Exakte Übereinstimmung für Filter.")
    redis_group.add_argument("--export-db-csv", help="Exportiert AP-Daten aus Redis DB 3 in eine CSV-Datei.")
    redis_group.add_argument("--export-db-json", help="Exportiert AP-Daten aus Redis DB 3 in eine JSON-Datei.")

    output_group = parser.add_argument_group('Ausgabe')
    output_group.add_argument("-o", "--output-file", default="XiqDeviceList.json", help="Dateiname für JSON-Ausgabe.")
    output_group.add_argument("--show-pretty", action="store_true", help="Vereinfachte Ausgabe der APs.")
    output_group.add_argument("--output-csv", dest="output_csv_file", help="Dateiname für CSV-Ausgabe.")
    output_group.add_argument("--store-redis", action="store_true", help="Speichert AP-Daten in Redis (db=3).")

    misc_group = parser.add_argument_group('Sonstige')
    misc_group.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe aktivieren.")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug(f"Verbose-Modus aktiviert. XIQ_BASE_URL={args.server}")

    if args.create_env and args.username and args.password:
        save_credentials_to_env(args.username, args.password)
        sys.exit(0)
    elif args.create_env:
        parser.error("--create-env erfordert -u und -p.")

    api_token = get_api_token(args)
    if not api_token and any([args.get_aps, args.device_id, args.hostname_details, args.location_id, args.get_locations_tree]):
        log.error("Ungültiger API-Token. Skript wird beendet.")
        sys.exit(1)

    action_map = {
        args.get_aps: lambda: handle_get_devicelist(args, api_token),
        args.device_id: lambda: handle_get_device_by_id(args, api_token),
        args.hostname: lambda: handle_get_device_by_hostname(args),
        args.find_hosts: lambda: handle_find_hosts(args, args.verbose),
        args.location_id: lambda: handle_get_device_status(args, api_token),
        args.get_locations_tree: lambda: handle_get_locations_tree(api_token),
        args.search_location: lambda: handle_find_location(args),
        args.hostname_details: lambda: handle_get_device_details_by_hostname(args, api_token),
        bool(args.export_db_csv or args.export_db_json): lambda: handle_export_redis(args),
    }

    executed = False
    for condition, action in action_map.items():
        if condition:
            action()
            executed = True
            break

    if not executed:
        parser.print_help()

if __name__ == "__main__":
    main()
