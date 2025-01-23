#!/usr/bin/env python3

import requests
import json
import os
import getpass  # For secure password input
import sys

def generate_xiq_api_key(username, password):
    """Generates an ExtremeCloud IQ API key.

    Args:
        username: The ExtremeCloud IQ username.
        password: The ExtremeCloud IQ password.

    Returns:
        The API key as a string or None in case of failure.
    """
    url = "https://api.extremecloudiq.com/login"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Check for HTTP errors (e.g., 400, 500)
        json_response = response.json()
        api_key = json_response.get("access_token")

        if not api_key:
            print("Error: Could not extract API key from the response. Check the JSON format of the response.", file=sys.stderr)
            print(json_response, file=sys.stderr)
            return None
        return api_key

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}", file=sys.stderr)
        if response is not None:
            print(f"Server response text: {response.text}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}", file=sys.stderr)
        return None

def get_token_length(token):
    """Returns the length of the token."""
    return len(token)

def update_bashrc(api_key):
    """Updates the ~/.bashrc file to set the XIQ_API_SECRET environment variable."""
    bashrc_path = os.path.expanduser("~/.bashrc")
    env_var_entry = f'export XIQ_API_SECRET="{api_key}"\n'

    # Read the current content of ~/.bashrc
    with open(bashrc_path, 'r') as bashrc:
        lines = bashrc.readlines()

    # Check if the environment variable is already set and update it
    with open(bashrc_path, 'w') as bashrc:
        var_set = False
        for line in lines:
            if line.startswith('export XIQ_API_SECRET='):
                bashrc.write(env_var_entry)
                var_set = True
            else:
                bashrc.write(line)
        
        # If the variable was not set, add it to the end
        if not var_set:
            bashrc.write(env_var_entry)

if __name__ == "__main__":
    username = os.getenv('ADMIN_MAIL')
    if not username:
        print("Environment variable ADMIN_MAIL is not set", file=sys.stderr)
        exit(1)
    
    password = getpass.getpass("ExtremeCloud IQ password: ")

    api_key = generate_xiq_api_key(username, password)

    if api_key:
        # Output the token to stdout
        print(f"API key: {api_key}")

        # Write the token to the file extrem_token
        with open('extrem_token', 'w') as file:
            file.write(api_key)

        # Set the environment variable XIQ_API_SECRET
        os.environ["XIQ_API_SECRET"] = api_key

        # Output the length of the token
        token_length = get_token_length(api_key)
        print(f"Length of the API key: {token_length}")

        print("API key has been generated and saved in the file 'extrem_token'.")
        print("Environment variable XIQ_API_SECRET has been set.")
        
        # Check the environment variable and its length
        env_var_value = os.getenv('XIQ_API_SECRET')
        env_var_length = get_token_length(env_var_value) if env_var_value else 0
        print(f"XIQ_API_SECRET: {env_var_value}")
        print(f"Length of XIQ_API_SECRET: {env_var_length}")
        
        # Update ~/.bashrc to export the environment variable for all processes
        update_bashrc(api_key)
        
    else:
        print("Failed to generate the API key.", file=sys.stderr)
        exit(1)