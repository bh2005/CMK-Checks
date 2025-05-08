#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Special Agent for Kisters REST API Check
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Based on https://github.com/bh2005/CMK-Checks/blob/master/kisters/rest-check.py
# and https://docs.checkmk.com/latest/de/devel_special_agents.html

import argparse
import sys
import json
import time
import requests
import cmk.utils.password_store

def parse_arguments(args=None):
    """Parse command line arguments."""
    if args is None:
        cmk.utils.password_store.replace_passwords()
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Checkmk Special Agent for Kisters REST API")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", required=True, help="JSON configuration (URLs, methods, auth, pvId)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    return parser.parse_args(args)

def main(args=None):
    """Main function for the Kisters REST API Special Agent."""
    args = parse_arguments(args)

    try:
        # Parse JSON configuration
        config = json.loads(args.config)
        if not isinstance(config, list):
            raise ValueError("Configuration must be a list of entries")

        print("<<<kisters_rest_check>>>")
        for entry in config:
            instance = entry.get("instance", entry["url"])
            url = entry["url"]
            method = entry.get("method", "GET")
            data = entry.get("data")
            user = entry.get("user")
            password_id = entry.get("password_id")
            pvId = entry.get("pvId")
            password = cmk.utils.password_store.lookup(password_id) if password_id else None

            # Add pvId as query parameter if provided
            if pvId:
                url = f"{url}?pvId={pvId}" if "?" not in url else f"{url}&pvId={pvId}"

            try:
                start_time = time.time()
                if user and password:
                    response = requests.request(
                        method, url, timeout=args.timeout, auth=(user, password), data=data
                    )
                else:
                    response = requests.request(method, url, timeout=args.timeout, data=data)
                response_time = time.time() - start_time

                # Output in Checkmk format
                print(f"instance: {instance}")
                print(f"status_code: {response.status_code}")
                print(f"response_time: {response_time:.3f}")
                if pvId:
                    print(f"pvId: {pvId}")
                print("---")  # Separator for multiple instances
            except requests.exceptions.RequestException as e:
                print(f"instance: {instance}")
                print(f"status_code: -1")
                print(f"error: {str(e)}")
                if pvId:
                    print(f"pvId: {pvId}")
                print("---")
                if args.debug:
                    raise

        return 0
    except Exception as e:
        if args.debug:
            raise
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())