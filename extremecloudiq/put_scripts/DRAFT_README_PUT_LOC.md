# XIQ Location Creation Script

This Python script automates the creation of locations in ExtremeCloud IQ (XIQ) using data from a CSV file. It retrieves necessary IDs (organization, city, building, floor) via the XIQ API and then creates the locations with the correct parent-child relationships.

## Features

*   Securely handles XIQ API token management using environment variables.
*   Retrieves organization, city, building, and floor IDs dynamically.
*   Reads location data from a CSV file.
*   Creates locations in XIQ with appropriate parent IDs and address information.
*   Implements robust error handling and logging.

## Requirements

*   Python 3.6 or higher
*   `requests` library: `pip install requests`
*   Environment variables: `XIQ_API_SECRET`, `ADMIN_MAIL`, `XIQ_PASS`

## Setup

1.  **Install Python and `requests`:** If you don't have Python 3.6+ and `pip` installed, follow the instructions for your operating system. Then, install the `requests` library:

    ```bash
    pip install requests
    ```

2.  **Set Environment Variables:** Before running the script, set the following environment variables.  This is crucial for secure API key management.

    ```bash
    export XIQ_API_SECRET="your_actual_secret"
    export ADMIN_MAIL="your_admin_email"
    export XIQ_PASS="your_xiq_password"
    ```

    Replace the placeholder values with your actual XIQ credentials.

3.  **Create CSV File:** Create a CSV file named `locations.csv` (or whatever you specify in the `CSV_FILE` variable). The format of this file is critical and explained in detail below.

4.  **Save the Script:** Save the Python script to a file named `xiq_create_locations.py` (or any name you prefer).

5.  **Run the Script:** Execute the script from your terminal:

    ```bash
    python xiq_create_locations.py
    ```

## CSV File Format (`locations.csv`)

The CSV file **must** have the following columns in this exact order. The column names are case-sensitive:

| Column        | Description                                                                                                                                                                                                                                                           |
| :------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `location_id` | *(Optional)*: A unique identifier for the location. This can be left blank or used for your internal tracking. It's not used by the script.                                                                                                                            |
| `org_id`      | *(Optional)*: The ID of the organization. This can be left blank as the script will look it up based on `org_name`.                                                                                                                                                     |
| `org_name`    | **Required:** The name of the organization in XIQ. The script will use this to find the correct `org_id`.                                                                                                                                                               |
| `city_id`     | *(Optional)*: The ID of the city. This can be left blank as the script will look it up based on `city_name`.                                                                                                                                                           |
| `city_name`   | **Required:** The name of the city. The script will use this to find the correct `city_id`.                                                                                                                                                                               |
| `building_id` | *(Optional)*: The ID of the building. This can be left blank as the script will look it up based on `building_name`.                                                                                                                                                    |
| `building_name`| **Required:** The name of the building. The script will use this to find the correct `building_id`.                                                                                                                                                                    |
| `floor_id`    | *(Optional)*: The ID of the floor. This can be left blank as the script will look it up based on `floor_name`.                                                                                                                                                           |
| `floor_name`  | **Required:** The name of the floor. The script will use this to find the correct `floor_id`.                                                                                                                                                                            |

**Important:** The `org_name`, `city_name`, `building_name`, and `floor_name` values **must** match the names exactly as they appear in your XIQ instance.

**Example `locations.csv`:**

```csv
location_id,org_id,org_name,city_id,city_name,building_id,building_name,floor_id,floor_name
,,"My Organization",,"New York City",,"Main Building",,"1st Floor"
,,"My Organization",,"New York City",,"Main Building",,"2nd Floor"
,,"Another Org",,"London",,"Building A",,"Ground Floor"