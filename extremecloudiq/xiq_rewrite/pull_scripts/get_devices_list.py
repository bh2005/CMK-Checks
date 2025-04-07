#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# License: GNU General Public License v2
#
# Author: bh2005
# URL  : https://github.com/bh2005
# Date : 2024-04-02
#
# This script retrieves the device list from ExtremeCloud IQ via the API and outputs it to JSON and CSV files.
# It handles pagination to retrieve all available data.
#
# Release notes - init release
# adding auth module

import requests
import json
import os
import logging
import argparse
import csv
import time
from tqdm import tqdm
import sys
sys.path.append('..')
import modules.xiq_api_auth  # Importieren Sie das Modul aus dem Unterverzeichnis

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "device_list.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def get_device_list(page=1, limit=100, sort=None, dir=None, where=None):
    global API_SECRET  # Access the global API_SECRET variable
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }
    params = {
        "page": page,
        "limit": limit,
        "sort": sort,
        "dir": dir,
        "where": where,
    }

    try:
        response = requests.get(f"{XIQ_BASE_URL}/devices", headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()
        log.info(f"Device list retrieved successfully with parameters: {params}")
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving device list with parameters: {params}: {e}")
        print(f"Error retrieving device list with parameters: {params}: {e}")
        # Check if the error is due to an expired token, and renew it.
        if response.status_code == 401:  # Assuming 401 is unauthorized
            log.warning("Token expired, attempting to renew")
            print("Token expired, attempting to renew")
            if modules.xiq_api_auth.renew_token(): # nutzt das modul aus dem Unterverzeichnis
                log.info("Token renewal successful, retrying request")
                print("Token renewal successful, retrying request")
                # Retry the request after token renewal
                return get_device_list(page, limit, sort, dir, where)
            else:
                log.error("Token renewal failed. Request not retried.")
                print("Token renewal failed. Request not retried.")
        else:
            log.error(f"Error retrieving device list. Error Code: {response.status_code}")
            print(f"Error retrieving device list. Error Code: {response.status_code}")
        return None

def fetch_all_devices(page_size=100, sort=None, dir=None, where=None):
    all_devices = []
    page = 1
    pbar = tqdm(desc="Fetching devices", unit="page")

    while True:
        devices_data = get_device_list(page, page_size, sort, dir, where)
        if not devices_data or not devices_data.get('data'):
            break

        all_devices.extend(devices_data['data'])
        pbar.update(1)

        if len(devices_data['data']) < page_size:
            break

        page += 1
        time.sleep(3)  # Pause for 3 seconds before requesting the next page

    pbar.close()
    log.info(f"Found {len(all_devices)} devices across {page - 1} pages.")
    return all_devices

def write_json(data, filename="devices.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    log.info(f"Device list written to {filename}")

def write_csv(data, filename="devices.csv"):
    if not data:
        log.warning("No device data to write to CSV.")
        return

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        header = data[0].keys()
        writer.writerow(header)
        for device in data:
            writer.writerow(device.values())
    log.info(f"Device list written to {filename}")

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

    parser = argparse.ArgumentParser(description="Retrieves the device list from ExtremeCloud IQ via the API and outputs it to JSON and CSV files.")
    parser.add_argument("-l", "--log", help="Path to the log file.", default="device_list.log")
    parser.add_argument("--page", type=str, default="1", help="Page number for pagination or 'all' to retrieve all pages.")
    parser.add_argument("--page_size", type=int, default=100, help="Number of items per page.")
    parser.add_argument("--sort", help="Field to sort by.")
    parser.add_argument("--dir", choices=["asc", "desc"], help="Sort direction (asc or desc).")
    parser.add_argument("--where", help="Filter criteria (e.g., 'name=test').")

    # Beispiele in die Hilfemeldung einfügen
    parser.epilog = """
    Examples:
        python xiq_pull_devices_list.py
        python xiq_pull_devices_list.py --page all -l my_device_list.log
        python xiq_pull_devices_list.py --page_size 50 --sort name --dir asc --where 'name=test'
    """

    args = parser.parse_args()

    LOG_FILE = args.log
    page = args.page
    page_size = args.page_size
    sort = args.sort
    dir = args.dir
    where = args.where

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    if page.lower() == "all":
        device_data = fetch_all_devices(page_size, sort, dir, where)
    else:
        device_data = get_device_list(int(page), page_size, sort, dir, where)

    if device_data:
        write_json(device_data, "devices.json")
        write_csv(device_data, "devices.csv")

if __name__ == "__main__":
    main()