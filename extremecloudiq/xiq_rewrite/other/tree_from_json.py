import json
import argparse

def print_tree(node, level=0, is_last=False, prefix=''):
    """
    Rekursive Funktion zum Ausgeben der Baumstruktur mit Strichen.

    :param node: Der aktuelle Knoten im Baum.
    :param level: Das aktuelle Einrückungsniveau.
    :param is_last: Gibt an, ob der Knoten das letzte Kind seines Elternknotens ist.
    :param prefix: Das Präfix für die Einrückung.
    """
    indent = "  " * level
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{node['id']} - {node['name']} ({node['type']})")

    if 'children' in node and node['children']:
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node['children']):
            is_last_child = (i == len(node['children']) - 1)
            print_tree(child, level + 1, is_last_child, new_prefix)

def main():
    """
    Hauptfunktion zum Lesen der JSON-Datei und Ausgeben der Baumstruktur.
    """
    parser = argparse.ArgumentParser(description="Gibt eine Baumstruktur aus einer JSON-Datei aus.")
    parser.add_argument('json_file', type=str, help='Pfad zur JSON-Datei')

    args = parser.parse_args()

    # JSON-Datei lesen
    with open(args.json_file, 'r') as file:
        data = json.load(file)

    # Baumstruktur ausgeben
    for item in data:
        print_tree(item)

if __name__ == "__main__":
    main()
