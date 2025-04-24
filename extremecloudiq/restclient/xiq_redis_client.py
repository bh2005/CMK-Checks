#!/usr/bin/env python3

from argparse import ArgumentParser
import json
import logging
import os
import sys
import time
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
    """Loggt sich bei der ExtremeCloud IQ API ein und ruft den API-Token ab und setzt die globale API_SECRET."""
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
        elif isinstance(e, requests.exceptions.ConnectionError):
            log.error(f"Verbindungsfehler beim Zugriff auf die API für den Login: {e}")
            print(f"Verbindungsfehler beim Zugriff auf die API für den Login: {e}")
        else:
            log.error(f"Unerwarteter Fehler bei der Login-Anfrage: {e}")
            print(f"Unerwarteter Fehler bei der Login-Anfrage: {e}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Fehler beim Decodieren der JSON-Antwort beim Login: {e}")
        print(f"Fehler beim Decodieren der JSON-Antwort beim Login: {e}")
        return None

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

    log.info(f"Successfully retrieved and processed {len(all_devices)} devices (using 'FULL' view).")
    return all_devices

def get_device_by_id(base_url: str, api_token: str, device_id: str) -> Optional[Dict[str, Any]]:
    """
    Ruft die detaillierten Informationen für ein einzelnes Gerät anhand seiner ID ab.
    """
    url = f"{base_url}/devices/{device_id}&views=FULL"
    headers = {"Authorization": f"Bearer {api_token}"}
    log.info(f"Fetching details for device ID '{device_id}'...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        device_data = response.json().get('data')
        if device_data:
            return process_device(device_data)
        else:
            log.warning(f"Device with ID '{device_id}' not found or data is empty.")
            print(f"Device with ID '{device_id}' not found or data is empty.")
            return None
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching details for device ID '{device_id}': {e}")
        print(f"Error fetching details for device ID '{device_id}': {e}")
        if isinstance(e, requests.exceptions.HTTPError) and response is not None:
            if response.status_code == 401:
                log.warning("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen.")
                print("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen.")
            elif response.status_code == 404:
                log.error(f"Gerät mit ID '{device_id}' nicht gefunden (404).")
                print(f"Gerät mit ID '{device_id}' nicht gefunden (404).")
            else:
                log.error(f"HTTP-Fehler beim Abrufen der Geräte-Details (Code: {response.status_code}).")
                print(f"HTTP-Fehler beim Abrufen der Geräte-Details (Code: {response.status_code}).")
        elif isinstance(e, requests.exceptions.ConnectionError):
            log.error(f"Verbindungsfehler beim Zugriff auf die API für Geräte-ID '{device_id}': {e}")
            print(f"Verbindungsfehler beim Zugriff auf die API für Geräte-ID '{device_id}': {e}")
        else:
            log.error(f"Unerwarteter Fehler beim Abrufen der Details für Gerät ID '{device_id}': {e}")
            print(f"Unerwarteter Fehler beim Abrufen der Details für Gerät ID '{device_id}': {e}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Fehler beim Decodieren der JSON-Antwort für Gerät ID '{device_id}': {e}")
        print(f"Fehler beim Decodieren der JSON-Antwort für Gerät ID '{device_id}': {e}")
        return None
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Abrufen der Detailinformationen für Gerät ID '{device_id}': {e}")
        print(f"Unerwarteter Fehler beim Abrufen der Detailinformationen für Gerät ID '{device_id}': {e}")
        return None

def get_device_from_redis_by_hostname(hostname: str) -> Optional[Dict[str, Any]]:
    """Ruft Geräteinformationen aus Redis anhand des Hostnamens ab."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
        device_json = r.get(f"xiq:device:{hostname}")
        if device_json:
            return json.loads(device_json)
        else:
            return None
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}): {e}")
        print(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}): {e}")
        return None
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Abrufen von '{hostname}' aus Redis: {e}")
        print(f"Unerwarteter Fehler beim Abrufen von '{hostname}' aus Redis: {e}")
        return None

def store_devices_in_redis(device_list: List[Dict[str, Any]]):
    """Speichert eine Liste von Geräten in Redis."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
        for device in device_list:
            hostname = device.get("hostname")
            device_id = device.get("id")
            print(f"Zu speicherndes Gerät (ID: {device_id}, Hostname: {hostname}): {device}") # <<< DEBUG
            if hostname:
                r.set(f"xiq:device:{hostname}", json.dumps(device))
                log.debug(f"Gerät mit Hostname '{hostname}' und ID '{device_id}' in Redis gespeichert.")
            elif device_id:
                r.set(f"xiq:device:id:{device_id}", json.dumps(device))
                log.warning(f"Gerät ohne Hostname aber mit ID '{device_id}' unter Schlüssel 'xiq:device:id:{device_id}' in Redis gespeichert.")
            else:
                log.warning(f"Gerät ohne Hostname und ID gefunden: {device}. Konnte nicht in Redis gespeichert werden.")
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}): {e}")
        print(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}): {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Speichern von Geräten in Redis: {e}")
        print(f"Unerwarteter Fehler beim Speichern von Geräten in Redis: {e}")

#def find_hosts(
#    managed_by: Optional[str] = None,
#    location_part: Optional[str] = None,
#    hostname_filter: Optional[str] = None,
#    device_function: Optional[str] = None,
#    exact_match: bool = False,
#) -> List[Dict[str, Any]]:
#    matching_devices = []
#    try:
#        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
#        for key in r.scan_iter("xiq:device:*"):
#            print(f"Gefundener Schlüssel: {key}")
#            if key.startswith("xiq:device:id:"):
#                device_id = key.split(":")[-1]
#                identifier = f"ID: {device_id}"
#            else:
#                identifier = f"Hostname: {key.split(':')[-1]}"
#
#            device_json = r.get(key)
#            if device_json:
#                device = json.loads(device_json)
#                device_function_redis = device.get('deviceFunction')
#                search_term_lower = device_function.lower() if device_function else None
#                print(f"Überprüfe Gerät ({identifier}) - Geräte-Funktion in Redis: '{device_function_redis}', Länge: {len(device_function_redis or '')}, Suchbegriff (lower): '{search_term_lower}', Länge: {len(search_term_lower or '')}")
#                match = True
#
#                if managed_by is not None:
#                    managed = device.get("managed")
#                    managed_check = (managed is not None and
#                                     ((exact_match and managed.lower() == managed_by.lower() == "true") or
#                                      (not exact_match and managed.lower() == managed_by.lower() == "true")))
#                    if not managed_check:
#                        match = False
#
#                if hostname_filter:
#                    hostname = device.get("hostname", "")
#                    hostname_check = (exact_match and hostname.lower() == hostname_filter.lower()) or \
#                                     (not exact_match and hostname_filter.lower() in hostname.lower())
#                    if not hostname_check:
#                        match = False
#
#                if location_part:
#                    locations = device.get("locations", [])
#                    location_match = False
#                    for loc in locations:
#                        location_name = loc.get("name", "")
#                        if (exact_match and location_name.lower() == location_part.lower()) or \
#                           (not exact_match and location_part.lower() in location_name.lower()):
#                            location_match = True
#                            break
#                    if not location_match:
#                        match = False
#
#                if device_function:
#                    if device_function_redis is not None:
#                        device_function_check = (exact_match and device_function_redis.lower() == search_term_lower) or \
#                                                (not exact_match and search_term_lower in device_func_redis.lower())
#                        if not device_function_check:
#                            match = False
#                    else:
#                        match = False
#
#                if match:
#                    matching_devices.append(device)
#    except redis.exceptions.ConnectionError as e:
#        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}) während der Suche: {e}")
#        print(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}) während der Suche: {e}")
#    except Exception as e:
#        log.error(f"Unerwarteter Fehler bei der Suche in Redis: {e}")
#        print(f"Unerwarteter Fehler bei der Suche in Redis: {e}")
#    return matching_devices

def find_hosts(
    managed_by: Optional[str] = None,
    location_part: Optional[str] = None,
    hostname_filter: Optional[str] = None,
    device_function: Optional[str] = None,
    exact_match: bool = False,
) -> List[Dict[str, Any]]:
    matching_devices = []
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DEVICE_DB, decode_responses=True)
        for key in r.scan_iter():  # <--- Geändert: Durchlaufe alle Schlüssel
            print(f"Gefundener Schlüssel: {key}") # <--- Debug-Ausgabe aller Schlüssel
            if key.startswith("xiq:device:"):
                if key.startswith("xiq:device:id:"):
                    device_id = key.split(":")[-1]
                    identifier = f"ID: {device_id}"
                else:
                    identifier = f"Hostname: {key.split(':')[-1]}"

                device_json = r.get(key)
                if device_json:
                    print(f"  Raw JSON from Redis for key '{key}': {device_json}") # <<< DEBUG
                    device = json.loads(device_json)
                    device_function_redis = device.get('deviceFunction')
                    search_term_lower = device_function.lower() if device_function else None
                    print(f"  Überprüfe Gerät ({identifier}) - Geräte-Funktion in Redis: '{device_function_redis}', Länge: {len(device_function_redis or '')}, Suchbegriff (lower): '{search_term_lower}', Länge: {len(search_term_lower or '')}")
                    match = True

                    if managed_by is not None:
                        managed = device.get("managed")
                        managed_check = (managed is not None and
                                         ((exact_match and managed.lower() == managed_by.lower() == "true") or
                                          (not exact_match and managed.lower() == managed_by.lower() == "true")))
                        if not managed_check:
                            match = False

                    if hostname_filter:
                        hostname_lower = hostname.lower()
                        hostname_filter_lower = hostname_filter.lower()
                        if exact_match:
                            hostname_check = hostname_lower == hostname_filter_lower
                        else:
                            hostname_check = hostname_filter_lower in hostname_lower
                        if not hostname_check:
                            match = False

                    if location_part:
                        locations = device.get("locations", [])
                        location_match = False
                        location_part_lower = location_part.lower()
                        for loc in locations:
                            location_name_lower = loc.get("name", "").lower()
                            if exact_match:
                                if location_name_lower == location_part_lower:
                                    location_match = True
                                    break
                            else:
                                if location_part_lower in location_name_lower:
                                    location_match = True
                                    break
                        if not location_match:
                            match = False

                    if device_function:
                        if device_function_redis is not None:
                            search_term_lower = device_function.lower()
                            if exact_match:
                                device_function_check = device_function_redis.lower() == search_term_lower
                            else:
                                device_function_check = search_term_lower in device_function_redis.lower()
                            if not device_function_check:
                                match = False
                        else:
                            match = False

                    if match:
                        matching_devices.append(device)
    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}) während der Suche: {e}")
        print(f"Fehler bei der Verbindung zu Redis (db={REDIS_DEVICE_DB}) während der Suche: {e}")
    except Exception as e:
        log.error(f"Unerwarteter Fehler bei der Suche in Redis: {e}")
        print(f"Unerwarteter Fehler bei der Suche in Redis: {e}")
    return matching_devices

