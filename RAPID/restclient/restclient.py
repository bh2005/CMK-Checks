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


def authenticateSession(serverRoot, apiKey, verify_cert=True):
    """Authorisiert die Session mit einem API-Schlüssel."""
    headers['Authorization'] = f'Bearer {apiKey}'
    response = session.get(f"{serverRoot}/auth?format=json", headers=headers, verify=verify_cert)
    if response.status_code != 200:
        raise Exception("Unauthorized session")
    else:
        print("Session authenticated successfully")


def getDatabase(requestUri, dbName, apiKey, verify_cert=True):
    """Ruft die Datenbankliste ab und prüft, ob die angegebene Datenbank existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database mit Headern: {headers_copy}")
    response = session.get(f"{requestUri}/api/v1/database", headers=headers_copy, verify=verify_cert)
    print(f"Antwort-Statuscode (getDatabase): {response.status_code}")
    if response.status_code == 200:
        databases = json.loads(response.text)
        print(f"Antwort-Body (getDatabase): {databases}")
        for db_url in databases:
            # Extrahiere den Datenbanknamen aus der URL
            db = db_url.split('/')[-1]
            if db == dbName:
                print(f"Gefundene Datenbank (getDatabase): {db}")
                return db
        raise Exception(f"Database not found: {dbName}")
    else:
        raise Exception(f"Error fetching database list: {response.status_code}")


def getNode(requestUri, dbName, nodeName, apiKey, verify_cert=True):
    """Ruft die Knotenliste für eine Datenbank ab und prüft, ob der angegebene Knoten existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database/{dbName}/node mit Headern: {headers_copy}")
    response = session.get(f"{requestUri}/api/v1/database/{dbName}/node", headers=headers_copy, verify=verify_cert)
    print(f"Antwort-Statuscode (getNode): {response.status_code}")
    if response.status_code == 200:
        nodesList = json.loads(response.text)
        print(f"Antwort-Body (getNode): {nodesList}")
        for node_url in nodesList:
            node = node_url.split('/')[-1]  # Extrahiere den letzten Teil des Pfads
            if node == nodeName:
                print(f"Gefundener Knoten (getNode): {node}")
                return node
        return ""  # Knoten nicht gefunden
    else:
        raise Exception(f"Error fetching node list: {response.status_code}")


def getNodeStatus(requestUri, dbName, nodeName, apiKey, verify_cert=True):
    """Ruft den Status eines einzelnen Knotens ab."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    status_url = f"{requestUri}/api/v1/nodeconnections/database/{dbName}/node/{nodeName}/status"
    print(f"Sende GET-Anfrage an: {status_url} mit Headern: {headers_copy}")
    response = session.get(status_url, headers=headers_copy, verify=verify_cert)
    print(f"Antwort-Statuscode (getNodeStatus) für Knoten '{nodeName}': {response.status_code}")
    if response.status_code == 200:
        status_data = json.loads(response.text)
        print(f"Status für Knoten '{nodeName}': {status_data.get('ConnectionStatus')}")
        return status_data
    else:
        print(f"Fehler beim Abrufen des Status für Knoten '{nodeName}': {response.status_code}")
        return None


def listNodes(requestUri, dbName, apiKey, verify_cert=True):
    """Ruft die Knotenliste für eine Datenbank ab und gibt sie mit Status aus."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    nodes_url = f"{requestUri}/api/v1/database/{dbName}/node"
    print(f"Sende GET-Anfrage an: {nodes_url} mit Headern: {headers_copy}")
    response = session.get(nodes_url, headers=headers_copy, verify=verify_cert)
    print(f"Antwort-Statuscode (listNodes): {response.status_code}")
    if response.status_code == 200:
        nodesList = json.loads(response.text)
        print(f"Verfügbare Knoten in Datenbank '{dbName}' und deren Status:")
        for node_url in nodesList:
            nodeName = node_url.split('/')[-1]
            getNodeStatus(requestUri, dbName, nodeName, apiKey, verify_cert)
        return True
    else:
        raise Exception(f"Fehler beim Abrufen der Knotenliste: {response.status_code}")


