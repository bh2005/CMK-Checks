import csv
import requests
import json
import os
import logging

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'
CSV_FILE = "commands.csv"

# Configure logging
LOG_FILE = "xiq_api.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def generate_xiq_api_key(username, password):
    # (Ihr vorhandener Code)
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
    # (Ihr vorhandener Code)
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

def api_command_execute(id, command):
    global API_SECRET  # Access the global API_SECRET variable
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }
    payload = {
        "commands": [command], # commands muss als Array übergeben werden
    }

    try:
        response = requests.post(f"{XIQ_BASE_URL}/devices/{id}/:cli", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        log.info(f"Command for ID {id} executed successfully: {response.json()}")
    except requests.exceptions.RequestException as e:
        log.error(f"Error executing command for ID {id}: {e}")
        # Check if the error is due to an expired token, and renew it.
        if response.status_code == 401:  # Assuming 401 is unauthorized
            log.warning("Token expired, attempting to renew")
            if renew_token():
                log.info("Token renewal successful, retrying request")
                # Retry the request after token renewal
                api_command_execute(id, command)
            else:
                log.error("Token renewal failed. Request not retried.")
        else:
            log.error(f"Error executing command. Error Code: {response.status_code}")

def csv_commands_execute(csv_file):
    with open(csv_file, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) == 2:
                id = row[0]
                command = row[1]
                api_command_execute(id, command)
            else:
                log.warning(f"Invalid row in CSV: {row}")

def main():
    # Check if API_SECRET is available, otherwise renew token
    global API_SECRET  # Access the global API_SECRET variable
    if not API_SECRET:
        log.info("API Secret not found, attempting to renew")
        if renew_token():
            log.info("Token renewed successfully, continuing")
        else:
            log.error("Token renewal failed, exiting.")
            return

    csv_commands_execute(CSV_FILE)

if __name__ == "__main__":
    main()