def get_device_status_summary(location_id):
    global API_SECRET  # Access the global API_SECRET variable
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{XIQ_BASE_URL}/locations/{location_id}/device_status_summary", headers=headers)
        response.raise_for_status()
        response_json = response.json()
        log.info(f"Device status summary for location ID {location_id} retrieved successfully: {response_json}")
        print(json.dumps(response_json, indent=4))  # Ausgabe als formatiertes JSON
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving device status summary for location ID {location_id}: {e}")
        print(f"Error retrieving device status summary for location ID {location_id}: {e}")
        if isinstance(e, requests.exceptions.HTTPError) and response is not None:
            if response.status_code == 401:
                log.warning("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen. Bitte loggen Sie sich erneut ein.")
                print("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen. Bitte loggen Sie sich erneut ein.")
            elif response.status_code == 404:
                log.error(f"Location mit ID '{location_id}' nicht gefunden (404).")
                print(f"Location mit ID '{location_id}' nicht gefunden (404).")
            else:
                log.error(f"HTTP-Fehler beim Abrufen des Gerätestatus (Code: {response.status_code}).")
                print(f"HTTP-Fehler beim Abrufen des Gerätestatus (Code: {response.status_code}).")
        elif isinstance(e, requests.exceptions.ConnectionError):
            log.error(f"Verbindungsfehler beim Zugriff auf die API: {e}")
            print(f"Verbindungsfehler beim Zugriff auf die API: {e}")
        else:
            log.error(f"Unerwarteter Fehler beim Abrufen des Gerätestatus: {e}")
            print(f"Unerwarteter Fehler beim Abrufen des Gerätestatus: {e}")
    except json.JSONDecodeError as e:
        log.error(f"Fehler beim Decodieren der JSON-Antwort für den Gerätestatus: {e}")
        print(f"Fehler beim Decodieren der JSON-Antwort für den Gerätestatus: {e}")

