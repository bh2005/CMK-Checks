#!/usr/bin/env python3

import redis
import json
import logging
from argparse import ArgumentParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

def find_hosts(managed_by_value=None, location_name_part=None):
    """Findet Hosts in Redis basierend auf optionalen 'managed_by' und Teil des 'location' Namens (UND-Verknüpfung) und gibt spezifische Informationen aus."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        all_keys = r.keys("xiq:device:*")
        matching_devices_info = []

        for key in all_keys:
            try:
                device_json = r.get(key)
                if device_json:
                    device_data = json.loads(device_json)
                    hostname = device_data.get("hostname")
                    managed_by_match = True
                    location_match = True

                    if managed_by_value:
                        if device_data.get("managed_by") != managed_by_value:
                            managed_by_match = False

                    if location_name_part:
                        found_in_location = False
                        locations = device_data.get("locations", [])
                        if isinstance(locations, list):
                            for location in locations:
                                if isinstance(location, dict) and location.get("name") and location_name_part in location.get("name"):
                                    found_in_location = True
                                    break
                        if not found_in_location:
                            location_match = False

                    if managed_by_match and location_match and hostname:
                        matching_devices_info.append({
                            "id": device_data.get("id"),
                            "hostname": hostname,
                            "mac_address": device_data.get("mac_address"),
                            "ip_address": device_data.get("ip_address")
                        })

            except json.JSONDecodeError:
                log.warning(f"Ungültiges JSON für Schlüssel: {key}")
            except Exception as e:
                log.error(f"Fehler beim Verarbeiten des Schlüssels {key}: {e}")

        return matching_devices_info

    except redis.exceptions.ConnectionError as e:
        log.error(f"Fehler bei der Verbindung zu Redis: {e}")
        return []
    except Exception as e:
        log.error(f"Unerwarteter Fehler beim Abrufen von Daten aus Redis: {e}")
        return []

if __name__ == "__main__":
    parser = ArgumentParser(description="Findet Hosts in Redis basierend auf optionalen 'managed_by' und Teil des 'location' Namens (UND-Verknüpfung) und gibt spezifische Informationen aus.")
    parser.add_argument("-m", "--managed_by", dest="managed_by_value",
                        help="Optional: Der Wert des 'managed_by' Feldes, nach dem gesucht werden soll (z.B., 'XIQ').")
    parser.add_argument("-l", "--location_part", dest="location_name_part",
                        help="Optional: Ein Teil des Namens der Location, nach dem gesucht werden soll (z.B., 'LOC001').")
    args = parser.parse_args()

    managed_by = args.managed_by_value
    location_part = args.location_name_part
    matching_devices = find_hosts(managed_by, location_part)

    if matching_devices:
        print("Gefundene Hosts:")
        for device in matching_devices:
            print(f"  ID: {device.get('id')}")
            print(f"  Hostname: {device.get('hostname')}")
            print(f"  MAC-Adresse: {device.get('mac_address')}")
            print(f"  IP-Adresse: {device.get('ip_address')}")
            print("-" * 20)
    else:
        print("Keine Hosts gefunden, die den Suchkriterien entsprechen.")