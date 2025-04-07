#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import logging
import sys
sys.path.append('../modules')
import xiq_api_auth

XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "get_devices_list.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def get_device_list(api_token, page=1, limit=100, sort=None, dir=None, where=None):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }
    params = {
        'page': page,
        'limit': limit,
        'sort': sort,
        'dir': dir,
        'where': where
    }
    url = f'{XIQ_BASE_URL}/devices'

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving device list: {e}")
        print(f"Error retrieving device list: {e}")
        return None

def main():
    api_token = xiq_api_auth.renew_token()

    if api_token:
        parser = argparse.ArgumentParser(description="Retrieves the device list from ExtremeCloud IQ.")
        parser.add_argument("--page", type=int, default=1, help="Page number")
        parser.add_argument("--limit", type=int, default=100, help="Items per page")
        parser.add_argument("--sort", help="Sort field")
        parser.add_argument("--dir", help="Sort direction (asc/desc)")
        parser.add_argument("--where", help="Filter criteria")
        args = parser.parse_args()

        device_data = get_device_list(api_token, args.page, args.limit, args.sort, args.dir, args.where)

        if device_data:
            print(json.dumps(device_data, indent=4))
        else:
            log.error("Failed to retrieve device list data.")
            print("Failed to retrieve device list data.")
    else:
        log.error("Could not retrieve API token. Aborting.")
        print("Could not retrieve API token. Aborting.")

if __name__ == "__main__":
    import argparse
    main()