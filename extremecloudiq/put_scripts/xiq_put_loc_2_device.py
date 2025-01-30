import requests
import json
import csv
import os
import logging

# API Configuration (use environment variables)
XIQ_BASE_URL = 'https://api.extremecloudiq.com/v2'

# Configure logging
LOG_FILE = "xiq_api.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def generate_xiq_api_key(username, password):
    # Generate new API key using username and password
    url = f"{XIQ_BASE_URL}/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        api_key = json_response.get("access_token")

        if not api_key:
            log.error("Error: Could not extract API key from the response")
            return None
        return api_key

    except requests.exceptions.RequestException as e:
        log.error(f"Error during API request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Error decoding JSON response: {str(e)}")
        return None

def renew_token():
    # Renew the API token using stored credentials
    username = os.getenv('ADMIN_MAIL')
    password = os.getenv('XIQ_PASS')

    if not username or not password:
        log.error("Environment variables ADMIN_MAIL or XIQ_PASS are not set")
        return None

    new_api_key = generate_xiq_api_key(username, password)
    if new_api_key:
        os.environ["XIQ_API_SECRET"] = new_api_key
        log.info("API key has been renewed successfully")
        return new_api_key
    else:
        log.error("Failed to renew the API key")
        return None

def get_xiq_api_token():
    #"""Gets the XIQ API token, renewing it if necessary."""
    api_token = os.getenv("XIQ_API_SECRET")

    if not api_token:
        api_token = renew_token()
        if not api_token:
            log.error("XIQ API token is not set and could not be renewed.")
            return None
    return api_token

def assign_device_location(device_id, location_id, x, y, latitude, longitude):
    #"""Assigns a location to a device in XIQ."""
    api_token = get_xiq_api_token()
    if not api_token:
        return None

    url = f"{XIQ_BASE_URL}/devices/{device_id}/location"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

    payload = {
        "locationId": location_id,
        "geoCoordinate": {
            "x": x,
            "y": y,
            "latitude": latitude,
            "longitude": longitude
        }
    }

    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        log.info(f"Location assigned to device {device_id} successfully.")
    except requests.exceptions.RequestException as e:
        log.error(f"Error assigning location to device {device_id}: {e}")
        if response.text:
            log.error(f"Response content: {response.text}")

def read_csv_and_assign_locations():
    #"""Reads the CSV file and assigns locations to devices."""
    with open("devices_locations.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_id = row.get("id")
            location_id = row.get("location_id")
            x = row.get("x")
            y = row.get("y")
            latitude = row.get("latitude")
            longitude = row.get("longitude")

            if not device_id:
                log.warning(f"Skipping row: device id is missing")
                continue

            if not location_id:
                log.warning(f"Skipping row for device {device_id}: location_id is missing")
                continue

            # Konvertiere x, y, latitude und longitude in floats, falls vorhanden
            try:
                x = float(x) if x else None
                y = float(y) if y else None
                latitude = float(latitude) if latitude else None
                longitude = float(longitude) if longitude else None
            except ValueError:
                log.warning(f"Skipping row for device {device_id}: invalid x, y, latitude or longitude values")
                continue

            assign_device_location(device_id, location_id, x, y, latitude, longitude)

if __name__ == "__main__":
    read_csv_and_assign_locations()