# HowTo: Using the xiq_rest_client2.py Script

This document describes how to use the `xiq_rest_client2.py` script to interact with the ExtremeCloud IQ (XIQ) API and with data stored in Redis.

## Prerequisites

* **Python 3:** The script is written in Python 3. Ensure that Python 3 is installed on your system.
* **Requests Python Library:** The script uses the `requests` library for HTTP requests. Install it using pip:
    ```bash
    pip install requests
    ```
* **Redis Python Library:** For interacting with Redis, the `redis` library is required:
    ```bash
    pip install redis
    ```
* **API Token or XIQ Credentials:** You will need either a valid XIQ API token or your XIQ username and password for authentication.
* **Redis Server (optional):** Some features of the script require a running Redis server.

## Configuration

### API Authentication

The script offers several ways for API authentication:

1.  **API Token File (recommended):** Store your API token in a file (default is `xiq_api_token.txt`). The path can be specified using the `-k` or `--api_key_file` option.
2.  **Username and Password:** You can provide your XIQ username (`-u` or `--username`) and password (`-p` or `--password`) directly on the command line.
3.  **Creating a .env File:** Using the `--create-env` option, you can create a `.env` file with your username and password.

### Redis Connection

The Redis connection information is configured in the script in the `REDIS_HOST`, `REDIS_PORT`, and `REDIS_DEVICE_DB` (for devices) variables, and database 1 (for the Location Tree). Adjust these in the script if necessary.

## Usage

The script is called from the command line and provides various options for interacting with the XIQ API and Redis.

```bash
python xiq_rest_client2.py [OPTIONS]
```

### Options

#### Authentication Group

* `-k`, `--api_key_file <PATH>`: Path to the API token file (default: `xiq_api_token.txt`).
* `-u`, `--username <USERNAME>`: Username for the XIQ API.
* `-p`, `--password <PASSWORD>`: Password for the XIQ API.
* `--create-env`: Creates a `.env` file with the specified username and password.

#### API Retrieval Group

* `-s`, `--server <URL>`: Base URL of the XIQ API (default: `https://api.extremecloudiq.com`).
* `--get-devicelist`: Retrieves the list of devices.
* `--get-device-by-id <DEVICE_ID>`: Retrieves the details for a device with the specified ID.
* `--get-device-details-by-hostname <HOSTNAME>`: Retrieves the details for a device with the specified hostname (ID is retrieved from Redis).
* `-pp`, `--pretty-print`: Outputs device details in a readable format (applies to `--get-device-by-id` and `--get-device-details-by-hostname`).
* `--get-device-status <LOCATION_ID>`: Retrieves the device status overview for the specified location ID.
* `--get-locations-tree`: Retrieves the Location Tree and stores it in Redis (db=1).
* `--find-location <SEARCH_TERM>`: Searches for a location in the Location Tree (Redis db=1) and outputs `unique_name` and `id`.

#### Redis Interaction Group

* `--get-device-by-hostname <HOSTNAME>`: Retrieves the details for a device with the specified hostname from Redis.
* `-f`, `--find-hosts`: Searches for hosts in Redis based on optional criteria.
* `-m`, `--managed_by <MANAGED_BY>`: Optional: Filter for `managed_by` during the Redis search.
* `-l`, `--location-part <LOCATION_PART>`: Optional: Part of the location name for the Redis search.
* `--hostname-filter <HOSTNAME>`: Optional: Hostname for the Redis search.
* `--device-function <DEVICE_FUNCTION>`: Optional: Filter for the device function (e.g., `AP`, `Switch`).
* `--exact-match`: Uses an exact match for the filters in the Redis search.
* `--store-redis`: Stores the device information (from `--get-devicelist`) in Redis (db=0).

#### Output Options

* `-o`, `--output_file <FILENAME>`: Filename for outputting the device list (JSON, default: `XiqDeviceList.json`).
* `--show-pretty`: Displays a simplified output of devices (id, hostname, mac, ip) on the console (for `--get-devicelist`).
* `--output-csv <FILENAME>`: Filename for outputting the device list as CSV (for `--get-devicelist`).

