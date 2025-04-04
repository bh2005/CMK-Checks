#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import argparse

def get_device_list(xiq_base_url, username, password, page=1, limit=100, sort=None, dir=None, where=None):
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
        params = {
            "page": page,
            "limit": limit,
            "sort": sort,
            "dir": dir,
            "where": where,
        }

        response = requests.get(f"{xiq_base_url}/devices", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving device list: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Retrieves the device list from ExtremeCloud IQ.")
    parser.add_argument("--xiq_base_url", required=True, help="ExtremeCloud IQ Base URL")
    parser.add_argument("--username", required=True, help="Username for ExtremeCloud IQ API")
    parser.add_argument("--password", required=True, help="Password for ExtremeCloud IQ API")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--limit", type=int, default=100, help="Items per page")
    parser.add_argument("--sort", help="Sort field")
    parser.add_argument("--dir", help="Sort direction (asc/desc)")
    parser.add_argument("--where", help="Filter criteria")
    args = parser.parse_args()

    device_data = get_device_list(args.xiq_base_url, args.username, args.password, args.page, args.limit, args.sort, args.dir, args.where)

    if device_data:
        print("<<<xiq_device_list:sep(0)>>>")
        print(json.dumps(device_data))

if __name__ == "__main__":
    main()