def createNode(requestUri, dbName, nodeName, apiKey, verify_cert=True):
    """Erstellt einen neuen Knoten."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"Name": nodeName, "Type": 2}
    print(f"Sende POST-Anfrage an: {requestUri}/api/v1/database/{dbName}/node?format=json mit Headern: {headers_copy}, Daten: {payload}")
    response = session.post(f"{requestUri}/api/v1/database/{dbName}/node?format=json", headers=headers_copy, json=payload, verify=verify_cert)
    print(f"Antwort-Statuscode (createNode): {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Unable to create node: {response.text}")
    else:
        print(f"Node: {nodeName} created")


def getItem(requestUri, dbName, nodeName, itemName, apiKey, verify_cert=True):
    """Ruft die Itemliste für einen Knoten ab und prüft, ob das angegebene Item existiert."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    print(f"Sende GET-Anfrage an: {requestUri}/api/v1/database/{dbName}/node/{nodeName}/item mit Headern: {headers_copy}")
    response = session.get(f"{requestUri}/api/v1/database/{dbName}/node/{nodeName}/item", headers=headers_copy, verify=verify_cert)
    print(f"Antwort-Statuscode (getItem): {response.status_code}")
    if response.status_code == 200:
        itemsList = json.loads(response.text)
        print(f"Antwort-Body (getItem): {itemsList}")
        for entry in itemsList:
            item = entry.split('/')[-1]
            if item == itemName:
                print(f"Gefundenes Item (getItem): {item}")
                return item
        return ""  # Item nicht gefunden
    else:
        raise Exception(f"Error fetching item list: {response.status_code}")


