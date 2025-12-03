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
REDIS_DEVICE_DB = int(os.getenv("REDIS_DEVICE_DB", 0))
REDIS_LOCATIONS_DB = int(os.getenv("REDIS_LOCATIONS_DB", 1))
PAGE_SIZE = int(os.getenv("PAGE_SIZE", 100))
API_SECRET = None  # Global für den API-Token

log = logging.getLogger(__name__)

# --- Neue Funktion: API-Request mit Rate-Limit-Handling ---
def api_get_with_rate_limit(url: str, headers: dict, params: dict = None, max_retries: int = 3) -> Optional[requests.Response]:
    """
    Führt einen GET-Request mit automatischem Rate-Limit-Handling (429) aus.
    Gibt Response zurück oder None bei endgültigem Fehler.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                log.warning(f"429 Too Many Requests – Warte {retry_after}s (Versuch {attempt + 1}/{max_retries})")
                time.sleep(retry_after + 1)
                continue
            response.raise_for_status()
            # Logge Rate-Limits
            limit = response.headers.get("RateLimit-Limit")
            remaining = response.headers.get("RateLimit-Remaining")
            reset = response.headers.get("RateLimit-Reset")
            if limit and remaining:
                log.debug(f"Rate-Limit: {remaining}/{limit}, Reset in {reset}s")
            return response
        except requests.exceptions.RequestException as e:
            log.error(f"API-Fehler bei {url} (Versuch {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

# --- Neue Funktion: Rate-Limits manuell abfragen ---
def check_rate_limits(base_url: str, api_token: str) -> Optional[Dict[str, Any]]:
    """Fragt aktuelle Rate-Limits über /devices ab."""
    url = f"{base_url}/devices"
    headers = {"Authorization": f"Bearer {api_token}"}
    params = {"page": 1, "limit": 1}
    log.info("Prüfe API-Rate-Limits...")
    response = api_get_with_rate_limit(url, headers, params)
    if not response:
        return None
    limit = response.headers.get("RateLimit-Limit")
    remaining = response.headers.get("RateLimit-Remaining")
    reset = response.headers.get("RateLimit-Reset")
    result = {
        "limit": limit,
        "remaining": remaining,
        "reset_in_seconds": reset
    }
    log.info(f"Rate-Limits: {remaining}/{limit}, Reset in {reset}s")
    print(json.dumps(result, indent=2))
    return result

# --- Angepasste get_device_list_paginated mit Rate-Limit ---
def get_device_list_paginated(base_url: str, api_token: str) -> Optional[List[Dict[str, Any]]]:
    page = 1
    all_devices = []
    headers = {"Authorization": f"Bearer {api_token}"}

    while True:
        url = f"{base_url}/devices"
        params = {"page": page, "limit": PAGE_SIZE, "views": "BASIC"}
        log.info(f"Rufe Geräte Seite {page} ab...")
        response = api_get_with_rate_limit(url, headers, params)
        if not response:
            return None
        data = response.json().get('data', [])
        if not data:
            log.info("Keine weiteren Geräte gefunden.")
            break
        for raw_device in data:
            device = process_device(raw_device)
            all_devices.append(device)
        if len(data) < PAGE_SIZE:
            break
        page += 1
        time.sleep(1)
    log.info(f"Erfolgreich {len(all_devices)} Geräte abgerufen.")
    return all_devices

# --- Angepasste get_device_by_id mit Rate-Limit ---
def get_device_by_id(base_url: str, api_token: str, device_id: str) -> Optional[Dict[str, Any]]:
    url = f"{base_url}/devices/{device_id}"
    params = {"views": "FULL"}
    headers = {"Authorization": f"Bearer {api_token}"}
    log.info(f"Rufe Details für Gerät ID '{device_id}' ab...")
    response = api_get_with_rate_limit(url, headers, params)
    if not response:
        return None
    device_data = response.json()
    return process_device(device_data) if device_data else None

# --- Angepasste get_locations_tree mit Rate-Limit ---
def get_locations_tree():
    global API_SECRET
    url = f"{XIQ_BASE_URL}/locations/tree"
    headers = {"Authorization": f"Bearer {API_SECRET}"}
    log.info("Rufe Location Tree ab...")
    response = api_get_with_rate_limit(url, headers)
    if not response:
        return
    locations_tree = response.json()
    print(json.dumps(locations_tree, indent=4))
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOCATIONS_DB, decode_responses=True)
        r.set("xiq:locations:tree", json.dumps(locations_tree))
        log.info("Location Tree in Redis (db=1) gespeichert.")
    except Exception as e:
        log.error(f"Fehler beim Speichern in Redis: {e}")

# --- Neue Handler-Funktion für --check-rate-limits ---
def handle_check_rate_limits(args, api_token):
    if not api_token:
        log.error("Kein API-Token vorhanden.")
        sys.exit(1)
    check_rate_limits(args.serverRoot, api_token)

# --- Rest des Skripts (unverändert, außer api_get_with_rate_limit) ---
def load_api_token(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'r') as f:
            token = f.readline().strip()
            if token:
                global API_SECRET
                API_SECRET = token
                log.info(f"API-Token aus '{file_path}' geladen.")
                return token
    except FileNotFoundError:
        log.warning(f"Token-Datei '{file_path}' nicht gefunden.")
    except Exception as e:
        log.error(f"Fehler beim Lesen der Token-Datei: {e}")
    return None

def save_api_token(token: str, file_path: str):
    try:
        with open(file_path, 'w') as f:
            f.write(token)
        log.info(f"API-Token in '{file_path}' gespeichert.")
    except Exception as e:
        log.error(f"Fehler beim Speichern des Tokens: {e}")

def load_credentials_from_env() -> Optional[tuple[str, str]]:
    username = os.getenv("XIQ_USERNAME")
    password = os.getenv("XIQ_PASSWORD")
    if username and password:
        log.info("Anmeldedaten aus .env geladen.")
        return username, password
    return None

def save_credentials_to_env(username: str, password: str):
    try:
        with open(".env", "w") as f:
            f.write(f"XIQ_USERNAME={username}\nXIQ_PASSWORD={password}\n")
        log.info("Anmeldedaten in .env gespeichert.")
    except Exception as e:
        log.error(f"Fehler beim Schreiben der .env: {e}")

def get_xiq_api_token(base_url: str, username: str, password: str) -> Optional[str]:
    global API_SECRET
    url = f"{base_url}/login"
    try:
        response = requests.post(url, json={"username": username, "password": password}, timeout=30)
        response.raise_for_status()
        token = response.json().get("access_token")
        if token:
            API_SECRET = token
            log.info("Login erfolgreich – Token abgerufen.")
            return token
    except Exception as e:
        log.error(f"Login fehlgeschlagen: {e}")
    return None

def get_device_from_redis_by_hostname(hostname: str) -> Optional[Dict[str, Any]]:
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
        device_json = r.get(f"xiq:device:{hostname}")
        return json.loads(device_json) if device_json else None
    except Exception as e:
        log.error(f"Redis-Fehler: {e}")
        return None

def store_devices_in_redis(device_list: List[Dict[str, Any]]):
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
        for device in device_list:
            hostname = device.get("hostname")
            if hostname:
                r.set(f"xiq:device:{hostname}", json.dumps(device))
                log.debug(f"Gerät '{hostname}' in Redis gespeichert.")
    except Exception as e:
        log.error(f"Fehler beim Speichern in Redis: {e}")

def find_hosts(
    managed_by: Optional[str] = None,
    location_part: Optional[str] = None,
    hostname_filter: Optional[str] = None,
    device_function: Optional[str] = None,
    exact_match: bool = False,
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    matching_devices = []
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
        for key in r.scan_iter("xiq:device:*"):
            if key.startswith("xiq:device:id:"): continue
            device_json = r.get(key)
            if not device_json: continue
            device = json.loads(device_json)
            match = True
            if managed_by and managed_by.lower() not in device.get("managed_by", "").lower():
                match = False
            if hostname_filter and hostname_filter.lower() not in device.get("hostname", "").lower():
                match = False
            if location_part:
                if not any(location_part.lower() in loc.get("name", "").lower() for loc in device.get("locations", [])):
                    match = False
            if device_function and device.get("device_function", "").lower() != device_function.lower():
                match = False
            if match:
                matching_devices.append(device)
    except Exception as e:
        log.error(f"Redis-Suchfehler: {e}")
    return matching_devices

def get_device_status_summary(location_id):
    global API_SECRET
    url = f"{XIQ_BASE_URL}/locations/{location_id}/device_status_summary"
    headers = {"Authorization": f"Bearer {API_SECRET}"}
    response = api_get_with_rate_limit(url, headers)
    if response:
        print(json.dumps(response.json(), indent=4))

def get_location_info_by_name(search_name: str) -> Optional[Dict[str, Any]]:
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOCATIONS_DB, decode_responses=True)
        tree_json = r.get("xiq:locations:tree")
        if not tree_json: return None
        tree = json.loads(tree_json)
        def find(node):
            if isinstance(node, dict):
                if node.get("uniqueName") == search_name:
                    return {"unique_name": node.get("uniqueName"), "id": node.get("id")}
                if "children" in node:
                    return find(node["children"])
            elif isinstance(node, list):
                for item in node:
                    result = find(item)
                    if result: return result
            return None
        return find(tree)
    except Exception as e:
        log.error(f"Location-Suche fehlgeschlagen: {e}")
        return None

def process_device(raw_device: Dict[str, Any]) -> Dict[str, Any]:
    device = raw_device.copy()
    mac = device.get("macAddress")
    if mac:
        device["mac_address"] = ":".join(mac[i:i + 2] for i in range(0, len(mac), 2)).lower()
        del device["macAddress"]
    uptime = device.get("uptime")
    if uptime is not None:
        device["uptime_readable"] = calculate_uptime(uptime)
    return device

def calculate_uptime(seconds: int) -> str:
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days: parts.append(f"{days} Tage")
    if hours: parts.append(f"{hours} Stunden")
    if mins: parts.append(f"{mins} Minuten")
    if secs and not days and not hours: parts.append(f"{secs} Sekunden")
    return ", ".join(parts) or "Weniger als eine Sekunde"

def convert_list_to_csv(data: List[Dict[str, Any]], output_file: str):
    if not data: return
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "hostname", "mac_address", "ip_address", "model", "serialNumber", "uptime_readable", "managed", "site", "building", "floor"])
            writer.writeheader()
            for item in data:
                locs = item.get("locations", [])
                writer.writerow({
                    "id": item.get("id"),
                    "hostname": item.get("hostname"),
                    "mac_address": item.get("mac_address"),
                    "ip_address": item.get("ip_address"),
                    "model": item.get("model"),
                    "serialNumber": item.get("serialNumber"),
                    "uptime_readable": item.get("uptime_readable"),
                    "managed": item.get("managed"),
                    "site": locs[0].get("name") if len(locs) > 0 else "",
                    "building": locs[1].get("name") if len(locs) > 1 else "",
                    "floor": locs[2].get("name") if len(locs) > 2 else "",
                })
        log.info(f"CSV exportiert: {output_file}")
    except Exception as e:
        log.error(f"CSV-Fehler: {e}")

def get_api_token(args):
    creds = load_credentials_from_env()
    if creds:
        args.username, args.password = creds
    if args.username and args.password:
        token = get_xiq_api_token(args.serverRoot, args.username, args.password)
        if token:
            save_api_token(token, args.api_key_file)
        return token
    return load_api_token(args.api_key_file)

def handle_get_devicelist(args, api_token):
    devices = get_device_list_paginated(args.serverRoot, api_token)
    if not devices:
        sys.exit(1)
    if args.show_pretty:
        for d in devices:
            print(f"ID: {d.get('id')} | {d.get('hostname')} | {d.get('mac_address')} | {d.get('ip_address')}")
    else:
        print(json.dumps(devices, indent=4))
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(devices, f, indent=4)
    if args.store_redis:
        store_devices_in_redis(devices)
    if args.output_csv_file:
        convert_list_to_csv(devices, args.output_csv_file)

def handle_get_device_by_id(args, api_token):
    data = get_device_by_id(args.serverRoot, api_token, args.device_id)
    if data:
        print(json.dumps(data, indent=4) if not args.pretty_print else pretty_print_device(data))

def handle_get_device_by_hostname(args):
    data = get_device_from_redis_by_hostname(args.hostname)
    if data:
        print(json.dumps(data, indent=4))

def handle_find_hosts(args, verbose):
    devices = find_hosts(args.managed_by_value, args.location_name_part, args.hostname_value, args.device_function, args.exact_match, verbose)
    for d in devices:
        print(f"{d.get('hostname')} | {d.get('ip_address')} | {d.get('device_function')}")

def handle_get_device_status(args, api_token):
    get_device_status_summary(args.location_id)

def handle_get_locations_tree(api_token):
    get_locations_tree()

def handle_find_location(args):
    loc = get_location_info_by_name(args.search_location)
    if loc:
        print(f"Unique Name: {loc['unique_name']}\nID: {loc['id']}")

def handle_get_device_details_by_hostname(args, api_token):
    device_id = get_device_id_by_hostname_from_redis(args.hostname_details)
    if device_id:
        data = get_device_by_id(args.serverRoot, api_token, device_id)
        if data:
            print(json.dumps(data, indent=4) if not args.pretty_print else pretty_print_device(data))

def get_device_id_by_hostname_from_redis(hostname: str) -> Optional[str]:
    devices = find_hosts(hostname_filter=hostname, exact_match=True)
    return str(devices[0].get("id")) if devices else None

def pretty_print_device(device: Dict[str, Any]) -> str:
    locs = ", ".join([l.get("name", "") for l in device.get("locations", [])])
    return f"ID: {device.get('id')}\nHostname: {device.get('hostname')}\nMAC: {device.get('mac_address')}\nIP: {device.get('ip_address')}\nLocations: {locs}"

def main():
    parser = ArgumentParser(description="ExtremeCloud IQ API Tool mit Rate-Limit-Support")
    auth_group = parser.add_argument_group('Auth')
    auth_group.add_argument("-k", "--api_key_file", default="xiq_api_token.txt")
    auth_group.add_argument("-u", "--username")
    auth_group.add_argument("-p", "--password")
    auth_group.add_argument("--create-env", action="store_true")

    api_group = parser.add_argument_group('API')
    api_group.add_argument("-s", "--server", dest="serverRoot", default=XIQ_BASE_URL)
    api_group.add_argument("--get-devicelist", action="store_true")
    api_group.add_argument("--get-device-by-id", dest="device_id")
    api_group.add_argument("--get-device-details-by-hostname", dest="hostname_details")
    api_group.add_argument("--get-device-status", dest="location_id")
    api_group.add_argument("--get-locations-tree", action="store_true")
    api_group.add_argument("--find-location", dest="search_location")
    api_group.add_argument("--check-rate-limits", action="store_true", help="Zeigt aktuelle API-Rate-Limits")

    redis_group = parser.add_argument_group('Redis')
    redis_group.add_argument("--get-device-by-hostname", dest="hostname")
    redis_group.add_argument("-f", "--find-hosts", action="store_true")
    redis_group.add_argument("-m", "--managed_by", dest="managed_by_value")
    redis_group.add_argument("-l", "--location-part", dest="location_name_part")
    redis_group.add_argument("--hostname-filter", dest="hostname_value")
    redis_group.add_argument("--device-function", dest="device_function")
    redis_group.add_argument("--exact-match", action="store_true")
    redis_group.add_argument("--store-redis", action="store_true")

    output_group = parser.add_argument_group('Ausgabe')
    output_group.add_argument("-o", "--output_file", default="XiqDeviceList.json")
    output_group.add_argument("--show-pretty", action="store_true")
    output_group.add_argument("--output-csv", dest="output_csv_file")
    output_group.add_argument("-pp", "--pretty-print", action="store_true")

    misc_group = parser.add_argument_group('Sonstiges')
    misc_group.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if not args.verbose else logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    if args.create_env and args.username and args.password:
        save_credentials_to_env(args.username, args.password)
        sys.exit(0)

    api_token = get_api_token(args)
    if not api_token and any([args.get_devicelist, args.device_id, args.location_id, args.get_locations_tree, args.check_rate_limits]):
        sys.exit(1)

    action_map = {
        args.get_devicelist: lambda: handle_get_devicelist(args, api_token),
        args.device_id: lambda: handle_get_device_by_id(args, api_token),
        args.hostname: lambda: handle_get_device_by_hostname(args),
        args.find_hosts: lambda: handle_find_hosts(args, args.verbose),
        args.location_id: lambda: handle_get_device_status(args, api_token),
        args.get_locations_tree: lambda: handle_get_locations_tree(api_token),
        args.search_location: lambda: handle_find_location(args),
        args.hostname_details: lambda: handle_get_device_details_by_hostname(args, api_token),
        args.check_rate_limits: lambda: handle_check_rate_limits(args, api_token),
    }

    for cond, action in action_map.items():
        if cond:
            action()
            break
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
