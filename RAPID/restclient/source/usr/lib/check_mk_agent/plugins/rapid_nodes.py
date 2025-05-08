#!/usr/bin/env python3
# Copyright (C) 2025 - License: GNU General Public License v2
# Check_MK Check Plugin for RAPID REST API Node Status (based on Redfish agent)

from cmk.base.check_api import (
    check_levels,
    LegacyCheckDefinition,
    get_value_store,
)
from cmk.base.config import check_info
import requests
import logging
import json
from typing import Optional, Dict, Any
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Node status enum from restclient script
class NodeStatus_e(str, Enum):
    DISCONNECTED_E = 'DISCONNECTED_E'
    WAITING_TO_CONNECT_E = 'WAITING_TO_CONNECT_E'
    ITEMS_LOADED_E = 'ITEMS_LOADED_E'
    ITEMS_UNLOADED_E = 'ITEMS_UNLOADED_E'
    CONNECTING_E = 'CONNECTING_E'
    CONNECTED_E = 'CONNECTED_E'
    WAITING_TO_DISCONNECT_E = 'WAITING_TO_DISCONNECT_E'
    DISCONNECTING_E = 'DISCONNECTING_E'
    WAITING_FOR_RETRY_E = 'WAITING_FOR_RETRY_E'
    CONNECTED_PARTIALLY_E = 'CONNECTED_PARTIALLY_E'
    CONNECTED_TO_NOT_ALL_E = 'CONNECTED_TO_NOT_ALL_E'

class RestClient2:
    """Simplified RestClient2 class for RAPID REST API interaction."""
    def __init__(self, base_url: str, api_key: str, verify_ssl: bool = True, timeout: int = 10):
        self.base_url = base_url
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'Authorization': f'Bearer {self.api_key}'
        }

    def get_json(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send HTTP GET request and return JSON response."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in API request to {url}: {e}")
            raise

def parse_rapid_nodes(info):
    """Parse agent output into a dictionary."""
    parsed = {}
    for line in info:
        try:
            data = json.loads(line[0])
            parsed.update(data)
        except (ValueError, IndexError):
            continue
    return parsed

def discovery_rapid_nodes(parsed):
    """Discover nodes in the RAPID database."""
    nodes = parsed.get("Nodes", [])
    for node in nodes:
        yield node, {}

def check_rapid_nodes(item, params, parsed):
    """Check the status of a specific node."""
    nodes = parsed.get("Nodes", [])
    for node in nodes:
        if node == item:
            status_data = parsed.get("Status", {}).get(node, {})
            node_status = status_data.get("ConnectionStatus", "Unknown")
            connection_error = status_data.get("ConnectionError")
            last_update = status_data.get("LastUpdate", "Unknown")

            # Map node status to Check_MK states
            if node_status == NodeStatus_e.CONNECTED_E.value:
                state = 0
                message = f"Node '{item}': Status OK - {node_status}"
            elif node_status in [NodeStatus_e.DISCONNECTED_E.value, "ERROR"] or connection_error:
                state = 2
                message = f"Node '{item}': Status CRITICAL - {node_status if node_status else 'Connection Error'}"
            else:
                state = 1
                message = f"Node '{item}': Status WARNING - {node_status}"

            # Optional performance data (e.g., time since last update)
            perfdata = []
            if last_update != "Unknown":
                try:
                    last_update_dt = datetime.datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                    time_since_update = (datetime.datetime.now(datetime.timezone.utc) - last_update_dt).total_seconds()
                    perfdata.append(("time_since_update", time_since_update))
                except ValueError:
                    pass

            return state, f"{message} (Last Update: {last_update})", perfdata

    return 3, f"Node '{item}' not found", []

def rapid_nodes_api_request(config):
    """Fetch node list and status from RAPID REST API."""
    try:
        api_client = RestClient2(
            base_url=config.get("server_root", "https://localhost:3001"),
            api_key=config.get("api_key", ""),
            verify_ssl=config.get("verify_ssl", True),
            timeout=config.get("timeout", 10)
        )
        db_name = config.get("db_name", "DB1")

        # Get list of nodes
        nodes_response = api_client.get_json(f"/api/v1/database/{db_name}/node")
        nodes = [url.split('/')[-1] for url in nodes_response]

        # Get status for each node
        status_data = {}
        for node in nodes:
            try:
                status = api_client.get_json(f"/api/v1/nodeconnections/database/{db_name}/node/{node}/status")
                status_data[node] = {
                    "ConnectionStatus": status.get("ConnectionStatus", {}).get("ConnectionStatus", "Unknown"),
                    "ConnectionError": status.get("ConnectionError"),
                    "LastUpdate": status.get("LastUpdate", "Unknown")
                }
            except requests.exceptions.RequestException:
                status_data[node] = {
                    "ConnectionStatus": "Unknown",
                    "ConnectionError": "Failed to fetch status",
                    "LastUpdate": "Unknown"
                }

        return {"Nodes": nodes, "Status": status_data}
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from RAPID API: {e}")
        return {}

check_info["rapid_nodes"] = LegacyCheckDefinition(
    parse_function=parse_rapid_nodes,
    discovery_function=discovery_rapid_nodes,
    check_function=check_rapid_nodes,
    service_name="RAPID Node %s",
    check_ruleset_name="rapid_nodes",
)
