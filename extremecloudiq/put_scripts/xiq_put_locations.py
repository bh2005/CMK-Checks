import requests
import json
import csv
import os
import logging

# API Configuration (use environment variables)
XIQ_BASE_URL = 'https://api.extremecloudiq.com/v2'

# Configure logging
LOG_FILE = "xiq_api.log"  # Log file
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def generate_xiq_api_key(username, password):
    # Generate new API key using username and password
    # Returns:
    #     str: API key if successful, None if failed
    url = f"{XIQ_BASE_URL}/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
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
    # Returns:
    #     str: New access token if successful, None if failed
    username = os.getenv('ADMIN_MAIL')
    password = os.getenv('XIQ_PASS')

    if not username or not password:
        log.error("Environment variables ADMIN_MAIL or XIQ_PASS are not set")
        return None

    new_api_key = generate_xiq_api_key(username, password)
    if new_api_key:
        os.environ["XIQ_API_SECRET"] = new_api_key # Set environment variable
        log.info("API key has been renewed successfully")
        return new_api_key
    else:
        log.error("Failed to renew the API key")
        return None

def get_xiq_api_token():
    #"""Gets the XIQ API token, renewing it if necessary."""
    api_token = os.getenv("XIQ_API_SECRET")  # Get from environment

    if not api_token:
        api_token = renew_token()  # Try renewing if not set
        if not api_token:
            log.error("XIQ API token is not set and could not be renewed.")
            return None
    return api_token

def get_org_id(org_name):
    #"""Gets the ID of an organization by its name."""
    api_token = get_xiq_api_token()  # Get the API token
    if not api_token:
        return None  # Return None if token retrieval fails.

    try:
        response = requests.get(f"{XIQ_BASE_URL}/orgs", headers={"Authorization": f"Bearer {api_token}"}) # Use retrieved token.
        response.raise_for_status()
        orgs = response.json().get("data", [])
        for org in orgs:
            if org.get("name") == org_name:
                return org.get("id")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting organization ID: {e}")
        return None

def get_city_id(city_name):
    #"""Gets the ID of a city by its name."""
    api_token = get_xiq_api_token()
    if not api_token:
        return None

    try:
        response = requests.get(f"{XIQ_BASE_URL}/cities", headers={"Authorization": f"Bearer {api_token}"})
        response.raise_for_status()
        cities = response.json().get("data", [])
        for city in cities:
          if city.get("name") == city_name:
            return city.get("id")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting city ID: {e}")
        return None


def get_building_id(building_name):
    """Gets the ID of a building by its name."""
    api_token = get_xiq_api_token()
    if not api_token:
        return None

    try:
        response = requests.get(f"{XIQ_BASE_URL}/buildings", headers={"Authorization": f"Bearer {api_token}"})
        response.raise_for_status()
        buildings = response.json().get("data", [])
        for building in buildings:
            if building.get("name") == building_name:
                return building.get("id")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting building ID: {e}")
        return None


def get_floor_id(floor_name, building_id):
    #"""Gets the ID of a floor by its name and building ID."""
    api_token = get_xiq_api_token()
    if not api_token:
        return None

    try:
        response = requests.get(f"{XIQ_BASE_URL}/floors", headers={"Authorization": f"Bearer {api_token}"})
        response.raise_for_status()
        floors = response.json().get("data", [])
        for floor in floors:
            if floor.get("name") == floor_name and floor.get("buildingId") == building_id:
                return floor.get("id")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting floor ID: {e}")
        return None


def create_location(name, org_id, building_id, floor_id, city_id):
    #"""Creates a new location in XIQ."""
    api_token = get_xiq_api_token()
    if not api_token:
        return None

    payload = {
        "name": name,
        "orgId": org_id,
        "parentIds": [building_id, floor_id],
        "address": {
            "cityId": city_id
        }
    }
    try:
        response = requests.post(f"{XIQ_BASE_URL}/locations", headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        print(f"Location '{name}' created successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error creating location: {e}")
        if response.text: # Check if the response has content
            print(f"Response content: {response.text}")

def read_csv_and_create_locations():
    #"""Reads the CSV file and creates locations."""
    with open("locations.csv", "r", encoding="utf-8") as csvfile: # Specify encoding
        reader = csv.DictReader(csvfile)
        for row in reader:
            org_id = get_org_id(row["org_name"])
            if org_id is None:
                print(f"Organization '{row['org_name']}' not found. Skipping.")
                continue

            city_id = get_city_id(row["city_name"])
            if city_id is None:
                print(f"City '{row['city_name']}' not found. Skipping.")
                continue

            building_id = get_building_id(row["building_name"])
            if building_id is None:
                print(f"Building '{row['building_name']}' not found. Skipping.")
                continue

            floor_id = get_floor_id(row["floor_name"], building_id)
            if floor_id is None:
                print(f"Floor '{row['floor_name']}' not found. Skipping.")
                continue

            name = f"{row['building_name']} - {row['floor_name']}"
            create_location(name, org_id, building_id, floor_id, city_id)


if __name__ == "__main__":
    read_csv_and_create_locations()
