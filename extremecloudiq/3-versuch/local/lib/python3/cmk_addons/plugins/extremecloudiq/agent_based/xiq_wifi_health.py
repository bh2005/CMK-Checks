#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import argparse

def get_wifi_health(xiq_base_url, username, password, location_id):
    url = f"{xiq_base_url}/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        api_key = response.json().get("access_token")

        if not api_key:
            print("Error: Could not extract API key from the response")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        url = f"{xiq_base_url}/locations/{location_id}/wifi-health"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving Wi-Fi health: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Retrieves Wi-Fi overall health for a given location from ExtremeCloud IQ.")
    parser.add_argument("--xiq_base_url", required=True, help="ExtremeCloud IQ Base URL")
    parser.add_argument("--username", required=True, help="Username for ExtremeCloud IQ API")
    parser.add_argument("--password", required=True, help="Password for ExtremeCloud IQ API")
    parser.add_argument("location_id", help="The location ID.")
    args = parser.parse_args()

    wifi_health_data = get_wifi_health(args.xiq_base_url, args.username, args.password, args.location_id)

    if wifi_health_data:
        print("<<<xiq_wifi_health:sep(0)>>>")
        print(json.dumps(wifi_health_data))

if __name__ == "__main__":
    main()