#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import logging
import modules.xiq_api_auth  # Importieren Sie das Modul aus dem Unterverzeichnis

# API Configuration (use environment variables)
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "get_dashboard_criteria.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def get_dashboard_criteria(api_token):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }
    url = f'{XIQ_BASE_URL}/dashboard/wireless/dashboard/criteria'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving dashboard criteria: {e}")
        print(f"Error retrieving dashboard criteria: {e}")
        return None

def main():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    api_token = modules.xiq_api_auth.get_xiq_api_token()

    if api_token:
        criteria_data = get_dashboard_criteria(api_token)
        if criteria_data:
            print(json.dumps(criteria_data, indent=4))
        else:
            log.error("Failed to retrieve dashboard criteria.")
            print("Failed to retrieve dashboard criteria.")
    else:
        log.error("Could not retrieve API token. Aborting.")
        print("Could not retrieve API token. Aborting.")

if __name__ == "__main__":
    main()