#### Miscellaneous Options

* `-v`, `--verbose`: Enables verbose output.

### Examples

#### API Retrieval

1.  **Retrieve the device list and save it as JSON:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist -o my_devices.json
    ```

2.  **Retrieve the device list and display a simplified output on the console:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist --show-pretty
    ```

3.  **Retrieve the device list and save it as CSV:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist --output-csv devices.csv
    ```

4.  **Retrieve details for a device with the ID `917843101234567`:**
    ```bash
    ./xiq_rest_client2.py --get-device-by-id 917843101234567
    ```

5.  **Retrieve details for a device with the ID `917843101234567` and output in a pretty format:**
    ```bash
    ./xiq_rest_client2.py --get-device-by-id 917843101234567 -pp
    ```

6.  **Retrieve details for a device with the hostname `my-ap-01` (ID from Redis):**
    ```bash
    ./xiq_rest_client2.py --get-device-details-by-hostname my-ap-01
    ```

7.  **Retrieve details for a device with the hostname `my-ap-01` and output in a pretty format (ID from Redis):**
    ```bash
    ./xiq_rest_client2.py --get-device-details-by-hostname my-ap-01 -pp
    ```

8.  **Retrieve the device status for the location ID `917843101234568`:**
    ```bash
    ./xiq_rest_client2.py --get-device-status 917843101234568
    ```

9.  **Retrieve the Location Tree and store it in Redis:**
    ```bash
    ./xiq_rest_client2.py --get-locations-tree
    ```

10. **Search for a location with the name part "Office":**
    ```bash
    ./xiq_rest_client2.py --find-location Office
    ```

#### Redis Interaction

1.  **Retrieve details for a device with the hostname `another-ap-02` directly from Redis:**
    ```bash
    ./xiq_rest_client2.py --get-device-by-hostname another-ap-02
    ```

2.  **Show all hosts in Redis:**
    ```bash
    ./xiq_rest_client2.py -f
    ```

3.  **Search for hosts in Redis managed by "on-premise":**
    ```bash
    ./xiq_rest_client2.py -f -m on-premise
    ```

4.  **Search for hosts in Redis that have "Warehouse" in their location name:**
    ```bash
    ./xiq_rest_client2.py -f -l Warehouse
    ```

5.  **Search for hosts in Redis with the exact hostname "switch-05":**
    ```bash
    ./xiq_rest_client2.py -f --hostname-filter switch-05 --exact-match
    ```

6.  **Store device information (after retrieving it with `--get-devicelist`) in Redis:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist --store-redis
    ```

#### Miscellaneous Options

1.  **Enable verbose output:**
    ```bash
    ./xiq_rest_client2.py --get-devicelist -v
    ./xiq_rest_client2.py --get-device-details-by-hostname my-ap-01 -pp -v
    ```

## Output

The output of the script depends on the option used:

* **`--get-devicelist`:**
    * Without further options, a list of device objects in JSON format is output to the console.
    * With `-o <FILENAME>`, the device information is written as JSON to the specified file.
    * With `--show-pretty`, a simplified list of devices with ID, hostname, MAC address, and IP address is displayed on the console.
    * With `--output-csv <FILENAME>`, the device information is written as CSV to the specified file (the columns may vary depending on the data retrieved).

* **`--get-device-by-id <DEVICE_ID>`:**
    * Outputs the detailed information for the specified device in JSON format to the console.
    * With `-pp`, a formatted, more readable output of the key device information is displayed (ID, hostname, MAC address, IP address, device function, managed by, locations).

* **`--get-device-details-by-hostname <HOSTNAME>`:**
    * First retrieves the device ID for the specified hostname from Redis and then queries the API for the details. The output is identical to that of `--get-device-by-id`.
    * With `-pp`, the formatted output is also displayed.
    * If the device ID is not found in Redis, a corresponding message is output.

