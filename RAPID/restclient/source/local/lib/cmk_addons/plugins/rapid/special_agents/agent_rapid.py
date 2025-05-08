#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Special Agent for RAPID Server based on REST API
# (c) 2025 Your Name <your.email@example.com>
# License: GNU General Public License v2
#
# Inspired by Redfish Special Agent by Andreas Doehler (Yogibaer75)
# and restclient3.py by bh2005

import sys
import argparse
import json
import logging
import urllib3
import requests
from typing import Dict, Any, Optional
from cmk.special_agents.utils import vcrtrace

# Suppress SSL warnings if verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_rapid")

class RapidAPIClient:
    """Client for interacting with RAPID Server REST API"""
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = True):
        self.base_url = f"https://{host}/rest/v1"
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.auth = (username, password)

    def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Perform a GET request to the RAPID API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, verify=self.verify_ssl, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def get_system(self) -> Optional[Dict[str, Any]]:
        """Fetch system information"""
        return self.get("system")

    def get_thermal(self) -> Optional[Dict[str, Any]]:
        """Fetch thermal information (fans, temperatures)"""
        return self.get("thermal")

    def get_power(self) -> Optional[Dict[str, Any]]:
        """Fetch power supply information"""
        return self.get("power")

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Special Agent for RAPID Server")
    parser.add_argument("--host", required=True, help="RAPID Server hostname or IP")
    parser.add_argument("--username", required=True, help="API username")
    parser.add_argument("--password", required=True, help="API password")
    parser.add_argument("--no-cert-check", action="store_true", help="Disable SSL verification")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()

@vcrtrace
def main() -> None:
    """Main function for the RAPID special agent"""
    args = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Initialize API client
    client = RapidAPIClient(
        host=args.host,
        username=args.username,
        password=args.password,
        verify_ssl=not args.no_cert_check
    )

    # Collect data
    sections = {
        "rapid_system": client.get_system(),
        "rapid_thermal": client.get_thermal(),
        "rapid_power": client.get_power()
    }

    # Output data in Checkmk agent format
    for section_name, data in sections.items():
        if data:
            print(f"<<<{section_name}>>>")
            print(json.dumps(data, indent=2))
        else:
            logger.warning(f"No data for section {section_name}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        sys.exit(1)
