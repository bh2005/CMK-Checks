#!/usr/bin/env python3

import requests
import logging
from typing import Optional, Dict, Any
import os
import sys
import json
import random
from argparse import ArgumentParser
from enum import Enum
import datetime

logging.basicConfig(level=logging.INFO)

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
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 verify_ssl: bool = True,
                 timeout: int = 10,
                 proxies: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.proxies = proxies
        self.session = requests.Session()
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization': f'Bearer {self.api_key}'}

    def _request(self,
                 method: str,
                 endpoint: str,
                 params: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None,
                 json_data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                proxies=self.proxies
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {method} {url}: {e}")
            raise

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        return self._request('GET', endpoint, params=params, headers=headers)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        return self._request('POST', endpoint, data=data, json_data=json_data, headers=headers)

    def get_json(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        response = self.get(endpoint, params=params, headers=headers)
        return response.json()

    def post_json(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        response = self.post(endpoint, data=data, json_data=json_data, headers=headers)
        return response.json()

def set_no_proxy():
    """Entfernt Proxy-Einstellungen aus der Umgebung."""
    if 'HTTP_PROXY' in os.environ:
        del os.environ['HTTP_PROXY']
    if 'HTTPS_PROXY' in os.environ:
        del os.environ['HTTPS_PROXY']
    if 'http_proxy' in os.environ:
        del os.environ['http_proxy']
    if 'https_proxy' in os.environ:
        del os.environ['https_proxy']
    logging.info("Proxy-Einstellungen entfernt.")

def main():
    parser = ArgumentParser(description="Interact with a REST API to manage databases, nodes, and items.")
    parser.add_argument("-s", "--server", dest="serverRoot", help="Server address (z.B., https://yourserver:3001)", default="https://localhost:3001", metavar="URL", required=True)
    parser.add_argument("-k", "--apiKey", dest="apiKey", help="API Key für die Authentifizierung (erforderlich)", default=os.getenv('API_KEY'), required=True, metavar="KEY")
    parser.add_argument("-db", "--dbName", dest="dbName", help="Name der Zieldatenbank (Standard: DB1)", default="DB1", metavar="NAME")
    parser.add_argument("-n", "--nodeName", dest="nodeName", help="Name des Zielknotens (Standard: PythonRestClient)", default="PythonRestClient", metavar="NAME")
    parser.add_argument("-i", "--itemName", dest="itemName", help="Name des Ziel-Items (Standard: RandomData-<Zufallszahl>)", default="RandomData-" + str(random.randint(1, 100001)), metavar="NAME")
    parser.add_argument("-e", "--eventsToWrite", dest="eventsToWrite", help="Anzahl der zu schreibenden Events (Standard: 10)", default=10, type=int, metavar="COUNT")
    parser.add_argument("--no-proxy", action="store_true", default=True, help="Deaktiviert die Verwendung von Proxies (Standard)")
    parser.add_argument("--proxy", dest="proxy_url", help="Verwendet den angegebenen Proxy (z.B., http://user:pass@host:port)", metavar="URL")
    parser.add_argument("--verify-ssl", action="store_true", default=True, help="Aktiviert die SSL-Zertifikatsprüfung (Standard: True)")
    parser.add_argument("--list-nodes", action="store_true", help="Listet alle Knoten in der angegebenen Datenbank mit ihrem Status für Checkmk auf")
    parser.add_argument("--get-node-status", dest="target_node_status", help="Ruft den Status eines bestimmten Knotens ab ('all' für alle Knoten)", metavar="NODE_NAME")
    parser.add_argument("--read-process-data", action="store_true", help="Liest Prozessdaten vom angegebenen Item")
    parser.add_argument("--start-time", dest="startTime", help="Startzeit für das Lesen von Prozessdaten (ISO-Format) (z.B., 2023-10-26T10:00:00)", metavar="TIMESTAMP")
    parser.add_argument("--end-time", dest="endTime", help="Endzeit für das Lesen von Prozessdaten (ISO-Format) (z.B., 2023-10-26T11:00:00)", metavar="TIMESTAMP")
    parser.add_argument("--get-item", action="store_true", help="Überprüft, ob das angegebene Item existiert und gibt Details aus")
    parser.add_argument("--create-node", dest="newNodeName", help="Erstellt einen neuen Knoten mit dem angegebenen Namen", metavar="NAME")
    parser.add_argument("--create-item", dest="newItemName", help="Erstellt ein neues Item mit dem angegebenen Namen", metavar="NAME")
    parser.add_argument("--write-process-data", action="store_true", help="Schreibt zufällige Prozessdaten zum angegebenen Item")
    parser.add_argument("--list-items", action="store_true", help="Listet alle Items im angegebenen Knoten auf")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe aktivieren")

    args = parser.parse_args()

    verbose = args.verbose
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Ausführliche Ausgabe aktiviert.")
        logging.debug(f"SSL-Verifikationsstatus: {args.verify_ssl}")

    proxies = None
    if args.proxy_url:
        proxies = {'http': args.proxy_url, 'https': args.proxy_url}
        logging.info(f"Verwendet Proxy: {args.proxy_url}")
    elif args.no_proxy:
        set_no_proxy()
    else:
        logging.info("Verwendet keine explizit konfigurierten Proxies (Standard).")

    api_client = RestClient2(base_url=args.serverRoot, api_key=args.apiKey, verify_ssl=args.verify_ssl, proxies=proxies)

    ts = datetime.datetime.now() - datetime.timedelta(milliseconds=args.eventsToWrite)
    te = datetime.datetime.now()

    if args.startTime:
        try:
            ts = datetime.datetime.fromisoformat(args.startTime)
        except ValueError:
            logging.error("Ungültiges Startzeit-Format. Bitte ISO-Format verwenden (z.B., 2023-10-26T10:00:00).")
            sys.exit(1)

    if args.endTime:
        try:
            te = datetime.datetime.fromisoformat(args.endTime)
        except ValueError:
            logging.error("Ungültiges Endzeit-Format. Bitte ISO-Format verwenden (z.B., 2023-10-26T11:00:00).")
            sys.exit(1)

    try:
        # Helper functions using the RestClient
        def check_db_exists(db_name):
            try:
                response = api_client.get_json("/api/v1/database")
                return db_name in [url.split('/')[-1] for url in response]
            except requests.exceptions.RequestException:
                return False

        def check_node_exists(db_name, node_name):
            try:
                response = api_client.get_json(f"/api/v1/database/{db_name}/node")
                return node_name in [url.split('/')[-1] for url in response]
            except requests.exceptions.RequestException:
                return False

        def check_item_exists(db_name, node_name, item_name):
            try:
                response = api_client.get_json(f"/api/v1/database/{db_name}/node/{node_name}/item")
                return item_name in [url.split('/')[-1] for url in response]
            except requests.exceptions.RequestException:
                return False

        def get_node_status(db_name, node_name):
            try:
                return api_client.get_json(f"/api/v1/nodeconnections/database/{db_name}/node/{node_name}/status")
            except requests.exceptions.RequestException:
                return None

        def list_nodes(db_name):
            try:
                response = api_client.get_json(f"/api/v1/database/{db_name}/node")
                return [url.split('/')[-1] for url in response]
            except requests.exceptions.RequestException:
                return []

        def list_items(db_name, node_name):
            try:
                response = api_client.get_json(f"/api/v1/database/{db_name}/node/{node_name}/item")
                return [url.split('/')[-1] for url in response]
            except requests.exceptions.RequestException:
                return []

        def create_node(db_name, node_name):
            payload = {"Name": node_name, "Type": 2}
            api_client.post(f"/api/v1/database/{db_name}/node?format=json", json_data=payload)
            logging.info(f"Node: {node_name} created")

        def create_item(db_name, node_name, item_name):
            payload = {"DbName": db_name, "NodeName": node_name, "Name": item_name, "Description": "Test Item"}
            api_client.post("/api/v1.1/item?format=json", json_data=payload)
            logging.info(f"Item: {item_name} created")

        def get_item_details(db_name, node_name, item_name):
            return api_client.get_json(f"/api/v1/database/{db_name}/node/{node_name}/item/{item_name}?format=json")

        def write_process_data(db_name, node_name, item_name, start_time, events_to_write):
            start_time_dt = datetime.datetime.fromisoformat(start_time)
            events = []
            for i in range(events_to_write):
                timestamp = (start_time_dt + datetime.timedelta(milliseconds=i)).isoformat()
                value = random.uniform(0, 100)
                events.append({"ts": timestamp, "val": value})
            payload = {"values": events}
            api_client.post(f"/api/v1/database/{db_name}/node/{node_name}/item/{item_name}/processData?format=json", json_data=payload)
            logging.info(f"{len(events)} Events zu Item '{item_name}' in Knoten '{node_name}' geschrieben.")

        def read_process_data(db_name, node_name, item_name, start_time, end_time):
            params = {"startTime": start_time, "endTime": end_time, "format": "json"}
            return api_client.get_json(f"/api/v1/database/{db_name}/node/{node_name}/item/{item_name}/processData", params=params)

        # Main execution logic
        if args.newNodeName:
            if check_db_exists(args.dbName):
                create_node(args.dbName, args.newNodeName)
            else:
                logging.error(f"Datenbank '{args.dbName}' nicht gefunden. Knoten '{args.newNodeName}' kann nicht erstellt werden.")
            sys.exit(0)

        if args.newItemName:
            if check_db_exists(args.dbName) and check_node_exists(args.dbName, args.nodeName):
                create_item(args.dbName, args.nodeName, args.newItemName)
            else:
                logging.error(f"Datenbank '{args.dbName}' oder Knoten '{args.nodeName}' nicht gefunden. Item '{args.newItemName}' kann nicht erstellt werden.")
            sys.exit(0)

        if args.target_node_status:
            if check_db_exists(args.dbName):
                print("<<<local>>>")
                if args.target_node_status.lower() == 'all':
                    nodes = list_nodes(args.dbName)
                    for node_name in nodes:
                        status = get_node_status(args.dbName, node_name)
                        last_update = None
                        if status:
                            node_status_value = status.get('ConnectionStatus', {}).get('ConnectionStatus')
                            connection_error = status.get('ConnectionError')
                            last_update = status.get('LastUpdate')
                            checkmk_state = 0
                            checkmk_message = f"Node '{node_name}': Status {node_status_value}"
                            if node_status_value == NodeStatus_e.DISCONNECTED_E.value or node_status_value == NodeStatus_e.ERROR.value or connection_error:
                                checkmk_state = 2
                                checkmk_message = f"Node '{node_name}': Status CRITICAL - {node_status_value if node_status_value else 'Connection Error'}"
                            elif node_status_value != NodeStatus_e.CONNECTED_E.value:
                                checkmk_state = 1
                                checkmk_message = f"Node '{node_name}': Status WARNING - {node_status_value}"
                            print(f"{checkmk_state} rest_api_node_{node_name.replace('"', '\\"')}"
                                  f" - {checkmk_message.replace('"', '\\"')}"
                                  f" (Last Update: {last_update})")
                elif check_node_exists(args.dbName, args.target_node_status):
                    status = get_node_status(args.dbName, args.target_node_status)
                    last_update = None
                    if status:
                        node_status_value = status.get('ConnectionStatus', {}).get('ConnectionStatus')
                        connection_error = status.get('ConnectionError')
                        last_update
                        checkmk_state = 0
                        checkmk_message = f"Node '{args.target_node_status}': Status {node_status_value}"
                        if node_status_value == NodeStatus_e.DISCONNECTED_E.value or node_status_value == NodeStatus_e.ERROR.value or connection_error:
                            checkmk_state = 2
                            checkmk_message = f"Node '{args.target_node_status}': Status CRITICAL - {node_status_value if node_status_value else 'Connection Error'}"
                        elif node_status_value != NodeStatus_e.CONNECTED_E.value:
                            checkmk_state = 1
                            checkmk_message = f"Node '{args.target_node_status}': Status WARNING - {node_status_value}"
                        print(f"{checkmk_state} rest_api_node_{args.target_node_status.replace('"', '\\"')}"
                              f" - {checkmk_message.replace('"', '\\"')}"
                              f" (Last Update: {last_update})")
                    else:
                        logging.error(f"Konnte Status für Knoten '{args.target_node_status}' nicht abrufen.")
                else:
                    logging.error(f"Knoten '{args.target_node_status}' nicht gefunden.")
            else:
                logging.error(f"Datenbank '{args.dbName}' nicht gefunden.")
            sys.exit(0)

        if args.list_nodes:
            if check_db_exists(args.dbName):
                nodes = list_nodes(args.dbName)
                print("<<<local>>>")
                for node_name in nodes:
                    status = get_node_status(args.dbName, node_name)
                    last_update = None
                    if status:
                        node_status_value = status.get('ConnectionStatus', {}).get('ConnectionStatus')
                        connection_error = status.get('ConnectionError')
                        last_update = status.get('LastUpdate')
                        checkmk_state = 0
                        checkmk_message = f"Node '{node_name}': Status {node_status_value}"
                        if node_status_value == NodeStatus_e.DISCONNECTED_E.value or node_status_value == NodeStatus_e.ERROR.value or connection_error:
                            checkmk_state = 2
                            checkmk_message = f"Node '{node_name}': Status CRITICAL - {node_status_value if node_status_value else 'Connection Error'}"
                        elif node_status_value != NodeStatus_e.CONNECTED_E.value:
                            checkmk_state = 1
                            checkmk_message = f"Node '{node_name}': Status WARNING - {node_status_value}"
                        print(f"{checkmk_state} rest_api_node_{node_name.replace('"', '\\"')}"
                              f" - {checkmk_message.replace('"', '\\"')}"
                              f" (Last Update: {last_update})")
                    else:
                        logging.warning(f"Konnte Status für Knoten '{node_name}' nicht abrufen.")
            else:
                print("<<<local>>>")
                print(f"0 rest_api_nodes - Datenbank '{args.dbName}' nicht gefunden.")
            sys.exit(0)

        if args.get_item:
            if check_db_exists(args.dbName) and check_node_exists(args.dbName, args.nodeName) and check_item_exists(args.dbName, args.nodeName, args.itemName):
                item_data = get_item_details(args.dbName, args.nodeName, args.itemName)
                print(f"Item '{args.itemName}' gefunden in Knoten '{args.nodeName}':")
                print(json.dumps(item_data, indent=4))
            else:
                logging.error(f"Datenbank '{args.dbName}', Knoten '{args.nodeName}' oder Item '{args.itemName}' nicht gefunden.")
            sys.exit(0)

        if args.write_process_data:
            if check_db_exists(args.dbName) and check_node_exists(args.dbName, args.nodeName) and check_item_exists(args.dbName, args.nodeName, args.itemName):
                write_process_data(args.dbName, args.nodeName, args.itemName, ts.isoformat(), args.eventsToWrite)
            else:
                logging.error(f"Datenbank '{args.dbName}', Knoten '{args.nodeName}' oder Item '{args.itemName}' nicht gefunden. Prozessdaten können nicht geschrieben werden.")
            sys.exit(0)

        if args.read_process_data:
            if args.startTime and args.endTime:
                if check_db_exists(args.dbName) and check_node_exists(args.dbName, args.nodeName) and check_item_exists(args.dbName, args.nodeName, args.itemName):
                    data = read_process_data(args.dbName, args.nodeName, args.itemName, args.startTime, args.endTime)
                    if data:
                        print(f"Prozessdaten von Item '{args.itemName}' in Knoten '{args.nodeName}':")
                        print(json.dumps(data, indent=4))
                    else:
                        logging.warning(f"Konnte keine Prozessdaten für Item '{args.itemName}' abrufen.")
                else:
                    logging.error(f"Datenbank '{args.dbName}', Knoten '{args.nodeName}' oder Item '{args.itemName}' nicht gefunden. Prozessdaten können nicht gelesen werden.")
            else:
                logging.error("Bitte geben Sie sowohl --start-time als auch --end-time für das Lesen von Prozessdaten an.")
            sys.exit(0)

        if args.list_items:
            if check_db_exists(args.dbName) and check_node_exists(args.dbName, args.nodeName):
                items = list_items(args.dbName, args.nodeName)
                if items is not None:
                    print(f"Items im Knoten '{args.nodeName}':")
                    for item in items:
                        print(f"- {item}")
                else:
                    logging.warning(f"Konnte die Item-Liste für Knoten '{args.nodeName}' nicht abrufen.")
            else:
                logging.error(f"Datenbank '{args.dbName}' oder Knoten '{args.nodeName}' nicht gefunden.")
            sys.exit(0)

        # Default action if no specific option is used
        if not any([args.newNodeName, args.newItemName, args.target_node_status, args.list_nodes, args.get_item, args.write_process_data, args.read_process_data, args.list_items]):
            if check_db_exists(args.dbName) and check_node_exists(args.dbName, args.nodeName) and check_item_exists(args.dbName, args.nodeName, args.itemName):
                logging.info(f"Datenbank '{args.dbName}', Knoten '{args.nodeName}' und Item '{args.itemName}' gefunden.")
            else:
                logging.warning("Mindestens eine der Standardentitäten (Datenbank, Knoten, Item) wurde nicht gefunden.")
                sys.exit(1)

    except requests.exceptions.RequestException as e:
        logging.error(f"Ein Fehler bei der API-Interaktion ist aufgetreten: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        sys.exit(-1)

if __name__ == '__main__':
    main()
