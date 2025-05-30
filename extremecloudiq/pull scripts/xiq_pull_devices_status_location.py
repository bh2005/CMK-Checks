#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# License: GNU General Public License v2
#
# Author: bh2005
# URL  : https://github.com/bh2005
# Date : 2024-03-01
#
# This script retrieves the device status summary for a location from ExtremeCloud IQ via the API and returns it as JSON.
#
# Release notes - init release

import requests
import json
import os
import logging
import argparse

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "device_status.log"
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
        # Check if the error is due to an expired token, and renew it.
        if response.status_code == 401:  # Assuming 401 is unauthorized
            log.warning("Token expired, attempting to renew")
            print("Token expired, attempting to renew")
            if renew_token():
                log.info("Token renewal successful, retrying request")
                print("Token renewal successful, retrying request")
                # Retry the request after token renewal
                get_device_status_summary(location_id)
            else:
                log.error("Token renewal failed. Request not retried.")
                print("Token renewal failed. Request not retried.")
        else:
            log.error(f"Error retrieving device status summary. Error Code: {response.status_code}")
            print(f"Error retrieving device status summary. Error Code: {response.status_code}")

def main():
    # Check if API_SECRET is available, otherwise renew token
    global API_SECRET  # Access the global API_SECRET variable
    if not API_SECRET:
        log.info("API Secret not found, attempting to renew")
        print("API Secret not found, attempting to renew")
        if renew_token():
            log.info("Token renewed successfully, continuing")
            print("Token renewed successfully, continuing")
        else:
            log.error("Token renewal failed, exiting.")
            print("Token renewal failed, exiting.")
            return

    parser = argparse.ArgumentParser(description="Retrieves the device status summary for a location from ExtremeCloud IQ via the API.")
    parser.add_argument("location_id", help="The ID of the location to retrieve the device status summary for.")
    parser.add_argument("-l", "--log", help="Path to the log file.", default="device_status.log")
    args = parser.parse_args()

    location_id = args.location_id
    LOG_FILE = args.log

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    get_device_status_summary(location_id)

if __name__ == "__main__":
    main()
