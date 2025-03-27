#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# License: GNU General Public License v2
#
# Author: bh2005
# URL  : https://github.com/bh2005
# Date : 2024-03-01
#
# This script retrieves the client list from ExtremeCloud IQ via the API and outputs it to JSON and CSV files.
# It handles pagination to retrieve all available data.
#
# Release notes - init release

import requests
import json
import os
import logging
import argparse
import csv
import time
from tqdm import tqdm

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "client_list.log"
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

def get_client_list(views, page=1, limit=100, sort=None, dir=None, where=None):
    global API_SECRET  # Access the global API_SECRET variable
    headers = {
        "Authorization": f"Bearer {API_SECRET}",
        "Content-Type": "application/json",
    }
    params = {
        "views": views,
        "page": page,
        "limit": limit,
        "sort": sort,
        "dir": dir,
        "where": where,
    }

    try:
        response = requests.get(f"{XIQ_BASE_URL}/clients", headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()
        log.info(f"Client list retrieved successfully with parameters: {params}")
        return response_json
    except requests.exceptions.RequestException as e:
        log.error(f"Error retrieving client list with parameters: {params}: {e}")
        print(f"Error retrieving client list with parameters: {params}: {e}")
        # Check if the error is due to an expired token, and renew it.
        if response.status_code == 401:  # Assuming 401 is unauthorized
            log.warning("Token expired, attempting to renew")
            print("Token expired, attempting to renew")
            if renew_token():
                log.info("Token renewal successful, retrying request")
                print("Token renewal successful, retrying request")
                # Retry the request after token renewal
                return get_client_list(views, page, limit, sort, dir, where)
            else:
                log.error("Token renewal failed. Request not retried.")
                print("Token renewal failed. Request not retried.")
        else:
            log.error(f"Error retrieving client list. Error Code: {response.status_code}")
            print(f"Error retrieving client list. Error Code: {response.status_code}")
        return None

def fetch_all_clients(views, page_size=100, sort=None, dir=None, where=None):
    all_clients = []
    page = 1
    pbar = tqdm(desc="Fetching clients", unit="page")

    while True:
        clients_data = get_client_list(views, page, page_size, sort, dir, where)
        if not clients_data or not clients_data.get('data'):
            break

        all_clients.extend(clients_data['data'])
        pbar.update(1)

        if len(clients_data['data']) < page_size:
            break

        page += 1
        time.sleep(3)  # Pause for 3 seconds before requesting the next page

    pbar.close()
    log.info(f"Found {len(all_clients)} clients across {page - 1} pages.")
    return all_clients

def write_json(data, filename="clients.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    log.info(f"Client list written to {filename}")

def write_csv(data, filename="clients.csv"):
    if not data:
        log.warning("No client data to write to CSV.")
        return

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        header = data[0].keys()
        writer.writerow(header)
        for client in data:
            writer.writerow(client.values())
    log.info(f"Client list written to {filename}")
  
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

    parser = argparse.ArgumentParser(description="Retrieves the client list from ExtremeCloud IQ via the API and outputs it to JSON and CSV files.")
    parser.add_argument("views", choices=['basic', 'detail', 'status', 'metrics', 'location', 'full'], default='basic', help="The views parameter for the API request (basic, detail, status, metrics, location, full).")
    parser.add_argument("-l", "--log", help="Path to the log file.", default="client_list.log")
    parser.add_argument("--page", type=str, default="1", help="Page number for pagination or 'all' to retrieve all pages.")
    parser.add_argument("--page_size", type=int, default=100, help="Number of items per page.")
    parser.add_argument("--sort", help="Field to sort by.")
    parser.add_argument("--dir", choices=["asc", "desc"], help="Sort direction (asc or desc).")
    parser.add_argument("--where", help="Filter criteria (e.g., 'name=test').")

    # Beispiele in die Hilfemeldung einfügen
    parser.epilog = """
    Examples:
        python get_client_list.py basic
        python get_client_list.py detail --page all -l my_client_list.log
        python get_client_list.py detail --page_size 50 --sort name --dir asc --where 'name=test'
    """

    args = parser.parse_args()

    views = args.views
    LOG_FILE = args.log
    page = args.page
    page_size = args.page_size
    sort = args.sort
    dir = args.dir
    where = args.where

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    if page.lower() == "all":
        client_data = fetch_all_clients(views, page_size, sort, dir, where)
    else:
        client_data = get_client_list(views, int(page), page_size, sort, dir, where)

    if client_data:
        write_json(client_data, "all_clients.json")
        write_csv(client_data, "all_clients.csv")

if __name__ == "__main__":
    main()
