#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import argparse

def get_client_list(xiq_base_url, username, password, views="basic", page=1, limit=100, sort=None, dir=None, where=None):
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
            "views": views,
            "page": page,
            "limit": limit,
            "sort": sort,
            "dir": dir,
            "where": where,
        }

        response = requests.get(f"{xiq_base_url}/clients", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving client list: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Retrieves the client list from ExtremeCloud IQ via the API.")
    parser.add_argument("--xiq_base_url", required=True, help="ExtremeCloud IQ Base URL")
    parser.add_argument("--username", required=True, help="Username for ExtremeCloud IQ API")
    parser.add_argument("--password", required=True, help="Password for ExtremeCloud IQ API")
    parser.add_argument("--views", default="basic", help="View type (basic, detail, etc.)")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--limit", type=int, default=100, help="Items per page")
    parser.add_argument("--sort", help="Sort field")
    parser.add_argument("--dir", help="Sort direction (asc/desc)")
    parser.add_argument("--where", help="Filter criteria")
    args = parser.parse_args()

    client_data = get_client_list(args.xiq_base_url, args.username, args.password, args.views, args.page, args.limit, args.sort, args.dir, args.where)

    if client_data:
        print("<<<xiq_client_list:sep(0)>>>")
        print(json.dumps(client_data))

if __name__ == "__main__":
    main()