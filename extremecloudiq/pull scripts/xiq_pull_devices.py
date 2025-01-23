#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
import json
import glob
import csv
import sys
import argparse
from tqdm import tqdm  # Import tqdm for progress bar

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

def get_devices(views, debug):
    if not API_SECRET:
        print("Error: API_SECRET environment variable not set.", file=sys.stderr)
        return 1

    page = 1
    page_size = 100
    all_devices = []  # Initialize as an empty list

    while True:
        # Get response from API for the current page
        response = requests.get(
            f"{XIQ_BASE_URL}/devices?page={page}&limit={page_size}&views={views}",
            headers={"Authorization": f"Bearer {API_SECRET}"}
        )

        if debug:
            # Print response to stdout for debugging
            print(f"DEBUG: Raw API response for page {page}:")
            print(response.text)

        if response.status_code != 200:
            print(f"Error: API request failed with HTTP status {response.status_code}.", file=sys.stderr)
            print(response.json(), file=sys.stderr)  # Print the error response for debugging
            break

        # Save the raw response for each page to a separate file
        with open(f"raw_devices_page_{page}.json", 'w') as f:
            f.write(response.text)

        # Extract devices from the response
        devices = response.json().get('data', [])

        if not devices:
            print(f"No devices found on page {page}, stopping.")
            break

        # Append devices to the all_devices list
        all_devices.extend(devices)

        # If less than 100 devices are returned, stop fetching more pages
        if len(devices) < page_size:
            break

        page += 1

        # Pause for 3 seconds before requesting the next page
        time.sleep(3)

    # Write all devices data to devices.json (after collecting from all pages)
    with open('devices.json', 'w') as f:
        json.dump(all_devices, f, indent=2)

    print("Devices data has been written to devices.json (formatted with json).")

def combine_json_files():
    output_file = "output_extreme_api.json"
    all_data = []

    for file_name in tqdm(glob.glob("raw_devices_page_*.json"), desc="Combining JSON files", unit="file"):
        with open(file_name, 'r') as f:
            data = json.load(f)
            all_data.extend(data.get('data', []))

    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"All raw JSON files have been combined into {output_file}.")

def format_mac_address(mac):
    if mac and len(mac) == 12:
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    return mac

def format_uptime(uptime_unix):
    """Formats the uptime based on the UNIX timestamp.

    Args:
        uptime_unix: The system uptime as a UNIX timestamp.

    Returns:
        The formatted uptime string.
    """
    # Get the current time as a UNIX timestamp
    current_time = int(time.time())

    # Calculate the uptime in seconds
    uptime_s = current_time - uptime_unix

    # Calculate days, hours, minutes, and seconds
    uptime_m = uptime_s // 60
    uptime_h = uptime_m // 60
    uptime_d = uptime_h // 24

    s = uptime_s % 60
    m = uptime_m % 60
    h = uptime_h % 24

    return f"{uptime_d} days, {h} hours, {m} minutes, {s} seconds"

def convert_json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f):
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
                format_uptime(device.get("system_up_time")),
                device.get("config_mismatch"),
                device.get("managed_by"),
                device.get("thread0_eui64"),
                device.get("thread0_ext_mac")
            ])

    print(f"JSON data has been converted to CSV and saved as {csv_file}.")

def delete_raw_files():
    raw_files = glob.glob("raw_devices_page_*.json")
    for file_name in raw_files:
        os.remove(file_name)
    print(f"Deleted {len(raw_files)} raw JSON files.")

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