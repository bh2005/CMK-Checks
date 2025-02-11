import requests
import json
import sys
import os
import logging

# Configure logging
logging.basicConfig(filename='smseagle.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_configuration(path):
    """Loads the configuration from the JSON file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error reading the configuration file: {path}")
        sys.exit(1)

def send_message(url, payload, headers, disable_ssl=False):
    """Sends a message to the SMS Eagle API."""
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=not disable_ssl)
        response.raise_for_status()  # Raise exception for HTTP error codes
        response_data = response.json()

        if response_data.get("status") == "queued":
            logging.info(f"Message sent successfully. Number: {response_data.get('number')}, ID: {response_data.get('id')}")
            return True, response_data
        else:
            logging.error(f"Error sending message: {response_data.get('message')}. Status Code: {response.status_code}. Response: {response.text}") # More details
            return False, response_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}. Response: {response.text if hasattr(response, 'text') else 'No response text available'}") # More details
        return False, None

def send_message_type(message_type, target, text=None, wave_id=None, disable_ssl=False, **kwargs):
    """Generic function to send different message types (SMS, TTS, Wave)."""
    target.update({"modem_no": kwargs.get("modem_no", 2)})

    if message_type == "sms":
        target.update({"text": text})
        url = url_sms
    elif message_type == "call_tts":
        target.update({"text": text, "voice_id": 1})
        url = url_call_tts
    elif message_type == "wave":
        target.update({"wave_id": wave_id})
        url = url_wave
    else:
        logging.error(f"Invalid message type: {message_type}")
        return False, None

    success, data = send_message(url, target, headers, disable_ssl)

    if not success:
        logging.info("Trying second server...")
        alternative_url = url.replace(config['smseagleip1'], config['smseagleip2'])
        alternative_headers = {'Content-Type': 'application/json', 'access-token': config['access-token2']}
        success, data = send_message(alternative_url, target, alternative_headers, disable_ssl)

    return success, data

def print_help():
    """Prints the help message."""
    help_text = """
    Usage:
        python smseagle_v2.py type=<type> [to=<number>] [contacts=<id1,id2,...>] [groups=<id1,id2,...>] [text=<message>] [wave-id=<id>] [modem_no=<number>] [--disable-ssl]

    Parameters:
        type         - Required. Type of message: 'sms', 'call_tts' or 'wave'.
        to           - Optional. Phone number for the message.
        contacts     - Optional. Contact IDs for the message.
        groups       - Optional. Group IDs for the message.
        text         - Required for 'sms' and 'call_tts'. Text of the message.
        wave-id      - Required for 'wave'. ID of the WAV file.
        modem_no     - Optional. Modem number. Default is 2.
        --disable-ssl - Optional. Disables SSL certificate verification (insecure!).

    Examples:
        # Send SMS to number and group (SSL enabled)
        python smseagle_v2.py type=sms to=+49123456789 groups=1,2 text="Hello World" modem_no=1

        # Send TTS call to contacts and group (SSL disabled)
        python smseagle_v2.py type=call_tts contacts=12,15 groups=3 text="This is a test." modem_no=1 --disable-ssl

        # Send Wave call (SSL enabled)
        python smseagle_v2.py type=wave groups=57,35 wave-id=2 modem_no=1
    """
    print(help_text)

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config = load_configuration(config_path)

    # API endpoints and tokens from the configuration
    url_sms = f"{config['smseagleip1']}/api/v2/messages/sms"
    url_call_tts = f"{config['smseagleip1']}/api/v2/calls/tts_advanced"
    url_wave = f"{config['smseagleip1']}/api/v2/calls/wave"
    access_token = config['access-token1']

    headers = {
        'Content-Type': 'application/json',
        'access-token': access_token
    }

    if len(sys.argv) < 2 or "help" in sys.argv:
        print_help()
        sys.exit(0)

    args = dict(arg.split('=') for arg in sys.argv[1:])

    action = args.get("type")
    text = args.get("text")
    wave_id = int(args.get("wave-id")) if "wave-id" in args else None
    modem_no = int(args.get("modem_no", 2))
    target = {"modem_no": modem_no}

    # Add recipients (combination of to, contacts, and groups)
    if "to" in args:
        target["to"] = [args["to"]]
    if "contacts" in args:
        target["contacts"] = [int(id) for id in args["contacts"].split(",")]
    if "groups" in args:
        target["groups"] = [int(id) for id in args["groups"].split(",")]

    # Check if at least one recipient is specified
    if not (target.get("to") or target.get("contacts") or target.get("groups")):
        print("Error: At least one of the parameters 'to', 'contacts', or 'groups' is required.")
        sys.exit(1)

    disable_ssl = "--disable-ssl" in sys.argv

    if action == "sms":
        success, data = send_message_type("sms", target, text=text, modem_no=modem_no, disable_ssl=disable_ssl)
    elif action == "call_tts":
        success, data = send_message_type("call_tts", target, text=text, modem_no=modem_no, disable_ssl=disable_ssl)
    elif action == "wave":
        success, data = send_message_type("wave", target, wave_id=wave_id, modem_no=modem_no, disable_ssl=disable_ssl)
    else:
        print("Invalid action. Use 'sms', 'call_tts', or 'wave'.")
        sys.exit(1)

    if success:
        print("Action performed successfully.")
        #print(data)  # For debugging: print complete data
    else:
        print("Action failed.")
        #print(data)  # For debugging: print complete data