* **`--get-device-status <LOCATION_ID>`:**
    * Outputs an overview of the device status for the specified location ID in JSON format to the console. The exact fields may vary.

* **`--get-locations-tree`:**
    * Outputs a success message if the Location Tree is successfully retrieved from the API and stored in Redis. Error messages are displayed in case of failure.

* **`--find-location <SEARCH_TERM>`:**
    * Outputs a list of the locations found in Redis that contain the search term in their name. For each location found, the `unique_name` and `id` are displayed.
    * If no matching locations are found, a corresponding message is output.

* **`--get-device-by-hostname <HOSTNAME>` (Redis):**
    * Outputs the detailed information for the device with the specified hostname directly from Redis in JSON format to the console.
    * If the hostname is not found in Redis, a corresponding message is output.

* **`-f`, `--find-hosts` (Redis):**
    * Outputs a list of the hosts found in Redis that match the specified filter criteria. For each host, the ID, hostname, MAC address, IP address, managed by, device function, and the list of locations are displayed.
    * If no matching hosts are found, a corresponding message is output.

* **`-v`, `--verbose`:**
    * Enables additional messages on the console that show the script's progress and any debug information in more detail.

The exact structure of the JSON output may vary depending on the specific API endpoint. The formatted output (`-pp`) aims to present the most important device information in a human-readable format.

## Troubleshooting

* **Invalid API Token:**
    * Ensure that the API token stored in the specified token file (`xiq_api_token.txt` or the path specified with `-k`) is valid.
    * Check if the token has expired.
    * If you are using username and password, make sure they are correct.
    * Check the error messages in the script's output regarding authentication.

* **Failed to Connect to the XIQ API:**
    * Check your internet connection.
    * Ensure that the base URL of the XIQ API (`-s` or default value) is correct.
    * Firewalls or proxies might be preventing the connection. Check your network settings.

* **Error Retrieving Data (HTTP Status Codes):**
    * If the script outputs error messages with HTTP status codes (e.g., 401 Unauthorized, 404 Not Found, 500 Internal Server Error), this indicates a problem with the API request.
        * **401 Unauthorized:** Check your API token or credentials.
        * **404 Not Found:** The requested resource (e.g., device ID, location ID) might not exist. Verify the IDs.
        * **500 Internal Server Error:** There was a server-side issue with ExtremeCloud IQ. Try again later.
    * Enable verbose mode (`-v`) to see more detailed error messages and the URLs being sent.

* **Redis Connection Issues:**
    * If functions that use Redis (`--get-device-by-hostname`, `-f`, `--get-locations-tree`, `--find-location`, `--store-redis`, `--get-device-details-by-hostname`) fail:
        * Ensure that the Redis server is running and reachable from your system.
        * Check the connection information configured in the script variables `REDIS_HOST` and `REDIS_PORT`.
        * Make sure the Redis Python library (`redis`) is installed.
        * Check for error messages related to `redis.exceptions.ConnectionError`.

* **No Data Found:**
    * If queries return no results, double-check your search criteria (e.g., device ID, hostname, location name).
    * For Redis searches, ensure that the data actually exists in Redis and that the filters are applied correctly (use `--exact-match` if needed).

* **Error Saving to Files:**
    * If errors occur while writing to the output file (`-o`, `--output-csv`), check the script's permissions to create and write files in the specified path.
    * Ensure that the specified filename is valid.

* **Unexpected Errors:**
    * Enable verbose mode (`-v`) to get more detailed information about the script's execution and any potential Python error messages (tracebacks). These can be very helpful in diagnosing problems.

* **Incorrect or Incomplete Output:**
    * Check the XIQ API documentation to ensure that the expected data fields are actually included in the response.
    * If you are using the formatted output (`-pp`), note that only a selection of the most important fields is displayed. Use the standard output to see all available data.

If you continue to have problems, enable verbose mode (`-v`) and share the complete output of the script along with the command you used and a description of the issue.

## Further Development

Let's see what else the API offers!
```