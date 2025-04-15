#!/usr/bin/env python3

import requests
import datetime
import json
import random
from argparse import ArgumentParser
import os
import sys
from enum import Enum

# Pfad zum Zertifikat (wird aktuell nicht verwendet, siehe Kommentar im Code)
cert_path = "/usr/local/share/ca-certificates/root_ks.crt"

# create session object
session = requests.session()
# Common request Header
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


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


class NodeConnectionTypeE(str, Enum):
    DATA_LOGGER = 'DataLogger'
    DATA_ADAPTOR = 'DataAdaptor'


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
    print("Proxy-Einstellungen entfernt.")


def authenticateSession(serverRoot, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Authorisiert die Session mit einem API-Schlüssel."""
    headers['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print("Sende GET-Anfrage zur Authentifizierung...")
    try:
        response = session.get(f"{serverRoot}/auth?format=json", headers=headers, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        if verbose:
            print("Session authenticated successfully")
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Authentifizierung: {e}")
        sys.exit(1)


def getDatabase(requestUri, dbName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Ruft die Datenbankliste ab und prüft, ob die angegebene Datenbank existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database mit Headern: {headers_copy}")
    try:
        response = session.get(f"{requestUri}/api/v1/database", headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        databases = response.json()
        if verbose:
            print(f"Antwort-Body (getDatabase): {databases}")
        for db_url in databases:
            db = db_url.split('/')[-1]
            if db == dbName:
                if verbose:
                    print(f"Gefundene Datenbank (getDatabase): {db}")
                return db
        print(f"Datenbank nicht gefunden: {dbName}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Datenbankliste: {e}")
        return None


def getNode(requestUri, dbName, nodeName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Ruft die Knotenliste für eine Datenbank ab und prüft, ob der angegebene Knoten existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database/{dbName}/node mit Headern: {headers_copy}")
    try:
        response = session.get(f"{requestUri}/api/v1/database/{dbName}/node", headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        nodesList = response.json()
        if verbose:
            print(f"Antwort-Body (getNode): {nodesList}")
        for node_url in nodesList:
            node = node_url.split('/')[-1]
            if node == nodeName:
                if verbose:
                    print(f"Gefundener Knoten (getNode): {node}")
                return node
        if verbose:
            print(f"Knoten '{nodeName}' nicht gefunden.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Knotenliste: {e}")
        return None


def getNodeStatus(requestUri, dbName, nodeName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Ruft den Status eines einzelnen Knotens ab und gibt die JSON-Antwort zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    status_url = f"{requestUri}/api/v1/nodeconnections/database/{dbName}/node/{nodeName}/status"
    if verbose:
        print(f"Sende GET-Anfrage an: {status_url} mit Headern: {headers_copy}")
    try:
        response = session.get(status_url, headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        status_data = response.json()
        if verbose:
            print(f"Status für Knoten '{nodeName}': {status_data}")
        return status_data
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen des Status für Knoten '{nodeName}': {e}")
        return None


def listNodes(requestUri, dbName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Ruft die Knotenliste für eine Datenbank ab und gibt sie zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    nodes_url = f"{requestUri}/api/v1/database/{dbName}/node"
    if verbose:
        print(f"Sende GET-Anfrage an: {nodes_url} mit Headern: {headers_copy}")
    try:
        response = session.get(nodes_url, headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        nodesList = response.json()
        if verbose:
            print(f"Antwort-Body (listNodes): {nodesList}")
        return [node_url.split('/')[-1] for node_url in nodesList]
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Knotenliste: {e}")
        return []


def createNode(requestUri, dbName, newNodeName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Erstellt einen neuen Knoten."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"Name": newNodeName, "Type": 2}
    if verbose:
        print(f"Sende POST-Anfrage an: {requestUri}/api/v1/database/{dbName}/node?format=json mit Headern: {headers_copy}, Daten: {payload}")
    try:
        response = session.post(f"{requestUri}/api/v1/database/{dbName}/node?format=json", headers=headers_copy, json=payload, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        if verbose:
            print(f"Node: {newNodeName} created")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen des Knotens: {e}")


def check_database_exists(serverRoot, dbName, apiKey, verify_ssl, verbose=False, proxies=None):
    """Überprüft, ob die Datenbank existiert und gibt True oder False zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database mit Headern: {headers_copy}")
    try:
        response = session.get(f"{serverRoot}/api/v1/database", headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        databases = response.json()
        if verbose:
            print(f"Antwort-Body (check_database_exists): {databases}")
        for db_url in databases:
            db = db_url.split('/')[-1]
            if db == dbName:
                if verbose:
                    print(f"Gefundene Datenbank: {db}")
                return True
        if verbose:
            print(f"Datenbank '{dbName}' nicht gefunden.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Überprüfen der Datenbank: {e}")
        return False


def check_node_exists(serverRoot, dbName, nodeName, apiKey, verify_ssl, verbose=False, proxies=None):
    """Überprüft, ob der Knoten existiert und gibt True oder False zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database/{dbName}/node mit Headern: {headers_copy}")
    try:
        response = session.get(f"{serverRoot}/api/v1/database/{dbName}/node", headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        nodesList = response.json()
        if verbose:
            print(f"Antwort-Body (check_node_exists): {nodesList}")
        for node_url in nodesList:
            node = node_url.split('/')[-1]
            if node == nodeName:
                if verbose:
                    print(f"Gefundener Knoten: {node}")
                return True
        if verbose:
            print(f"Knoten '{nodeName}' nicht gefunden.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Überprüfen des Knotens: {e}")
        return False


def check_item_exists(serverRoot, dbName, nodeName, itemName, apiKey, verify_ssl, verbose=False, proxies=None):
    """Überprüft, ob das Item existiert und gibt True oder False zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item mit Headern: {headers_copy}")
    try:
        response = session.get(f"{serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item", headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        itemsList = response.json()
        if verbose:
            print(f"Antwort-Body (check_item_exists): {itemsList}")
        for entry in itemsList:
            item = entry.split('/')[-1]
            if item == itemName:
                if verbose:
                    print(f"Gefundenes Item: {item}")
                return True
        if verbose:
            print(f"Item '{itemName}' in Knoten '{nodeName}' nicht gefunden.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Überprüfen des Items: {e}")
        return False


def createItem(requestUri, dbName, nodeName, newItemName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Erstellt ein neues Item."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"DbName": dbName, "NodeName": nodeName, "Name": newItemName, "Description": "Test Item"}
    if verbose:
        print(f"Sende POST-Anfrage an: {requestUri}/api/v1.1/item?format=json mit Headern: {headers_copy}, Daten: {payload}")
    try:
        response = session.post(f"{requestUri}/api/v1.1/item?format=json", headers=headers_copy, json=payload, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        if verbose:
            print(f"Item: {newItemName} created")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen des Items: {e}")


def getItem(serverRoot, dbName, nodeName, itemName, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Ruft die Details eines Items ab."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    item_url = f"{serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item/{itemName}?format=json"
    if verbose:
        print(f"Sende GET-Anfrage an: {item_url} mit Headern: {headers_copy}")
    try:
        response = session.get(item_url, headers=headers_copy, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        item_data = response.json()
        if verbose:
            print(f"Details für Item '{itemName}' in Knoten '{nodeName}': {item_data}")
        return item_data
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen des Items '{itemName}' in Knoten '{nodeName}': {e}")
        return None


def WriteProcessData(serverRoot, dbName, nodeName, itemName, startTime, eventsToWrite, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Schreibt Prozessdaten zu einem Item."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    headers_copy['Content-Type'] = 'application/json'
    startTime_dt = datetime.datetime.fromisoformat(startTime)
    events = []
    for i in range(eventsToWrite):
        timestamp = (startTime_dt + datetime.timedelta(milliseconds=i)).isoformat()
        value = random.uniform(0, 100)
        events.append({"ts": timestamp, "val": value})
    payload = {"values": events}
    data_url = f"{serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item/{itemName}/processData?format=json"
    if verbose:
        print(f"Sende POST-Anfrage an: {data_url} mit Headern: {headers_copy}, Daten: {payload}")
    try:
        response = session.post(data_url, headers=headers_copy, json=payload, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        if verbose:
            print(f"{len(events)} Events zu Item '{itemName}' in Knoten '{nodeName}' geschrieben.")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Schreiben von Prozessdaten zu Item '{itemName}' in Knoten '{nodeName}': {e}")

def ReadProcessData(serverRoot, dbName, nodeName, itemName, startTime, endTime, apiKey, verify_ssl=True, verbose=False, proxies=None):
    """Liest Prozessdaten von einem Item."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    params = {"startTime": startTime, "endTime": endTime, "format": "json"}
    data_url = f"{serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item/{itemName}/processData"
    if verbose:
        print(f"Sende GET-Anfrage an: {data_url} mit Headern: {headers_copy}, Parameter: {params}")
    try:
        response = session.get(data_url, headers=headers_copy, params=params, verify=verify_ssl, proxies=proxies)
        response.raise_for_status()
        if verbose:
            print(f"Prozessdaten von Item '{itemName}' in Knoten '{nodeName}' gelesen:")
            print(json.dumps(data, indent=4))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Lesen von Prozessdaten von Item '{itemName}' in Knoten '{nodeName}': {e}")
        return None


if __name__ == '__main__':
    # Setze die Umgebungsvariable PATH, falls sie nicht gesetzt ist (kann in manchen Umgebungen notwendig sein)
    if 'PATH' not in os.environ:
        os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

    # Set parameters for the query
    parser = ArgumentParser(description="Interact with a REST API to manage databases, nodes, and items.")
    parser.add_argument("-s", "--server", dest="serverRoot", help="Server address (z.B., https://yourserver:3001)", default="https://localhost:3001", metavar="URL")
    parser.add_argument("-k", "--apiKey", dest="apiKey", help="API Key für die Authentifizierung (erforderlich)", default=os.getenv('API_KEY'), required=True, metavar="KEY")
    parser.add_argument("-db", "--dbName", dest="dbName", help="Name der Zieldatenbank (Standard: DB1)", default="DB1", metavar="NAME")
    parser.add_argument("-n", "--nodeName", dest="nodeName", help="Name des Zielknotens (Standard: PythonRestClient)", default="PythonRestClient", metavar="NAME")
    parser.add_argument("-i", "--itemName", dest="itemName", help="Name des Ziel-Items (Standard: RandomData-<Zufallszahl>)", default="RandomData-" + str(random.randint(1, 100001)), metavar="NAME")
    parser.add_argument("-e", "--eventsToWrite", dest="eventsToWrite", help="Anzahl der zu schreibenden Events (Standard: 10)", default=10, type=int, metavar="COUNT")
    parser.add_argument("--no-proxy", action="store_true", help="Deaktiviert die Verwendung von Proxies")
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
    parser.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe aktivieren")

    args = parser.parse_args()

    verify_ssl = args.verify_ssl
    verbose = args.verbose
    if verbose:
        if verify_ssl:
            print("SSL-Zertifikatsprüfung aktiviert.")
        else:
            print("SSL-Zertifikatsprüfung deaktiviert.")

    # Proxy-Konfiguration
    proxies = None
    if args.proxy_url:
        proxies = {'http': args.proxy_url, 'https': args.proxy_url}
        if verbose:
            print(f"Verwendet Proxy: {args.proxy_url}")
    elif args.no_proxy:
        set_no_proxy()
        if verbose:
            print("Verwendet keine Proxies (Option --no-proxy gesetzt).")
    elif verbose:
        print("Verwendet keine explizit konfigurierten Proxies (systemweite Einstellungen könnten aktiv sein).")

    ts = datetime.datetime.now() - datetime.timedelta(milliseconds=args.eventsToWrite)
    te = datetime.datetime.now()

    if args.startTime:
        try:
            ts = datetime.datetime.fromisoformat(args.startTime)
        except ValueError:
            print("Ungültiges Startzeit-Format. Bitte ISO-Format verwenden (z.B., 2023-10-26T10:00:00).")
            sys.exit(1)

    if args.endTime:
        try:
            te = datetime.datetime.fromisoformat(args.endTime)
        except ValueError:
            print("Ungültiges Endzeit-Format. Bitte ISO-Format verwenden (z.B., 2023-10-26T11:00:00).")
            sys.exit(1)

    try:
        # Create an authenticated session
        if args.apiKey:
            authenticateSession(args.serverRoot, args.apiKey, verify_ssl, verbose, proxies=proxies)
        else:
            print("API Key nicht angegeben. Das Skript benötigt einen API Key für die Authentifizierung.")
            sys.exit(1)

        # Create a new node if --create-node is specified
        if args.newNodeName:
            if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                createNode(args.serverRoot, args.dbName, args.newNodeName, args.apiKey, verify_ssl, verbose, proxies)
            else:
                print(f"Datenbank '{args.dbName}' nicht gefunden. Knoten '{args.newNodeName}' kann nicht erstellt werden.")
            sys.exit(0)

        # Create a new item if --create-item is specified
        if args.newItemName:
            if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                if check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl, verbose, proxies):
                    createItem(args.serverRoot, args.dbName, args.nodeName, args.newItemName, args.apiKey, verify_ssl, verbose, proxies)
                else:
                    print(f"Knoten '{args.nodeName}' nicht gefunden. Item '{args.newItemName}' kann nicht erstellt werden.")
            else:
                print(f"Datenbank '{args.dbName}' nicht gefunden. Item '{args.newItemName}' kann nicht erstellt werden.")
            sys.exit(0)

        # Get node status if --get-node-status is specified
        if args.target_node_status:
            if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                print("<<<local>>>")
                if args.target_node_status.lower() == 'all':
                    nodes = listNodes(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies)
                    if nodes:
                        for node_name in nodes:
                            status = getNodeStatus(args.serverRoot, args.dbName, node_name, args.apiKey, verify_ssl, verbose, proxies)
                            if status is not None:
                                node_status = status.get('ConnectionStatus', {}).get('ConnectionStatus')
                                connection_error = status.get('ConnectionError')
                                last_update = status.get('LastUpdate')
                                checkmk_state = 0  # OK
                                checkmk_message = f"Node '{node_name}': Status {node_status}"

                                if node_status == NodeStatus_e.DISCONNECTED_E.value or node_status == NodeStatus_e.ERROR.value or connection_error:
                                    checkmk_state = 2  # CRITICAL
                                    checkmk_message = f"Node '{node_name}': Status CRITICAL - {node_status if node_status else 'Connection Error'}"
                                elif node_status != NodeStatus_e.CONNECTED_E.value:
                                    checkmk_state = 1  # WARNING
                                    checkmk_message = f"Node '{node_name}': Status WARNING - {node_status}"

                                print(f"{checkmk_state} rest_api_node_{node_name.replace('"', '\\"')}"
                                      f" - {checkmk_message.replace('"', '\\"')}"
                                      f" (Last Update: {last_update})")
                    else:
                        print(f"0 rest_api_nodes - Keine Knoten in Datenbank '{args.dbName}' gefunden.")
                else:
                    if check_node_exists(args.serverRoot, args.dbName, args.target_node_status, args.apiKey, verify_ssl, verbose, proxies):
                        status = getNodeStatus(args.serverRoot, args.dbName, args.target_node_status, args.apiKey, verify_ssl, verbose, proxies)
                        if status is not None:
                            node_status = status.get('ConnectionStatus', {}).get('ConnectionStatus')
                            connection_error = status.get('ConnectionError')
                            last_update = status.get('LastUpdate')
                            checkmk_state = 0  # OK
                            checkmk_message = f"Node '{args.target_node_status}': Status {node_status}"

                            if node_status == NodeStatus_e.DISCONNECTED_E.value or node_status == NodeStatus_e.ERROR.value or connection_error:
                                checkmk_state = 2  # CRITICAL
                                checkmk_message = f"Node '{args.target_node_status}': Status CRITICAL - {node_status if node_status else 'Connection Error'}"
                            elif node_status != NodeStatus_e.CONNECTED_E.value:
                                checkmk_state = 1  # WARNING
                                checkmk_message = f"Node '{args.target_node_status}': Status WARNING - {node_status}"

                            print(f"{checkmk_state} rest_api_node_{args.target_node_status.replace('"', '\\"')}"
                                  f" - {checkmk_message.replace('"', '\\"')}"
                                  f" (Last Update: {last_update})")
                        else:
                            print(f"Konnte Status für Knoten '{args.target_node_status}' nicht abrufen.")
                    else:
                        print(f"Knoten '{args.target_node_status}' nicht gefunden.")
            else:
                print(f"Datenbank '{args.dbName}' nicht gefunden.")
            sys.exit(0)

        # List nodes with status for Checkmk if --list-nodes is specified
        if args.list_nodes:
            if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                nodes = listNodes(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies)
                if nodes:
                    print("<<<local>>>")
                    for node_name in nodes:
                        status = getNodeStatus(args.serverRoot, args.dbName, node_name, args.apiKey, verify_ssl, verbose, proxies)
                        if status is not None:
                            node_status = status.get('ConnectionStatus', {}).get('ConnectionStatus')
                            connection_error = status.get('ConnectionError')
                            last_update = status.get('LastUpdate')
                            checkmk_state = 0  # OK
                            checkmk_message = f"Node '{node_name}': Status {node_status}"

                            if node_status == NodeStatus_e.DISCONNECTED_E.value or node_status == NodeStatus_e.ERROR.value or connection_error:
                                checkmk_state = 2  # CRITICAL
                                checkmk_message = f"Node '{node_name}': Status CRITICAL - {node_status if node_status else 'Connection Error'}"
                            elif node_status != NodeStatus_e.CONNECTED_E.value:
                                checkmk_state = 1  # WARNING
                                checkmk_message = f"Node '{node_name}': Status WARNING - {node_status}"

                            print(f"{checkmk_state} rest_api_node_{node_name.replace('"', '\\"')}"
                                  f" - {checkmk_message.replace('"', '\\"')}"
                                  f" (Last Update: {last_update})")
                else:
                    print("<<<local>>>")
                    print(f"0 rest_api_nodes - Keine Knoten in Datenbank '{args.dbName}' gefunden.")
            else:
                print("<<<local>>>")
                print(f"0 rest_api_nodes - Datenbank '{args.dbName}' nicht gefunden.")
            sys.exit(0)

        # Check if the specified item exists and print details
        if args.get_item:
            if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                if check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl, verbose, proxies):
                    item_data = getItem(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl, verbose, proxies)
                    if item_data:
                        print(f"Item '{args.itemName}' gefunden in Knoten '{args.nodeName}':")
                        print(json.dumps(item_data, indent=4))
                    else:
                        print(f"Item '{args.itemName}' nicht gefunden in Knoten '{args.nodeName}'.")
                else:
                    print(f"Knoten '{args.nodeName}' nicht gefunden.")
            else:
                print(f"Datenbank '{args.dbName}' nicht gefunden.")
            sys.exit(0)

        # Write process data if --write-process-data is specified
        if args.write_process_data:
            if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                if check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl, verbose, proxies):
                    if check_item_exists(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl, verbose, proxies):
                        WriteProcessData(args.serverRoot, args.dbName, args.nodeName, args.itemName, ts.isoformat(), args.eventsToWrite, args.apiKey, verify_ssl, verbose, proxies)
                    else:
                        print(f"Item '{args.itemName}' nicht gefunden in Knoten '{args.nodeName}'. Prozessdaten können nicht geschrieben werden.")
                else:
                    print(f"Knoten '{args.nodeName}' nicht gefunden. Prozessdaten können nicht geschrieben werden.")
            else:
                print(f"Datenbank '{args.dbName}' nicht gefunden. Prozessdaten können nicht geschrieben werden.")
            sys.exit(0)

        # Read process data if --read-process-data is specified
        if args.read_process_data:
            if args.startTime and args.endTime:
                if check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies):
                    if check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl, verbose, proxies):
                        if check_item_exists(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl, verbose, proxies):
                            ReadProcessData(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.startTime, args.endTime, args.apiKey, verify_ssl, verbose, proxies)
                        else:
                            print(f"Item '{args.itemName}' nicht gefunden in Knoten '{args.nodeName}'. Prozessdaten können nicht gelesen werden.")
                    else:
                        print(f"Knoten '{args.nodeName}' nicht gefunden. Prozessdaten können nicht gelesen werden.")
                else:
                    print(f"Datenbank '{args.dbName}' nicht gefunden. Prozessdaten können nicht gelesen werden.")
            else:
                print("Bitte geben Sie sowohl --start-time als auch --end-time für das Lesen von Prozessdaten an.")
            sys.exit(0)

        # Verify the database exists and print the result (only if no other action was taken)
        if not any([args.newNodeName, args.newItemName, args.target_node_status, args.list_nodes, args.get_item, args.write_process_data, args.read_process_data]):
            found_database = check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl, verbose, proxies)
            if not found_database:
                print("Keine Datenbank gefunden. Beende.")
                sys.exit(-1)

            # Verify if the node exists and print the result (only if no other action was taken)
            found_node = check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl, verbose, proxies)
            if not found_node:
                print(f"Knoten '{args.nodeName}' nicht gefunden. Beende.")
                sys.exit(-1)

            # Verify if the item exists and print the result (only if no other action was taken)
            found_item = check_item_exists(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl, verbose, proxies)
            if not found_item:
                print(f"Item '{args.itemName}' nicht gefunden. Beende.")
                sys.exit(-1)

            print("Datenbank, Knoten und Item gefunden.")

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        sys.exit(-1)