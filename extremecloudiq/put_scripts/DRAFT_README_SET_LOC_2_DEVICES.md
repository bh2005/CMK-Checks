# XIQ Device Location Assignment Script

This Python script automates the assignment of locations to devices in ExtremeCloud IQ (XIQ) using data from a CSV file. It reads device IDs, location IDs, and coordinates from the CSV and uses the XIQ API to update device locations.

## Features

*   Securely handles XIQ API token management using environment variables.
*   Reads device and location data from a CSV file.
*   Assigns locations to devices in XIQ with provided coordinates.
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

2.  **Set Environment Variables:** Before running the script, set the following environment variables. This is crucial for secure API key management.

    ```bash
    export XIQ_API_SECRET="your_actual_secret"
    export ADMIN_MAIL="your_admin_email"
    export XIQ_PASS="your_xiq_password"
    ```

    Replace the placeholder values with your actual XIQ credentials.

3.  **Create CSV File:** Create a CSV file named `devices_locations.csv` (or whatever you specify in the `CSV_FILE` variable). The format of this file is critical and explained in detail below.

4.  **Save the Script:** Save the Python script to a file named `xiq_assign_device_locations.py` (or any name you prefer).

5.  **Run the Script:** Execute the script from your terminal:

    ```bash
    python xiq_assign_device_locations.py
    ```

## CSV File Format (`devices_locations.csv`)

The CSV file **must** have the following columns in this *exact* order. The column names are case-sensitive:

id, location_id, x, y, latitude, longitude

sample CSV
```bash
id,location_id,x,y,latitude,longitude
1,67890,100,200,50.1109,8.6821
2,78901,150,250,48.8566,2.3522
3,89012,200,300,51.5074,-0.1278
```