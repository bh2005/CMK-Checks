import json
import argparse

def print_tree(node, level=0):
    """
    Rekursive Funktion zum Ausgeben der Baumstruktur.

    :param node: Der aktuelle Knoten im Baum.
    :param level: Das aktuelle Einrückungsniveau.
    """
    indent = "  " * level
    print(f"{indent}{node['name']} ({node['type']})")
    if 'children' in node and node['children']:
        for child in node['children']:
            print_tree(child, level + 1)

def main():
    """
    Hauptfunktion zum Lesen der JSON-Datei und Ausgeben der Baumstruktur.
    """
    parser = argparse.ArgumentParser(description="Gibt eine Baumstruktur aus einer JSON-Datei aus.")
    parser.add_argument('json_file', type=str, help='Pfad zur JSON-Datei')
    parser.add_argument('--help', action='help', help='Zeigt diese Hilfemeldung an und beendet das Programm')

    args = parser.parse_args()

    # JSON-Datei lesen
    with open(args.json_file, 'r') as file:
        data = json.load(file)

    # Baumstruktur ausgeben
    for item in data:
        print_tree(item)

if __name__ == "__main__":
    main()
