#!/usr/bin/env python3
"""
Check_MK Special Agent for ExtremeCloud IQ Access Points

Queries the ExtremeCloud IQ API to monitor Access Points and their clients.
Outputs data in Check_MK piggyback format.

Usage:
    agent_extreme_cloud_iq --username USER --password PASS [--api-token TOKEN] [--debug]

Environment Variables:
    EXTREME_USERNAME - API username
    EXTREME_PASSWORD - API password  
    EXTREME_API_TOKEN - API token (alternative to username/password)
"""

import sys
import json
import argparse
import logging
import os
from typing import Dict, List, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

# API Configuration
API_BASE_URL = "https://api.extremecloudiq.com"
API_TIMEOUT = 30


class ExtremeCloudIQClient:
    """Client for ExtremeCloud IQ API"""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, 
                 api_token: Optional[str] = None, debug: bool = False):
        self.username = username
        self.password = password
        self.api_token = api_token
        self.access_token = None
        self.debug = debug
        
        # Setup logging
        log_level = logging.DEBUG if debug else logging.WARNING
        logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None, auth_required: bool = True) -> Any:
        """Make HTTP request to ExtremeCloud IQ API"""
        url = f"{API_BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication
        if auth_required and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        # Prepare request
        body = json.dumps(data).encode('utf-8') if data else None
        req = Request(url, data=body, headers=headers, method=method)
        
        self.logger.debug(f"{method} {url}")
        if data:
            self.logger.debug(f"Request body: {json.dumps(data, indent=2)}")
        
        try:
            with urlopen(req, timeout=API_TIMEOUT) as response:
                response_data = response.read().decode('utf-8')
                self.logger.debug(f"Response: {response_data[:500]}")
                return json.loads(response_data) if response_data else {}
        except HTTPError as e:
            error_msg = e.read().decode('utf-8')
            self.logger.error(f"HTTP Error {e.code}: {error_msg}")
            raise Exception(f"API request failed: {e.code} - {error_msg}")
        except URLError as e:
            self.logger.error(f"URL Error: {e.reason}")
            raise Exception(f"Connection failed: {e.reason}")
    
    def authenticate(self) -> bool:
        """Authenticate with ExtremeCloud IQ API"""
        if self.api_token:
            # Use provided API token directly
            self.access_token = self.api_token
            self.logger.info("Using provided API token")
            return True
        
        if not self.username or not self.password:
            raise ValueError("Username and password required for authentication")
        
        self.logger.info(f"Authenticating as {self.username}")
        
        try:
            response = self._make_request(
                "/login",
                method="POST",
                data={"username": self.username, "password": self.password},
                auth_required=False
            )
            
            self.access_token = response.get("access_token")
            if not self.access_token:
                raise Exception("No access token in response")
            
            self.logger.info("Authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices (Access Points)"""
        self.logger.info("Fetching devices...")
        
        try:
            # Get paginated device list
            all_devices = []
            page = 1
            page_size = 100
            
            while True:
                params = {
                    "page": page,
                    "limit": page_size,
                    "deviceTypes": "REAL"  # Only real devices, not simulated
                }
                
                response = self._make_request(f"/devices?{urlencode(params)}")
                
                # Handle both paginated and non-paginated responses
                if isinstance(response, dict) and "data" in response:
                    devices = response.get("data", [])
                    all_devices.extend(devices)
                    
                    # Check if there are more pages
                    pagination = response.get("pagination", {})
                    total = pagination.get("total", 0)
                    if len(all_devices) >= total or not devices:
                        break
                    page += 1
                else:
                    # Non-paginated response
                    all_devices = response if isinstance(response, list) else []
                    break
            
            # Filter only Access Points
            aps = [d for d in all_devices if d.get("device_function") == "AP"]
            self.logger.info(f"Found {len(aps)} Access Points")
            return aps
            
        except Exception as e:
            self.logger.error(f"Failed to get devices: {e}")
            return []
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get all connected clients"""
        self.logger.info("Fetching clients...")
        
        try:
            response = self._make_request("/clients")
            
            # Handle paginated response
            if isinstance(response, dict) and "data" in response:
                clients = response.get("data", [])
            else:
                clients = response if isinstance(response, list) else []
            
            self.logger.info(f"Found {len(clients)} clients")
            return clients
            
        except Exception as e:
            self.logger.error(f"Failed to get clients: {e}")
            return []


def output_check_mk_section(section_name: str, data: str):
    """Output Check_MK agent section"""
    print(f"<<<{section_name}>>>")
    print(data)


def output_piggyback_host(hostname: str):
    """Start piggyback output for specific host"""
    print(f"<<<<{hostname}>>>>")


def end_piggyback():
    """End piggyback output"""
    print("<<<<>>>>")


def format_ap_status(ap: Dict[str, Any]) -> str:
    """Format AP status for Check_MK"""
    # Extract key information
    serial = ap.get("serial_number", "unknown")
    hostname = ap.get("hostname", ap.get("host_name", serial))
    mac = ap.get("mac_address", "unknown")
    ip = ap.get("ip_address", "unknown")
    model = ap.get("product_type", "unknown")
    
    # Connection status
    connected = ap.get("connected", False)
    connection_state = ap.get("connection_state", "DISCONNECTED")
    
    # Software version
    software_version = ap.get("software_version", "unknown")
    
    # Location
    location = ap.get("location", {})
    site_name = location.get("site_name", "N/A") if isinstance(location, dict) else "N/A"
    
    # Build status line
    status = "1" if connected and connection_state == "CONNECTED" else "0"
    
    return f"{hostname}|{serial}|{mac}|{ip}|{model}|{status}|{connection_state}|{software_version}|{site_name}"


def format_ap_clients(ap: Dict[str, Any], all_clients: List[Dict[str, Any]]) -> str:
    """Format client count for specific AP"""
    ap_mac = ap.get("mac_address", "").lower()
    
    # Count clients connected to this AP
    ap_clients = [c for c in all_clients if c.get("ap_mac", "").lower() == ap_mac]
    
    client_count = len(ap_clients)
    
    # Count by radio (2.4 GHz vs 5 GHz)
    radio_2_4 = len([c for c in ap_clients if c.get("radio", "").startswith("wifi0")])
    radio_5 = len([c for c in ap_clients if c.get("radio", "").startswith("wifi1")])
    
    return f"{client_count}|{radio_2_4}|{radio_5}"


def format_ap_details(ap: Dict[str, Any]) -> str:
    """Format detailed AP information"""
    # CPU and Memory
    cpu_usage = ap.get("cpu_usage", 0)
    memory_usage = ap.get("memory_usage", 0)
    
    # Uptime in seconds
    uptime = ap.get("up_time", 0)
    
    # Power
    power_mode = ap.get("power_mode", "unknown")
    poe_power = ap.get("poe_power", 0)
    
    return f"{cpu_usage}|{memory_usage}|{uptime}|{power_mode}|{poe_power}"


def main():
    parser = argparse.ArgumentParser(
        description="Check_MK Special Agent for ExtremeCloud IQ Access Points"
    )
    parser.add_argument("--username", help="API Username", 
                       default=os.environ.get("EXTREME_USERNAME"))
    parser.add_argument("--password", help="API Password",
                       default=os.environ.get("EXTREME_PASSWORD"))
    parser.add_argument("--api-token", help="API Token (alternative to username/password)",
                       default=os.environ.get("EXTREME_API_TOKEN"))
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    # Validate credentials
    if not args.api_token and (not args.username or not args.password):
        sys.stderr.write("Error: Either --api-token or --username and --password required\n")
        sys.exit(2)
    
    try:
        # Initialize client
        client = ExtremeCloudIQClient(
            username=args.username,
            password=args.password,
            api_token=args.api_token,
            debug=args.debug
        )
        
        # Authenticate
        client.authenticate()
        
        # Get data
        devices = client.get_devices()
        clients = client.get_clients()
        
        if not devices:
            sys.stderr.write("Warning: No Access Points found\n")
        
        # Output data for each AP as piggyback host
        for ap in devices:
            hostname = ap.get("hostname", ap.get("host_name", ap.get("serial_number", "unknown")))
            
            # Start piggyback for this AP
            output_piggyback_host(hostname)
            
            # AP Status Section
            output_check_mk_section("extreme_ap_status", format_ap_status(ap))
            
            # AP Clients Section
            output_check_mk_section("extreme_ap_clients", format_ap_clients(ap, clients))
            
            # AP Details Section
            output_check_mk_section("extreme_ap_details", format_ap_details(ap))
            
            # End piggyback
            end_piggyback()
        
        # Output summary on main host
        output_check_mk_section("extreme_summary", 
                               f"access_points={len(devices)}|total_clients={len(clients)}")
        
        sys.exit(0)
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()