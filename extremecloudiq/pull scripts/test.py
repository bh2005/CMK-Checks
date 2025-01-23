import os
import time
import datetime
import requests
import json
import glob
import csv
import sys
import argparse
import logging
from tqdm import tqdm
import concurrent.futures  # Für parallele Ausführung

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "xiq_api.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def renew_token():
    # Implementiere die Logik zur Erneuerung des Tokens
    # Beispiel:
    # response = requests.post(f"{XIQ_BASE_URL}/auth/renew", headers={"Authorization": f"Bearer {API_SECRET}"})
    # if response.status_code == 200:
    #     new_token = response.json().get('token')
    #     os.environ['XIQ_API_SECRET'] = new_token
    pass

def fetch_page(page, views):
    response = requests.get(
        f"{XIQ_BASE_URL}/devices?page={page}&limit=100&views={views}",
        headers={"Authorization": f"Bearer {API_SECRET}"}
    )
    if response.status_code != 200:
        log.error(f"Error: API request failed with HTTP status {response.status_code}.")
        return None
    return response.json().get('data', [])

def get_devices(views, debug):
    if not API_SECRET:
        log.error("Error: API_SECRET environment variable not set.")
        return 1

    all_devices = []
    page = 1
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            future_to_page = {executor.submit(fetch_page, page, views): page for page in range(1, 11)}  # Beispiel: 10 Seiten parallel
            for future in concurrent.futures.as_completed(future_to_page):
                devices = future.result()
                if not devices:
                    break
                all_devices.extend(devices)
                if len(devices) < 100:
                    break
            page += 10
            time.sleep(3)

    with open('devices.json', 'w') as f:
        json.dump(all_devices, f, indent=2)

    log.info("Devices data has been written to devices.json (formatted with json).")

# Weitere Funktionen ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and process devices from ExtremeCloud IQ API.')
    parser.add_argument('-V', '--views', type=str, choices=['BASIC', 'FULL', 'STATUS', 'LOCATION', 'CLIENT', 'DETAIL'], default='FULL',
                        help='Specify the view type for the API request. Default is FULL.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug information.')
    
    args = parser.parse_args()
    
    get_devices(args.views, args.debug)
    combine_json_files()
    convert_json_to_csv('output_extreme_api.json', 'output_extreme_api.csv')
    delete_raw_files()
    
    
    
    
    
    
    ################################################2.
    
    import os
import time
import datetime
import requests
import json
import glob
import csv
import sys
import argparse
import logging
from tqdm import tqdm
import getpass  # For secure password input

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "xiq_api.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def generate_xiq_api_key(username, password):
    url = "https://api.extremecloudiq.com/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        api_key = json_response.get("access_token")

        if not api_key:
            log.error("Error: Could not extract API key from the response. Check the JSON format of the response.")
            log.error(json_response)
            return None
        return api_key

    except requests.exceptions.RequestException as e:
        log.error(f"Error during API request: {e}")
        if response is not None:
            log.error(f"Server response text: {response.text}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Error decoding JSON response: {e}")
        return None

def renew_token():
    username = os.getenv('ADMIN_MAIL')
    if not username:
        log.error("Environment variable ADMIN_MAIL is not set")
        return None

    password = getpass.getpass("ExtremeCloud IQ password: ")

    new_api_key = generate_xiq_api_key(username, password)
    if new_api_key:
        os.environ["XIQ_API_SECRET"] = new_api_key
        update_bashrc(new_api_key)
        log.info("API key has been renewed and updated.")
        return new_api_key
    else:
        log.error("Failed to renew the API key.")
        return None

def update_bashrc(api_key):
    bashrc_path = os.path.expanduser("~/.bashrc")
    env_var_entry = f'export XIQ_API_SECRET="{api_key}"\n'

    with open(bashrc_path, 'r') as bashrc:
        lines = bashrc.readlines()

    with open(bashrc_path, 'w') as bashrc:
        var_set = False
        for line in lines:
            if line.startswith('export XIQ_API_SECRET='):
                bashrc.write(env_var_entry)
                var_set = True
            else:
                bashrc.write(line)

        if not var_set:
            bashrc.write(env_var_entry)

def get_devices(views, debug):
    if not API_SECRET:
        log.error("API_SECRET environment variable not set, renewing token.")
        API_SECRET = renew_token()
        if not API_SECRET:
            return 1

    page = 1
    page_size = 100
    all_devices = []

    while True:
        response = requests.get(
            f"{XIQ_BASE_URL}/devices?page={page}&limit={page_size}&views={views}",
            headers={"Authorization": f"Bearer {API_SECRET}"}
        )

        if debug:
            log.debug(f"DEBUG: Raw API response for page {page}:")
            log.debug(response.text)

        if response.status_code == 401:  # Unauthorized, token might be expired
            log.info("Unauthorized access, attempting to renew token.")
            API_SECRET = renew_token()
            if not API_SECRET:
                return 1
            continue

        if response.status_code != 200:
            log.error(f"Error: API request failed with HTTP status {response.status_code}.")
            log.error(response.json())
            break

        with open(f"raw_devices_page_{page}.json", 'w') as f:
            f.write(response.text)

        devices = response.json().get('data', [])
        if not devices:
            log.info(f"No devices found on page {page}, stopping.")
            break

        all_devices.extend(devices)

        if len(devices) < page_size:
            break

        page += 1
        time.sleep(3)

    with open('devices.json', 'w') as f:
        json.dump(all_devices, f, indent=2)

    log.info("Devices data has been written to devices.json (formatted with json).")

# Weitere Funktionen wie combine_json_files, format_mac_address, calculate_uptime, convert_json_to_csv, delete_raw_files bleiben unverändert ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and process devices from ExtremeCloud IQ API.')
    parser.add_argument('-V', '--views', type=str, choices=['BASIC', 'FULL', 'STATUS', 'LOCATION', 'CLIENT', 'DETAIL'], default='FULL',
                        help='Specify the view type for the API request. Default is FULL.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug information.')

    args = parser.parse_args()

    get_devices(args.views, args.debug)
    combine_json_files()
    convert_json_to_csv('output_extreme_api.json', 'output_extreme_api.csv')
    delete_raw_files()