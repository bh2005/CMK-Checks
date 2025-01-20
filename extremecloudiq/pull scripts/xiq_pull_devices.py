#!/usr/bin/env python3

import os
import time
import requests
import json
import glob

# API Configuration (use environment variables)
API_SECRET = os.getenv('XIQ_API_SECRET')
XIQ_BASE_URL = 'https://api.extremecloudiq.com'

def get_devices():
    if not API_SECRET:
        print("Error: API_SECRET environment variable not set.", file=sys.stderr)
        return 1

    page = 1
    page_size = 100
    all_devices = []  # Initialize as an empty list
    max_devices = 1000
    total_devices = 0
    total_pages = 9  # Set to 9 pages

    for page in range(1, total_pages + 1):
        # Get response from API for the current page
        response = requests.get(
            f"{XIQ_BASE_URL}/devices?page={page}&limit={page_size}&connected=true&adminStates=MANAGED&views=BASIC&fields=MANAGED_BY&deviceTypes=REAL&nullField=LOCATION_ID&async=false",
            headers={"Authorization": f"Bearer {API_SECRET}"}
        )

        # Print response to stdout for debugging
        print(f"DEBUG: Raw API response for page {page}:")
        print(response.text)

        if response.status_code != 200:
            print(f"Error: API request failed with HTTP status {response.status_code}.", file=sys.stderr)
            print(response.json(), file=sys.stderr)  # Print the error response for debugging
            continue

        # Save the raw response for each page to a separate file
        with open(f"raw_devices_page_{page}.json", 'w') as f:
            f.write(response.text)

        # Extract devices from the response
        devices = response.json().get('data', [])

        if not devices:
            print(f"No devices found on page {page}, skipping.")
            continue

        # Append devices to the all_devices list
        all_devices.extend(devices)

        total_devices += len(devices)

        # If we reach the max number of devices, stop fetching more
        if total_devices >= max_devices:
            break

        # Pause for 3 seconds before requesting the next page
        time.sleep(3)

    # Write all devices data to devices.json (after collecting from all pages)
    with open('devices.json', 'w') as f:
        json.dump(all_devices, f, indent=2)

    print("Devices data has been written to devices.json (formatted with json).")

def combine_json_files():
    output_file = "output_extreme_api.json"
    all_data = []

    for file_name in glob.glob("raw_devices_page_*.json"):
        with open(file_name, 'r') as f:
            data = json.load(f)
            all_data.extend(data.get('data', []))

    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"All raw JSON files have been combined into {output_file}.")

if __name__ == "__main__":
    get_devices()
    combine_json_files()
