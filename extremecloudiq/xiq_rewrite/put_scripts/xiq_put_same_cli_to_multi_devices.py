#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# License: GNU General Public License v2
#
# Author: bh2005
# URL  : https://github.com/bh2005
# Date : 2024-03-01
#
# This script sends the same CLI command to multiple devices in ExtremeCloud IQ via the API.
# adding auth module support
#

import requests
import json
import os
import logging
import argparse
import time
import modules.xiq_api_auth  # Importieren Sie das Modul aus dem Unterverzeichnis

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "send_cli.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def send_cli_command(device_ids, cli_command):
    global API_SECRET  # Access the global API_SECRET variable
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }
    url = f"{XIQ_BASE_URL}/devices/cli"
    data = {
        "deviceIds": device_ids,
        "cli": cli_command,
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        log.info(f"CLI command sent successfully to devices: {device_ids}")
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error sending CLI command to devices: {device_ids}: {e}")
        print(f"Error sending CLI command to devices: {device_ids}: {e}")
        # Check if the error is due to an expired token, and renew it.
        if response.status_code == 401:  # Assuming 401 is unauthorized
            log.warning("Token expired, attempting to renew")
            print("Token expired, attempting to renew")
            if modules.xiq_api_auth.renew_token(): # nutzt das modul aus dem Unterverzeichnis
                log.info("Token renewal successful, retrying request")
                print("Token renewal successful, retrying request")
                # Retry the request after token renewal
                return send_cli_command(device_ids, cli_command)
            else:
                log.error("Token renewal failed. Request not retried.")
                print("Token renewal failed. Request not retried.")
        else:
            log.error(f"Error sending CLI command. Error Code: {response.status_code}")
            print(f"Error sending CLI command. Error Code: {response.status_code}")
        return None

def main():
    # Check if API_SECRET is available, otherwise renew token
    global API_SECRET  # Access the global API_SECRET variable
    if not API_SECRET:
        log.info("API Secret not found, attempting to renew")
        print("API Secret not found, attempting to renew")
        if modules.xiq_api_auth.renew_token(): # nutzt das modul aus dem Unterverzeichnis
            log.info("Token renewed successfully, continuing")
            print("Token renewed successfully, continuing")
        else:
            log.error("Token renewal failed, exiting.")
            print("Token renewal failed, exiting.")
            return

    parser = argparse.ArgumentParser(description="Sends the same CLI command to multiple devices in ExtremeCloud IQ via the API.")
    parser.add_argument("device_ids", nargs="+", help="List of device IDs to send the CLI command to.")
    parser.add_argument("cli_command", help="The CLI command to send.")
    parser.add_argument("-l", "--log", help="Path to the log file.", default="send_cli.log")

    args = parser.parse_args()

    device_ids = args.device_ids
    cli_command = args.cli_command
    LOG_FILE = args.log

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    result = send_cli_command(device_ids, cli_command)
    if result:
        log.info(f"CLI command sent successfully. Result: {result}")
        print(f"CLI command sent successfully. Result: {result}")

if __name__ == "__main__":
    main()