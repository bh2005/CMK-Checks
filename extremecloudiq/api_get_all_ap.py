import requests
import json
import os
import logging
from extremecloudiq import Configuration, ApiClient, DevicesApi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API-configuration (replace these values with your own)
API_KEY = os.environ.get("XIQ_API_KEY")
API_SECRET = os.environ.get("XIQ_API_SECRET")
XIQ_BASE_URL = https://api.extremecloudiq.com

def get_access_points_with_location():
    """Retrieves all access points with location information from the ExtremeCloud IQ API."""

    if not API_KEY or not API_SECRET:
        logger.error("API_KEY or API_SECRET environment variables not set.")
        return None

    try:
        # Configuration of the API-Clients
        configuration = Configuration(
            host=XIQ_BASE_URL,
            api_key={"Authorization": API_KEY},
            api_key_prefix={"Authorization": "Bearer"}
        )

        with ApiClient(configuration) as api_client:
            # Create an instance of the Devices API
            devices_api = DevicesApi(api_client)

            # Retrieve all devices (including access points)
            devices = devices_api.list_devices()
            
            access_points = []

            if devices and devices.data:
                for device in devices.data:
                    if device.type == "AP":  # Filters out only access points
                        location = device.location
                        access_points.append({
                            "serial_number": device.serial_number,
                            "name": device.name,
                            "model": device.model,
                            "location": location.name if location else "No location set" # Outputs the name of the location or “No location specified” if none exists
                        })
            else:
                logger.info("No devices found or error retrieving data.")
                return None

            return access_points

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"An error has occurred: {e}")
        return None

if __name__ == "__main__":
    access_points_with_location = get_access_points_with_location()

    if access_points_with_location:
        print(json.dumps(access_points_with_location, indent=4)) # Outputs the data formatted as JSON
    else:
        logger.info("No access points with location information found.")
