import ast
import json
import pprint

# Path to the text file containing the configuration section
config_file = './notifications.mk'

# Read the content of the file
with open(config_file, 'r') as file:
    config_section = file.read()

# Convert the content of the file to a Python data structure
config_data = ast.literal_eval(config_section)

# Now config_data contains your configuration section as a list of dictionaries in Python
# You can access individual elements as before
# print(config_data['description'])  # Print the description of the first element in the list
# print(config_data['description'])  # Print the description of the second element in the list
# print(config_data['description'])  # Print the description of the third element in the list

# Convert the configuration data to a JSON formatted string
config_json = json.dumps(config_data, indent=4)
print(config_json)