def get_locations_tree():
    global API_SECRET
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }
    url = f"{XIQ_BASE_URL}/locations/tree"
    try:
        log.info(f"Rufe Location Tree ab: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        locations_tree = response.json()
        print(json.dumps(locations_tree, indent=4))  # Ausgabe auf stdout

        # Speichern in Redis (db=1)
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOCATIONS_DB, decode_responses=True)
            r.set("xiq:locations:tree", json.dumps(locations_tree))
            log.info("Location Tree erfolgreich in Redis (db=1) gespeichert.")
        except redis.exceptions.ConnectionError as e:
            log.error(f"Fehler bei der Verbindung zu Redis (db=1): {e}")
        except Exception as e:
            log.error(f"Unerwarteter Fehler beim Speichern des Location Tree in Redis: {e}")

    except requests.exceptions.RequestException as e:
        log.error(f"Fehler beim Abrufen des Location Tree: {e}")
        print(f"Fehler beim Abrufen des Location Tree: {e}")
        if isinstance(e, requests.exceptions.HTTPError) and response is not None:
            if response.status_code == 401:
                log.warning("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen. Bitte loggen Sie sich erneut ein.")
                print("Zugriff verweigert (401). Wahrscheinlich ist der API-Token abgelaufen. Bitte loggen Sie sich erneut ein.")
            else:
                log.error(f"HTTP-Fehler beim Abrufen des Location Tree (Code: {response.status_code}).")
                print(f"HTTP-Fehler beim Abrufen des Location Tree (Code: {response.status_code}).")
        elif isinstance(e, requests.exceptions.ConnectionError):
            log.error(f"Verbindungsfehler beim Zugriff auf die API: {e}")
            print(f"Verbindungsfehler beim Zugriff auf die API: {e}")
        else:
            log.error(f"Unerwarteter Fehler beim Abrufen des Location Tree: {e}")
            print(f"Unerwarteter Fehler beim Abrufen des Location Tree: {e}")
    except json.JSONDecodeError as e:
        log.error(f"Fehler beim Decodieren der JSON-Antwort für den Location Tree: {e}")
        print(f"Fehler beim Decodieren der JSON-Antwort für den Location Tree: {e}")