def createItem(requestUri, dbName, nodeName, itemName, apiKey, verify_cert=True):
    """Erstellt ein neues Item."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"DbName": dbName, "NodeName": nodeName, "Name": itemName, "Description": "Test Item"}
    print(f"Sende POST-Anfrage an: {requestUri}/api/v1.1/item?format=json mit Headern: {headers_copy}, Daten: {payload}")
    response = session.post(f"{requestUri}/api/v1.1/item?format=json", headers=headers_copy, json=payload, verify=verify_cert)
    print(f"Antwort-Statuscode (createItem): {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Unable to create item: {response.text}")
    else:
        print(f"Item: {itemName} created")


def ReadProcessData(requestUri, dbName, nodeName, itemName, ts, te, apiKey, verify_cert=True):
    """Liest Prozessdaten."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {"Aggregate": 0, "StartTime": ts, "EndTime": te}
    print(f"Sende PUT-Anfrage an: {requestUri}/api/v1/database/{dbName}/node/{nodeName}/item/{itemName}/processdata?format=json mit Headern: {headers_copy}, Daten: {payload}")
    response = session.put(f"{requestUri}/api/v1/database/{dbName}/node/{nodeName}/item/{itemName}/processdata?format=json",
                           headers=headers_copy,
                           data=json.dumps(payload),
                           verify=verify_cert)
    print(f"Antwort-Statuscode (ReadProcessData): {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        countValues = 0
        print("Data Fetched")
        print("------------")
        for s in data['ProcessData']:
            timestamp = s.get('EventTime')
            value = s.get('EventValue')['Value']
            print(f"{timestamp}: {value}")
            countValues += 1
        print(f"{countValues} values fetched")
    else:
        print(f"Error reading process data: {response.status_code} - {response.content.decode()}")


def WriteProcessData(serverRoot, dbName, nodeName, itemName, ts, eventsCount, apiKey, verify_cert=True):
    """Schreibt Prozessdaten."""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = f'Bearer {apiKey}'
    payload = {
        "ItemName": itemName,
        "MoreData": False,
        "SessionId": 0,
        "Data": []
    }
    print(f"Sende POST-Anfrage an: {serverRoot}/api/v1.1/database/{dbName}/node/{nodeName}/itemdata/processdata?format=json mit Headern: {headers_copy}, Daten: {payload}")
    eventTime = ts
    for eventIndex in range(eventsCount):
        processDataPoint = {"SerialisedValue": str(eventIndex), "IsNull": False}
        eventToWrite = {
            "EventTime": eventTime.isoformat(),
            "EventValue": processDataPoint,
            "Quality": 192
        }
        payload["Data"].append(eventToWrite)
        eventTime += datetime.timedelta(milliseconds=1)

    response = session.post(f"{serverRoot}/api/v1.1/database/{dbName}/node/{nodeName}/itemdata/processdata?format=json",
                           headers=headers_copy,
                           json=payload,
                           verify=verify_cert)
    print(f"Antwort-Statuscode (WriteProcessData): {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Unable to create process data: {response.text}")
    else:
        print(f"{eventsCount} events written to {itemName}")


def check_database_exists(serverRoot, dbName, apiKey, verify_cert):
    """Überprüft, ob die Datenbank existiert und gibt den Namen zurück oder None."""
    try:
        headers_copy = headers.copy()
        headers_copy['Authorization'] = f'Bearer {apiKey}'
        print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database mit Headern: {headers_copy}")
        response = session.get(f"{serverRoot}/api/v1/database", headers=headers_copy, verify=verify_cert)
        print(f"Antwort-Statuscode (check_database_exists): {response.status_code}")
        if response.status_code == 200:
            databases = json.loads(response.text)
            print(f"Antwort-Body (check_database_exists): {databases}")
            for db_url in databases:
                db = db_url.split('/')[-1]
                if db == dbName:
                    print(f"Gefundene Datenbank: {db}")
                    return db
            raise Exception(f"Database not found: {dbName}")
        else:
            raise Exception(f"Error fetching database list: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Überprüfen der Datenbank: {e}")
        return None


def check_node_exists(serverRoot, dbName, nodeName, apiKey, verify_cert):
    """Überprüft, ob der Knoten existiert und gibt den Namen zurück oder None."""
    try:
        headers_copy = headers.copy()
        headers_copy['Authorization'] = f'Bearer {apiKey}'
        print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database/{dbName}/node mit Headern: {headers_copy}")
        response = session.get(f"{serverRoot}/api/v1/database/{dbName}/node", headers=headers_copy, verify=verify_cert)
        print(f"Antwort-Statuscode (check_node_exists): {response.status_code}")
        if response.status_code == 200:
            nodesList = json.loads(response.text)
            print(f"Antwort-Body (check_node_exists): {nodesList}")
            for node_url in nodesList:
                node = node_url.split('/')[-1]  # Extrahiere den letzten Teil des Pfads
                if node == nodeName:
                    print(f"Gefundener Knoten: {node}")
                    return node
            return None  # Knoten nicht gefunden (leere Zeichenkette wird nicht als gefunden interpretiert)
        else:
            raise Exception(f"Error fetching node list: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Überprüfen des Knotens: {e}")
        return None


def check_item_exists(serverRoot, dbName, nodeName, itemName, apiKey, verify_cert):
    """Überprüft, ob das Item existiert und gibt den Namen zurück oder None."""
    try:
        headers_copy = headers.copy()
        headers_copy['Authorization'] = f'Bearer {apiKey}'
        print(f"Sende GET-Anfrage an: {serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item mit Headern: {headers_copy}")
        response = session.get(f"{serverRoot}/api/v1/database/{dbName}/node/{nodeName}/item", headers=headers_copy, verify=verify_cert)
        print(f"Antwort-Statuscode (check_item_exists): {response.status_code}")
        if response.status_code == 200:
            itemsList = json.loads(response.text)
            print(f"Antwort-Body (check_item_exists): {itemsList}")
            for entry in itemsList:
                item = entry.split('/')[-1]
                if item == itemName:
                    print(f"Gefundenes Item: {item}")
                    return item
            return None  # Item nicht gefunden (leere Zeichenkette wird nicht als gefunden interpretiert)
        else:
            raise Exception(f"Error fetching item list: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Überprüfen des Items: {e}")
        return None


if __name__ == '__main__':
    # Setze die Umgebungsvariable PATH, falls sie nicht gesetzt ist (kann in manchen Umgebungen notwendig sein)
    if 'PATH' not in os.environ:
        os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

    # Entferne Proxy-Einstellungen
    set_no_proxy()

    # Set parameters for the query
    parser = ArgumentParser(description="Interact with a REST API to manage databases, nodes, and items.")
    parser.add_argument("-s", "--server", dest="serverRoot", help="Server address (e.g., https://yourserver:3001)", default="https://localhost:3001", metavar="URL")
    parser.add_argument("-k", "--apiKey", dest="apiKey", help="API Key for authentication", default=os.getenv('API_KEY'), required=True, metavar="KEY")
    parser.add_argument("-db", "--dbName", dest="dbName", help="Target database name (default: DB1)", default="DB1", metavar="NAME")
    parser.add_argument("-n", "--nodeName", dest="nodeName", help="Target node name (e.g., 'SensorData')", default="PythonRestClient", metavar="NAME")
    parser.add_argument("-i", "--itemName", dest="itemName", help="Target item name (e.g., 'Temperature')", default="RandomData-" + str(random.randint(1, 100001)), metavar="NAME")
    parser.add_argument("-e", "--eventsToWrite", dest="eventsToWrite", help="Number of events to write (default: 10)", default=10, type=int, metavar="COUNT")
    parser.add_argument("--no-proxy", action="store_true", help="Disable the use of proxies.")
    parser.add_argument("--verify-ssl", action="store_true", help="Enable SSL certificate verification.")
    parser.add_argument("--list-nodes", action="store_true", help="List all nodes in the specified database with their status.")

    args = parser.parse_args()

    verify_ssl = args.verify_ssl
    if verify_ssl:
        print("SSL-Zertifikatsprüfung aktiviert.")
    else:
        print("SSL-Zertifikatsprüfung deaktiviert.")

    if args.no_proxy:
        print("Option --no-proxy gesetzt. Proxy-Einstellungen werden ignoriert.")
        set_no_proxy()

    ts = (datetime.datetime.now() + datetime.timedelta(milliseconds=-args.eventsToWrite))
    te = datetime.datetime.now()

    try:
        # Create an authenticated session
        if args.apiKey:
            authenticateSession(args.serverRoot, args.apiKey, verify_ssl if verify_ssl else False)
        else:
            print("API Key nicht angegeben. Das Skript benötigt einen API Key für die Authentifizierung.")
            sys.exit(1)

        # List nodes with status if --list-nodes is specified
        if args.list_nodes:
            check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False)
            listNodes(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False)
            sys.exit(0)

        # Verify the database exists and print the result
        found_database = check_database_exists(args.serverRoot, args.dbName, args.apiKey, verify_ssl if verify_ssl else False)
        if not found_database:
            print("Keine Datenbank gefunden. Beende.")
            sys.exit(-1)

        # Verify if the node exists and print the result
        found_node = check_node_exists(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl if verify_ssl else False)
        if not found_node:
            createNode(args.serverRoot, args.dbName, args.nodeName, args.apiKey, verify_ssl if verify_ssl else False)

        # Verify if the item exists and print the result
        found_item = check_item_exists(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl if verify_ssl else False)
        if not found_item:
            createItem(args.serverRoot, args.dbName, args.nodeName, args.itemName, args.apiKey, verify_ssl if verify_ssl else False)

        # Write data to the database
        WriteProcessData(args.serverRoot, args.dbName, args.nodeName, args.itemName, ts, args.eventsToWrite, args.apiKey, verify_ssl if verify_ssl else False)

        # Database has been read. Pull back data from the configured item
        ReadProcessData(args.serverRoot, args.dbName, args.nodeName, args.itemName, ts.isoformat(), te.isoformat(), args.apiKey, verify_ssl if verify_ssl else False)

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        sys.exit(1)