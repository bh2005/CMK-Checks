# HowTo: Using the xiq_redis_client.py Script

This document describes how to use the `xiq_redis_client.py` script to interact with the data stored in Redis from ExtremeCloud IQ (XIQ). This script allows you to search and display host information that was previously stored in Redis by another process (e.g., an XIQ API poller).

## Prerequisites

* **Python 3:** The script is written in Python 3. Ensure that Python 3 is installed on your system.
* **Redis Python Library:** The script uses the `redis` Python library to communicate with the Redis server. Install it using pip:
    ```bash
    pip install redis
    ```
* **Redis Server:** A running Redis server containing the XIQ data. The host and port information of the Redis server must be configured in the script (see Configuration).
* **XIQ Data in Redis:** It is assumed that XIQ device information is already stored in the Redis cache in a specific format. This script is designed to query this existing data.

## Configuration

Before using the script, you need to adjust the connection information for your Redis server within the script itself. Open `xiq_redis_client.py` and locate the following variables at the beginning of the file:


REDIS_HOST = "localhost"  # Default is localhost
REDIS_PORT = 6379        # Default Redis port
REDIS_DEVICE_DB = 0      # Database for device information


Adjust these variables to match your Redis server configuration.

## Usage

The script is called from the command line and provides various options for searching and displaying host information.

```bash
python xiq_redis_client.py [OPTIONS]
```

### Options

* `-f`, `--find-hosts`: Activates the host search mode in Redis. Must be used to apply search criteria.
* `-m`, `--managed_by <MANAGED_BY>`: Filters hosts by the value of the `managed_by` field (e.g., `XIQ`).
* `-l`, `--location-part <LOCATION_PART>`: Filters hosts whose location name contains the specified substring (case-insensitive).
* `--hostname-filter <HOSTNAME>`: Filters hosts by the hostname (substring search, case-insensitive).
* `--device-function <DEVICE_FUNCTION>`: Filters hosts by the device function (e.g., `AP`, `Switch`, case-insensitive).
* `--exact-match`: Enforces an exact match for all filter criteria (`managed_by`, `location-part`, `hostname-filter`, `device-function`). Without this option, a substring search is performed (case-insensitive).
* `-v`, `--verbose`: Activates verbose output. Displays additional debug information during the search (e.g., the Redis keys being scanned).

### Examples

1.  **Show all hosts:**
    ```bash
    python xiq_redis_client.py -f
    ```

2.  **Search for hosts managed by "XIQ":**
    ```bash
    python xiq_redis_client.py -f -m XIQ
    ```

3.  **Search for hosts with "Floor" in their location name:**
    ```bash
    python xiq_redis_client.py -f -l Floor
    ```

4.  **Search for hosts with the hostname "my-ap-01" (substring):**
    ```bash
    python xiq_redis_client.py -f --hostname-filter my-ap-01
    ```

5.  **Search for hosts with the device function "Switch" (exact match):**
    ```bash
    python xiq_redis_client.py -f --device-function Switch --exact-match
    ```

6.  **Search for hosts managed by "on-prem" and having "Building A" in their location name (substring search):**
    ```bash
    python xiq_redis_client.py -f -m on-prem -l "Building A"
    ```

7.  **Verbose search for hosts with the hostname "edge-switch-42":**
    ```bash
    python xiq_redis_client.py -f --hostname-filter edge-switch-42 -v
    ```

## Output

The script outputs a list of the found hosts to the console. For each matching host, the following information is displayed:

* ID
* Hostname
* MAC Address
* IP Address
* Managed By
* Device Function
* Locations (as a list of names)

## Troubleshooting

* **`redis.exceptions.ConnectionError`:** Ensure that the Redis server is running and that the connection information specified in the script variables `REDIS_HOST` and `REDIS_PORT` is correct.
* **No Output:** If the script does not find any hosts, double-check your search criteria and ensure that the XIQ data exists in Redis and that the fields you are searching for contain the expected values. Use the `-v` option to see which Redis keys are being scanned.
* **Incorrect Filtering:** Verify the case sensitivity and the use of `--exact-match` if your filters are not returning the expected results.

## Further Development

This script provides a basic way to query XIQ data stored in Redis. It can be extended as needed to include additional filter criteria, more formatted output, or interaction with other data in Redis.
```

This `HowTo.md` file should provide a good foundation for using the `xiq_redis_client.py` script. You can further customize or expand it as necessary.