def get_location_info_by_name(search_name: str) -> Optional[Dict[str, Any]]:
    """Sucht nach einer Location im Location Tree (Redis db=1) und gibt unique_name und id aus."""
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
        print(f"Fehler bei der Verbindung zu Redis (db=1): {e}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Fehler beim Decodieren des Location Tree aus Redis: {e}")
        print(f"Fehler beim Decodieren des Location Tree aus Redis: {e}")
        return None
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Suchen nach Location: {e}")
        print(f"Unerwarteter Fehler beim Suchen nach Location: {e}")
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
        if secs > 0 and days == 0 and hours == 0:  # Nur Sekunden anzeigen, wenn Tage und Stunden null sind
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
            fieldnames = ["id", "hostname", "mac_address", "ip_address", "model", "serialNumber", "uptime_readable", "managed", "site", "building", "floor", "latitude", "longitude", "lldp_remote_chassis_id", "lldp_remote_port_id", "cdp_neighbor", "cdp_neighbor_port"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in data:
                locations = item.get("locations", [])
                site = locations[0].get("name") if locations and len(locations) > 0 else ""
                building = locations[1].get("name") if locations and len(locations) > 1 else ""
                floor = locations[2].get("name") if locations and len(locations) > 2 else ""
                latitude = locations[-1].get("latitude") if locations and locations[-1].get("latitude") else ""
                longitude = locations[-1].get("longitude") if locations and locations[-1].get("longitude") else ""

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
                    "serialNumber": item.get("serialNumber"),
                    "uptime_readable": item.get("uptime_readable"),
                    "managed": item.get("managed"),
                    "site": site,
                    "building": building,
                    "floor": floor,
                    "latitude": latitude,
                    "longitude": longitude,
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

def get_api_token(args):
    """
    Lädt den API-Token entweder aus der Datei oder ruft ihn per Login ab.

    Args:
        args: Die von argparse geparsten Kommandozeilenargumente.

    Returns:
        Den API-Token als String oder None im Fehlerfall.
    """
    env_credentials = load_credentials_from_env()
    if env_credentials:
        args.username, args.password = env_credentials

    if args.username and args.password:
        token = get_xiq_api_token(args.serverRoot, args.username, args.password)
        if token:
            save_api_token(token, args.api_key_file)
        return token
    else:
        return load_api_token(args.api_key_file)

def handle_get_devicelist(args, api_token):
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

def handle_get_device_by_id(args, api_token):
    device_details = get_device_by_id(args.serverRoot, api_token, args.device_id)
    if device_details:
        print(json.dumps(device_details, indent=4))
    else:
        log.error(f"Fehler beim Abrufen der Details für Gerät mit ID '{args.device_id}'.")
        sys.exit(1)

def handle_get_device_by_hostname(args):
    device_from_redis = get_device_from_redis_by_hostname(args.hostname)
    if device_from_redis:
        print(json.dumps(device_from_redis, indent=4))
    else:
        log.warning(f"Keine Geräteinformationen für Hostname '{args.hostname}' in Redis gefunden.")

def handle_find_hosts(args):
    matching_devices = find_hosts(
        args.managed_by_value,
        args.location_name_part,
        args.hostname_value,
        args.device_function,
        args.exact_match,
    )
    if matching_devices:
        print("Gefundene Hosts:")
        for device in matching_devices:
            print(f"  ID: {device.get('id')}")
            print(f"  Hostname: {device.get('hostname')}")
            print(f"  MAC-Adresse: {device.get('mac_address')}")
            print(f"  IP-Adresse: {device.get('ip_address')}")
            print(f"  Managed: {device.get('managed')}")
            print(f"  Device Function: {device.get('deviceFunction')}")
            print(f"  Locations: {[loc.get('name') for loc in device.get('locations', [])]}")
            print("-" * 20)
    else:
        print("Keine Hosts gefunden, die den Suchkriterien entsprechen.")

def handle_get_device_status(args, api_token):
    if api_token:
        get_device_status_summary(args.location_id)
    else:
        log.error("Kein API-Token vorhanden. Bitte loggen Sie sich zuerst ein oder geben Sie den Pfad zur Token-Datei an.")
        print("Kein API-Token vorhanden. Bitte loggen Sie sich zuerst ein oder geben Sie den Pfad zur Token-Datei an.")
        sys.exit(1)

def handle_get_locations_tree(api_token):
    if api_token:
        get_locations_tree()
    else:
        log.error("Kein API-Token vorhanden. Bitte loggen Sie sich zuerst ein oder geben Sie den Pfad zur Token-Datei an.")
        print("Kein API-Token vorhanden. Bitte loggen Sie sich zuerst ein oder geben Sie den Pfad zur Token-Datei an.")
        sys.exit(1)

def handle_find_location(args):
    location_info = get_location_info_by_name(args.search_location)
    if location_info:
        print("Gefundene Location:")
        print(f"  unique_name: {location_info.get('unique_name')}")
        print(f"  ID: {location_info.get('id')}")
    else:
        print(f"Keine Location mit dem Suchbegriff '{args.search_location}' gefunden.")

def main():
    parser = ArgumentParser(description="Interagiert mit der ExtremeCloud IQ API.")

    # Authentifizierungsgruppe
    auth_group = parser.add_argument_group('Authentifizierung')
    auth_group.add_argument("-k", "--api_key_file", dest="api_key_file", default="xiq_api_token.txt", help="Pfad zur API-Token-Datei.")
    auth_group.add_argument("-u", "--username", dest="username", help="Benutzername für die XIQ API.")
    auth_group.add_argument("-p", "--password", dest="password", help="Passwort für die XIQ API.")
    auth_group.add_argument("--create-env", action="store_true", help="Erstellt eine .env-Datei mit den angegebenen Benutzername und Passwort.")

    # API-Abruf-Gruppe
    api_group = parser.add_argument_group('API-Abruf')
    api_group.add_argument("-s", "--server", dest="serverRoot", default="https://api.extremecloudiq.com", help="Basis-URL der XIQ API.")
    api_group.add_argument("--get-devicelist", action="store_true", help="Ruft die Liste der Geräte ab.")
    api_group.add_argument("--get-device-by-id", dest="device_id", help="Ruft die Details für ein Gerät mit der angegebenen ID ab.")
    api_group.add_argument("--get-device-status", dest="location_id", help="Ruft die Gerätestatusübersicht für die angegebene Location-ID ab.")
    api_group.add_argument("--get-locations-tree", action="store_true", help="Ruft den Location Tree ab und speichert ihn in Redis (db=1).")
    api_group.add_argument("--find-location", dest="search_location", help="Sucht nach einer Location im Location Tree (Redis db=1) und gibt unique_name und id aus.")

    # Redis-Interaktions-Gruppe
    redis_group = parser.add_argument_group('Redis-Interaktion')
    redis_group.add_argument("--get-device-by-hostname", dest="hostname", help="Ruft die Details für ein Gerät mit dem angegebenen Hostnamen aus Redis ab.")
    redis_group.add_argument("-f", "--find-hosts", action="store_true", help="Sucht Hosts in Redis basierend auf optionalen Kriterien.")
    redis_group.add_argument("-m", "--managed_by", dest="managed_by_value", help="Optional: Filter für 'managed_by' bei der Redis-Suche.")
    redis_group.add_argument("-l", "--location-part", dest="location_name_part", help="Optional: Teil des Location-Namens für die Redis-Suche.")
    redis_group.add_argument("--hostname-filter", dest="hostname_value", help="Optional: Hostname für die Redis-Suche.")
    redis_group.add_argument("--device-function", dest="device_function", help="Optional: Filter für die Gerätefunktion (z.B., AP, Switch).")
    redis_group.add_argument("--exact-match", action="store_true", help="Verwendet eine exakte Übereinstimmung für die Filter.")
    redis_group.add_argument("--store-redis", action="store_true", help="Speichert die Geräteinformationen in Redis (db=0).")

    # Ausgabe-Optionen
    output_group = parser.add_argument_group('Ausgabe')
    output_group.add_argument("-o", "--output_file", dest="output_file", default="XiqDeviceList.json", help="Dateiname für die Ausgabe der Geräteliste (JSON).")
    output_group.add_argument("--show-pretty", action="store_true", help="Zeigt eine vereinfachte Ausgabe der Geräte (id, hostname, mac, ip) auf der Konsole.")
    output_group.add_argument("--output-csv", dest="output_csv_file", help="Dateiname für die Ausgabe der Geräteliste als CSV.")

    # Sonstige Optionen
    misc_group = parser.add_argument_group('Sonstige')
    misc_group.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe aktivieren")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)

    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug("Verbose-Modus aktiviert.")
        print("Verbose-Modus aktiviert.")

    if args.create_env and args.username and args.password:
        save_credentials_to_env(args.username, args.password)
        sys.exit(0)
    elif args.create_env:
        parser.error("--create-env erfordert die Angabe von -u und -p.")

    api_token = get_api_token(args)  # Funktion zum Laden oder Abrufen des Tokens
    if not api_token:
        log.error("Ungültiger API-Token. Skript wird beendet.")
        sys.exit(1)

    action_map = {
        args.get_devicelist: lambda: handle_get_devicelist(args, api_token),
        args.device_id: lambda: handle_get_device_by_id(args, api_token),
        args.hostname: lambda: handle_get_device_by_hostname(args),
        args.find_hosts: lambda: handle_find_hosts(args),
        args.location_id: lambda: handle_get_device_status(args, api_token),
        args.get_locations_tree: lambda: handle_get_locations_tree(api_token),
        args.search_location: lambda: handle_find_location(args),
    }

    executed = False
    for condition, action in action_map.items():
        if condition:
            action()
            executed = True
            break

    if not executed and any(vars(args).values()):
        log.warning("Keine passende Aktion für die angegebenen Argumente gefunden.")
    elif not executed:
        parser.print_help()

if __name__ == "__main__":
    main()