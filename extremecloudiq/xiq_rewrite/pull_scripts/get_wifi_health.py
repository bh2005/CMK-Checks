#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# License: GNU General Public License v2
#
# Author: bh2005
# URL  : https://github.com/bh2005
# Date : 2024-04-02
#
# This script retrieves Wi-Fi overall health for a given location from ExtremeCloud IQ via the API and outputs it to log file and stdout.
# adding auth module support

import requests
import json
import os
import logging
import argparse
import time
from tqdm import tqdm
import modules.xiq_api_auth # nutzt das Modul aus dem Unterverzeichnis

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "wifi_health.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def get_wifi_health(location_id):
    global API_SECRET  # Access the global API_SECRET variable
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }
    url = f"{XIQ_BASE_URL}/locations/{location_id}/wifi-health"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        log.info(f"Wi-Fi health retrieved successfully for location ID: {location_id}")
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving Wi-Fi health for location ID: {location_id}: {e}")
        print(f"Error retrieving Wi-Fi health for location ID: {location_id}: {e}")
        # Check if the error is due to an expired token, and renew it.
        if response.status_code == 401:  # Assuming 401 is unauthorized
            log.warning("Token expired, attempting to renew")
            print("Token expired, attempting to renew")
            if modules.xiq_api_auth.renew_token(): # nutzt das Modul aus dem Unterverzeichnis
                log.info("Token renewal successful, retrying request")
                print("Token renewal successful, retrying request")
                # Retry the request after token renewal
                return get_wifi_health(location_id)
            else:
                log.error("Token renewal failed. Request not retried.")
                print("Token renewal failed. Request not retried.")
        else:
            log.error(f"Error retrieving Wi-Fi health. Error Code: {response.status_code}")
            print(f"Error retrieving Wi-Fi health. Error Code: {response.status_code}")
        return None

def main():
    # Check if API_SECRET is available, otherwise renew token
    global API_SECRET  # Access the global API_SECRET variable
    if not API_SECRET:
        log.info("API Secret not found, attempting to renew")
        print("API Secret not found, attempting to renew")
        if modules.xiq_api_auth.renew_token(): # nutzt das Modul aus dem Unterverzeichnis
            log.info("Token renewed successfully, continuing")
            print("Token renewed successfully, continuing")
        else:
            log.error("Token renewal failed, exiting.")
            print("Token renewal failed, exiting.")
            return

    parser = argparse.ArgumentParser(description="Retrieves Wi-Fi overall health for a given location from ExtremeCloud IQ via the API and outputs it to log file and stdout.")
    parser.add_argument("location_id", help="The location ID for which to retrieve Wi-Fi health.")
    parser.add_argument("-l", "--log", help="Path to the log file.", default="wifi_health.log")
    args = parser.parse_args()

    location_id = args.location_id
    LOG_FILE = args.log

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    wifi_health_data = get_wifi_health(location_id)
    if wifi_health_data:
        # Ausgabe in die Logdatei und auf stdout
        log.info(f"Wi-Fi health data: {wifi_health_data}")
        print(f"Wi-Fi health data: {wifi_health_data}")

if __name__ == "__main__":
    main()