#!/usr/bin/env python3

import requests
import datetime
import json
import random
from argparse import ArgumentParser
import os
import sys
from enum import Enum

# Pfad zum Zertifikat
cert_path = "/usr/local/share/ca-certificates/root_cert.crt"

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


def authenticateSession(serverRoot, apiKey, verify_cert=True, verbose=False):
    """Authorisiert die Session mit einem API-Schlüssel."""
    headers['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print("Sende GET-Anfrage zur Authentifizierung...")
    response = session.get(f"{serverRoot}/auth?format=json", headers=headers, verify=verify_cert)
    if response.status_code != 200:
        raise Exception("Unauthorized session")
    else:
        if verbose:
            print("Session authenticated successfully")


def getDatabase(requestUri, dbName, apiKey, verify_cert=True, verbose=False):
    """Ruft die Datenbankliste ab und prüft, ob die angegebene Datenbank existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database mit Headern: {headers_copy}")
    response = session.get(f"{requestUri}/api/v1/database", headers=headers_copy, verify=verify_cert)
    if verbose:
        print(f"Antwort-Statuscode (getDatabase): {response.status_code}")
    if response.status_code == 200:
        databases = json.loads(response.text)
        if verbose:
            print(f"Antwort-Body (getDatabase): {databases}")
        for db_url in databases:
            # Extrahiere den Datenbanknamen aus der URL
            db = db_url.split('/')[-1]
            if db == dbName:
                if verbose:
                    print(f"Gefundene Datenbank (getDatabase): {db}")
                return db
        raise Exception(f"Database not found: {dbName}")
    else:
        raise Exception(f"Error fetching database list: {response.status_code}")


def getNode(requestUri, dbName, nodeName, apiKey, verify_cert=True, verbose=False):
    """Ruft die Knotenliste für eine Datenbank ab und prüft, ob der angegebene Knoten existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    if verbose:
        print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database/{dbName}/node mit Headern: {headers_copy}")
    response = session.get(f"{requestUri}/api/v1/database/{dbName}/node", headers=headers_copy, verify=verify_cert)
    if verbose:
        print(f"Antwort-Statuscode (getNode): {response.status_code}")
    if response.status_code == 200:
        nodesList = json.loads(response.text)
        if verbose:
            print(f"Antwort-Body (getNode): {nodesList}")
        for node_url in nodesList:
            node = node_url.split('/')[-1]  # Extrahiere den letzten Teil des Pfads
            if node == nodeName:
                if verbose:
                    print(f"Gefundener Knoten (getNode): {node}")
                return node
        return ""  # Knoten nicht gefunden
    else:
        raise Exception(f"Error fetching node list: {response.status_code}")


def getNodeStatus(requestUri, dbName, nodeName, apiKey, verify_cert=True, verbose=False):
    """Ruft den Status eines einzelnen Knotens ab und gibt die JSON-Antwort zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    status_url = f"{requestUri}/api/v1/nodeconnections/database/{dbName}/node/{nodeName}/status"
    if verbose:
        print(f"Sende GET-Anfrage an: {status_url} mit Headern: {headers_copy}")
    response = session.get(status_url, headers=headers_copy, verify=verify_cert)
    if verbose:
        print(f"Antwort-Statuscode (getNodeStatus) für Knoten '{nodeName}': {response.status_code}")
    if response.status_code == 200:
        status_data = response.json()  # Verwende response.json() zum direkten Parsen
        if verbose:
            print(f"Status für Knoten '{nodeName}': {status_data}")
        return status_data
    else:
        print(f"Fehler beim Abrufen des Status für Knoten '{nodeName}': {response.status_code}")
        return None


def listNodes(requestUri, dbName, apiKey, verify_cert=True, verbose=False):
    """Ruft die Knotenliste für eine Datenbank ab und gibt sie zurück."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    nodes_url = f"{requestUri}/api/v1/database/{dbName}/node"
    if verbose:
        print(f"Sende GET-Anfrage an: {nodes_url} mit Headern: {headers_copy}")
    response = session.get(nodes_url, headers=headers_copy, verify=verify_cert)
    if verbose:
        print(f"Antwort-Statuscode (listNodes): {response.status_code}")
    if response.status_code == 200:
        nodesList = json.loads(response.text)
        if verbose:
            print(f"Antwort-Body (listNodes): {nodesList}")
        return [node_url.split('/')[-1] for node_url in nodesList]
    else:
        raise Exception(f"Fehler beim Abrufen der Knotenliste: {response.status_code}")


def createNode(requestUri, dbName, newNodeName, apiKey, verify_cert=True, verbose=False):
    """Erstellt einen neuen Knoten."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"Name": newNodeName, "Type": 2}
    if verbose:
        print(f"Sende POST-Anfrage an: {requestUri}/api/v1/database/{dbName}/node?format=json mit Headern: {headers_copy}, Daten: {payload}")
    response = session.post(f"{requestUri}/api/v1/database/{dbName}/node?format=json", headers=headers_copy, json=payload, verify=verify_cert)
    if verbose:
        print(f"Antwort-Statuscode (createNode): {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Unable to create node: {response.text}")
    else:
        print(f"Node: {newNodeName} created")


def check_database_exists(serverRoot, dbName, apiKey, verify_cert, verbose=False):
    """Überprüft, ob die Datenbank existiert und gibt den Namen zurück oder None."""
    try:
        headers_copy = headers.copy()
        headers_copy['Authorization'] = f'Bearer {apiKey}'
        if verbose:
            print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database mit Headern: {headers_copy}")
        response = session.get(f"{serverRoot}/api/v1/database", headers=headers_copy, verify=verify_cert)
        if verbose:
            print(f"Antwort-Statuscode (check_database_exists): {response.status_code}")
        if response.status_code == 200:
            databases = json.loads(response.text)
            if verbose:
                print(f"Antwort-Body (check_database_exists): {databases}")
            for db_url in databases:
                db = db_url.split('/')[-1]
                if db == dbName:
                    if verbose:
                        print(f"Gefundene Datenbank: {db}")
                    return db
            raise Exception(f"Database not found: {dbName}")
        else:
            raise Exception(f"Error fetching database list: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Überprüfen der Datenbank: {e}")
        return None


def check_node_exists(serverRoot, dbName, nodeName, apiKey, verify_cert, verbose=False):
    """Überprüft, ob der Knoten existiert und gibt den Namen zurück oder None."""
    try:
        headers_copy = headers.copy()
        headers_copy['Authorization'] = f'Bearer {apiKey}'
        if verbose:
            print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database/{dbName}/node mit Headern: {headers_copy}")
        response = session.get(f"{serverRoot}/api/v1/database/{dbName}/node", headers=headers_copy, verify=verify_cert)
        if verbose:
            print(f"Antwort-Statuscode (check_node_exists): {response.status_code}")
        if response.status_code == 200:
            nodesList = json.loads(response.text)
            if verbose:
                print(f"Antwort-Body (check_node_exists): {nodesList}")
            for node_url in nodesList:
                node = node_url.split('/')[-1]  # Extrahiere den letzten Teil des Pfads
                if node == nodeName:
                    if verbose:
                        print(f"Gefundener Knoten: {node}")
                    return node
            return None  # Knoten nicht gefunden (leere Zeichenkette wird nicht als gefunden interpretiert)
        else:
            raise Exception(f"Error fetching node list: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Überprüfen des Knotens: {e}")
        return None


def check_item_exists(serverRoot, dbName, nodeName, itemName, apiKey, verify_cert, verbose=False):
    """Überprüft, ob das Item existiert und gibt den Namen zurück oder None."""
    try:
        headers_copy = headers.copy()
        headers_copy['Authorization'] = f'Bearer {apiKey}'
        if verbose:
            print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item mit Headern: {headers_copy}")
        response = session.get(f"{serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item", headers=headers_copy, verify=verify_cert)
        if verbose:
            print(f"Antwort-Statuscode (check_item_exists): {response.status_code}")
        if response.status_code == 200:
            itemsList = json.loads(response.text)
            if verbose:
                print(f"Antwort-Body (check_item_exists): {itemsList}")
            for entry in itemsList:
                item = entry.split('/')[-1]
                if item == itemName:
                    if verbose:
                        print(f"Gefundenes Item: {item}")
                    return item
            return None  # Item nicht gefunden (leere Zeichenkette wird nicht als gefunden interpretiert)
        else:
            raise Exception(f"Error fetching item list: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Überprüfen des Items: {e}")
        return None


def createItem(requestUri, dbName, nodeName, newItemName, apiKey, verify_cert=True, verbose=False):
    """Erstellt ein neues Item."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"DbName": dbName, "NodeName": nodeName, "Name": newItemName, "Description": "Test Item"}
    if verbose:
        print(f"Sende POST-Anfrage an: {requestUri}/api/v1.1/item?format=json mit Headern: {headers_copy}, Daten: {payload}")
    response = session.post(f"{requestUri}/api/v1.1/item?format=json", headers=headers_copy, json=payload, verify=verify_cert)
    if verbose:
        print(f"Antwort-Statuscode (createItem): {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Unable to create item: {response.text}")
    else:
        print(f"Item: {newItemName} created")


if __name__ == '__main__':
    # Setze die Umgebungsvariable PATH, falls sie nicht gesetzt ist (kann in manchen Umgebungen notwendig sein)
    if 'PATH' not in os.environ:
        os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

    # Entferne Proxy-Einstellungen
    if not "--no-proxy" in sys.argv: # Nur entfernen, wenn --no-proxy nicht explizit gesetzt ist
        set_no_proxy()
    else:
        print("Option --no-proxy ist gesetzt, Proxy-Einstellungen bleiben.")

    # Set parameters for the query
    parser = ArgumentParser(description="Interact with a REST API to manage databases, nodes, and items.")
    parser.add_argument("-s", "--server", dest="serverRoot", help="Server address (z.B., https://yourserver:3001)", default="https://localhost:3001", metavar="URL")
    parser.add_argument("-k", "--apiKey", dest="apiKey", help="API Key für die Authentifizierung (erforderlich)", default=os.getenv('API_KEY'), required=True, metavar="KEY")
    parser.add_argument("-db", "--dbName", dest="dbName", help="Name der Zieldatenbank (Standard: DB1)", default="DB1", metavar="NAME")
    parser.add_argument("-n", "--nodeName", dest="nodeName", help="Name des Zielknotens (Standard: PythonRestClient)", default="PythonRestClient", metavar="NAME")
    parser.add_argument("-i", "--itemName", dest="itemName", help="Name des Ziel-Items (Standard: RandomData-<Zufallszahl>)", default="RandomData-" + str(random.randint(1, 100001)), metavar="NAME")
    parser.add_argument("-e", "--eventsToWrite", dest="eventsToWrite", help="Anzahl der zu schreibenden Events (Standard: 10)", default=10, type=int, metavar="COUNT")
    parser.add_argument("--no-proxy", action="store_true", help="Deaktiviert die Verwendung von Proxies")
    parser.add_argument("--verify-ssl", action="store_true", default=True, help="Aktiviert die SSL-Zertifikatsprüfung (Standard: True)")
    parser.add_argument("--list-nodes", action="store_true", help="Listet alle Knoten in der angegebenen Datenbank mit ihrem Status auf")
    parser.add_argument("--get-node-status", dest="target_node_status", help="Ruft den Status eines bestimmten Knotens ab ('all' für alle Knoten)", metavar="NODE_NAME")
    parser.add_argument("--read-process-data", action="store_true", help="Liest Prozessdaten vom angegebenen Item")
    parser.add_argument("--start-time", dest="startTime", help="Startzeit für das Lesen von Prozessdaten (ISO-Format) (z.B., 2023-10-26T10:00:00)", metavar="TIMESTAMP")
    parser.add_argument("--end-time", dest="endTime", help="Endzeit für das Lesen von Prozessdaten (ISO-Format) (z.B., 2023-10-26T11:00:00)", metavar="TIMESTAMP")
    parser.add_argument("--get-item", action="store_true", help="Überprüft, ob das angegebene Item existiert")
    parser.add_argument("--create-node", dest="newNodeName", help="Erstellt einen neuen Knoten mit dem angegebenen Namen", metavar="NAME")
    parser.add_argument("--create-item", dest="newItemName", help="Erstellt ein neues Item mit dem angegebenen Namen", metavar="NAME")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ausführliche Ausgabe aktivieren")

    args = parser.parse_args()

    verify_ssl = args.verify_ssl
    verbose = args.verbose
    if verify_ssl:
        print("SSL-Zertifikatsprüfung aktiviert.")
    else:
        print("SSL-Zertifikatsprüfung deaktiviert.")

    if args.no_proxy:
        print("Option --no-proxy gesetzt. Proxy-Einstellungen werden ignoriert.")
        set_no_proxy()

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
            authenticateSession(args.serverRoot, args.apiKey, verify_ssl if verify_ssl else False, verbose)
        else:
            print("API Key nicht angegeben. Das Skript benötigt einen API Key für die Authentifizierung.")
            sys.exit(1)

        # Create a new node if --create-node is specified
        if args.newNodeName:
            check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            createNode(args.serverRoot, args.dbName, args.newNodeName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            sys.exit(0)

        # Create a new item if --create-item is specified
        if args.newItemName:
            check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            node_exists = check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            if node_exists:
                createItem(args.serverRoot, args.dbName, args.nodeName, args.newItemName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            else:
                print(f"Knoten '{args.nodeName}' nicht gefunden. Item kann nicht erstellt werden.")
            sys.exit(0)

        # Get node status if --get-node-status is specified
        if args.target_node_status:
            check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            if args.target_node_status.lower() == 'all':
                nodes = listNodes(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
                if nodes:
                    print(f"Status aller Knoten in Datenbank '{args.dbName}':")
                    for node in nodes:
                        status = getNodeStatus(args.serverRoot, args.dbName, node, args.apiKey, verify_ssl if verify_ssl else False, verbose)
                        if status is not None and not verbose:
                            print(f"NodeName: {status.get('ConnectionStatus', {}).get('NodeName')}")
                            print(f" ConnectionStatus : {status.get('ConnectionStatus', {}).get('ConnectionStatus')}")
                            print(f" ConnectionError: {status.get('ConnectionError')}")
                            print(f" LastUpdate: {status.get('LastUpdate')}")
                else:
                    print(f"Keine Knoten in Datenbank '{args.dbName}' gefunden.")
            else:
                node_exists = check_node_exists(args.serverRoot, args.dbName, args.target_node_status, args.apiKey, verify_ssl if verify_ssl else False, verbose)
                if node_exists:
                    status = getNodeStatus(args.serverRoot, args.dbName, args.target_node_status, args.apiKey, verify_ssl if verify_ssl else False, verbose)
                    if status is not None and not verbose:
                        print(f"NodeName: {status.get('ConnectionStatus', {}).get('NodeName')}")
                        print(f" ConnectionStatus : {status.get('ConnectionStatus', {}).get('ConnectionStatus')}")
                        print(f" ConnectionError: {status.get('ConnectionStatus', {}).get('ConnectionError')}")
                        print(f" LastUpdate: {status.get('ConnectionStatus', {}).get('LastUpdate')}")
                else:
                    print(f"Knoten '{args.target_node_status}' nicht gefunden.")
            sys.exit(0)

        # List nodes with status if --list-nodes is specified
        if args.list_nodes:
            check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            nodes = listNodes(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            if nodes:
                print(f"Verfügbare Knoten in Datenbank '{args.dbName}' und deren Status:")
                for node_name in nodes:
                    status = getNodeStatus(args.serverRoot, args.dbName, node_name, args.apiKey, verify_ssl if verify_ssl else False, verbose)
                    if status is not None and not verbose:
                        print(f"NodeName: {status.get('ConnectionStatus', {}).get('NodeName')}")
                        print(f" ConnectionStatus : {status.get('ConnectionStatus', {}).get('ConnectionStatus')}")
                        print(f" ConnectionError: {status.get('ConnectionStatus', {}).get('ConnectionError')}")
                        print(f" LastUpdate: {status.get('ConnectionStatus', {}).get('LastUpdate')}")
            else:
                print(f"Keine Knoten in Datenbank '{args.dbName}' gefunden.")
            sys.exit(0)

        # Check if the specified item exists
        if args.get_item:
            check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            node_exists = check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            if node_exists:
                found_item = getItem(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
                if found_item:
                    print(f"Item '{args.itemName}' gefunden in Knoten '{args.nodeName}'.")
                else:
                    print(f"Item '{args.itemName}' nicht gefunden in Knoten '{args.nodeName}'.")
            else:
                print(f"Knoten '{args.nodeName}' nicht gefunden.")
            sys.exit(0)

        # Verify the database exists and print the result
        found_database = check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
        if not found_database:
            print("Keine Datenbank gefunden. Beende.")
            sys.exit(-1)

        # Verify if the node exists and print the result
        found_node = check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
        if not found_node and not args.newNodeName and not args.newItemName: # Nur prüfen, wenn kein neuer Knoten oder Item erstellt wird
            print(f"Knoten '{args.nodeName}' nicht gefunden. Beende.")
            sys.exit(-1)
        elif not check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl if verify_ssl else False, verbose) and args.newItemName:
            print(f"Knoten '{args.nodeName}' nicht gefunden. Item kann nicht erstellt werden. Beende.")
            sys.exit(-1)

        # Verify if the item exists and print the result (this will now only run if --get-item or --create-item is not used)
        if not args.get_item and not args.newItemName:
            found_item = check_item_exists(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl if verify_ssl else False, verbose)
            if not found_item:
                print(f"Item '{args.itemName}' nicht gefunden. Beende.")
                sys.exit(-1)

        # Write data to the database
        # WriteProcessData(args.serverRoot, args.dbName, args.nodeName, args.itemName, ts, args.eventsToWrite, args.apiKey, verify_ssl if verify_ssl else False, verbose)

        # Database has been read. Pull back data from the configured item
        if args.read_process_data:
            ReadProcessData(args.serverRoot, args.dbName, args.nodeName, args.itemName, ts.isoformat(), te.isoformat(), args.apiKey, verify_ssl if verify_ssl else False, verbose)

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        sys.exit(1)