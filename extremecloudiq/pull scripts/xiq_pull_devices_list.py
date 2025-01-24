#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from tqdm import tqdm  # Import tqdm for progress bar
###################################################
#     ToDo`s
# - secure auth
# - reneval of token
# - 
#
####################################################

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

# Configure logging
LOG_FILE = "xiq_api.log"  # Log file
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def renew_token():   # automatischen for renew the API token 
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

def make_api_request(url, headers, max_retries=1):
    # Make API request with automatic token renewal on unauthorized access
    global API_SECRET
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:  # Unauthorized - token might be expired
                if attempt < max_retries:
                    log.info("Token appears to be expired, attempting renewal...")
                    new_token = renew_token()
                    if new_token:
                        API_SECRET = new_token
                        headers["Authorization"] = f"Bearer {new_token}"
                        continue
            
            return response

        except requests.exceptions.RequestException as e:
            log.error(f"API request failed: {str(e)}")
            raise

    return response

def get_devices(views, debug):
    if not API_SECRET:
        log.error("API_SECRET environment variable not set, attempting to generate new token.")
        new_token = renew_token()
        if not new_token:
            return 1
        global API_SECRET
        API_SECRET = new_token

    page = 1
    page_size = 100
    all_devices = []  # Initialize as an empty list

    while True:
        try:
            response = make_api_request(
                f"{XIQ_BASE_URL}/devices?page={page}&limit={page_size}&views={views}",
                headers={"Authorization": f"Bearer {API_SECRET}"}
            )

            if debug:
                # Print response to stdout for debugging
                log.debug(f"DEBUG: Raw API response for page {page}:")
                log.debug(response.text)

            if response.status_code != 200:
                log.error(f"Error: API request failed with HTTP status {response.status_code}.")
                log.error(response.json())  # Print the error response for debugging
                break

            # Save the raw response for each page
            with open(f"raw_devices_page_{page}.json", 'w') as f:
                f.write(response.text)

            # Extract devices from the response
            devices = response.json().get('data', [])
            if not devices:
                log.info(f"No devices found on page {page}, stopping.")
                break

            # Append devices to the all_devices list
            all_devices.extend(devices)

            # If less than 100 devices are returned, stop fetching more pages
            if len(devices) < page_size:
                break

            page += 1
            # Pause for 3 seconds before requesting the next page
            time.sleep(3)

        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
            return 1

    # Write all devices data to devices.json
    with open('devices.json', 'w') as f:
        json.dump(all_devices, f, indent=2)

    log.info("Devices data has been written to devices.json (formatted with json).")

def combine_json_files():
    output_file = "output_extreme_api.json"
    all_data = []

    for file_name in tqdm(glob.glob("raw_devices_page_*.json"), desc="Combining JSON files", unit="file"):
        with open(file_name, 'r') as f:
            data = json.load(f)
            all_data.extend(data.get('data', []))

    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    log.info(f"All raw JSON files have been combined into {output_file}.")

def format_mac_address(mac):
    if mac and len(mac) == 12:
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    return mac

def calculate_uptime(timestamp_ms):
    """Calculates the uptime between a given timestamp and the current time.

    Args:
        timestamp_ms: The timestamp in milliseconds.

    Returns:
        A string in the format "days, hours:minutes:seconds" or None in case of an error.
    """
    if not isinstance(timestamp_ms, (int, float)):
        return None

    try:
        current_time_ms = int(time.time() * 1000)
        uptime_ms = current_time_ms - int(timestamp_ms)

        if uptime_ms < 0:
            return "Timestamp is in the future"

        uptime_delta = datetime.timedelta(milliseconds=uptime_ms)
        days = uptime_delta.days
        if days > 2000:
             return "offline"
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} days, {hours:02}:{minutes:02}:{seconds:02}"
    except OverflowError:
        return "Uptime too large for timedelta"
    except TypeError:
        return None

def convert_json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    with open(csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write the header row
        csvwriter.writerow([
            "id",
            "create_time",
            "update_time",
            "serial_number",
            "mac_address",
            "device_function",
            "product_type",
            "hostname",
            "ip_address",
            "software_version",
            "device_admin_state",
            "connected",
            "last_connect_time",
            "network_policy_name",
            "network_policy_id",
            "primary_ntp_server_address",
            "primary_dns_server_address",
            "subnet_mask",
            "default_gateway",
            "ipv6_address",
            "ipv6_netmask",
            "simulated",
            "display_version",
            "location_id",
            "org_id", 
            "org_name", 
            "city_id", 
            "city_name", 
            "building_id", 
            "building_name", 
            "floor_id", 
            "floor_name",
            "country_code",
            "description",
            "remote_port_id", 
            "remote_system_id", 
            "remote_system_name", 
            "local_interface",
            "system_up_time",
            "config_mismatch",
            "managed_by",
            "thread0_eui64",
            "thread0_ext_mac"
        ])
        
        # Write the data rows
        for device in tqdm(data, desc="Converting JSON to CSV", unit="device"):
            
            locations = device.get("locations", [])
            
            org_id = org_name = city_id = city_name = building_id = building_name = floor_id = floor_name = ""
            
            if len(locations) > 0:
                org_id = locations[0].get("id")
                org_name = locations[0].get("name")
                
                if len(locations) > 1:
                    city_id = locations[1].get("id")
                    city_name = locations[1].get("name")
                    
                    if len(locations) > 2:
                        building_id = locations[2].get("id")
                        building_name = locations[2].get("name")
                        
                        if len(locations) > 3:
                            floor_id = locations[3].get("id")
                            floor_name = locations[3].get("name")

            
            lldp_cdp_infos = device.get("lldp_cdp_infos", [])
            
            remote_port_id = remote_system_id = remote_system_name = local_interface = ""
            
            if len(lldp_cdp_infos) > 0:
                remote_port_id = lldp_cdp_infos[0].get("port_id")
                remote_system_id = lldp_cdp_infos[0].get("system_id")
                remote_system_name = lldp_cdp_infos[0].get("system_name")
                local_interface = lldp_cdp_infos[0].get("interface_name")

            
            csvwriter.writerow([
                device.get("id"),
                device.get("create_time"),
                device.get("update_time"),
                device.get("serial_number"),
                format_mac_address(device.get("mac_address")),
                device.get("device_function"),
                device.get("product_type"),
                device.get("hostname"),
                device.get("ip_address"),
                device.get("software_version"),
                device.get("device_admin_state"),
                device.get("connected"),
                device.get("last_connect_time"),
                device.get("network_policy_name"),
                device.get("network_policy_id"),
                device.get("primary_ntp_server_address"),
                device.get("primary_dns_server_address"),
                device.get("subnet_mask"),
                device.get("default_gateway"),
                device.get("ipv6_address"),
                device.get("ipv6_netmask"),
                device.get("simulated"),
                device.get("display_version"),
                device.get("location_id"),
                org_id,
                org_name,
                city_id,
                city_name,
                building_id,
                building_name,
                floor_id,
                floor_name,
                device.get("country_code"),
                device.get("description"),
                remote_port_id,
                remote_system_id,
                remote_system_name,
                local_interface,
                calculate_uptime(device.get("system_up_time")),
                device.get("config_mismatch"),
                device.get("managed_by"),
                device.get("thread0_eui64"),
                device.get("thread0_ext_mac")
            ])

    log.info(f"JSON data has been converted to CSV and saved as {csv_file}.")

def delete_raw_files():
    raw_files = glob.glob("raw_devices_page_*.json")
    for file_name in raw_files:
        os.remove(file_name)
    log.info(f"Deleted {len(raw_files)} raw JSON files.")

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