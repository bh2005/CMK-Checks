# ExtremeCloud IQ Device List Puller

This script fetches device information from ExtremeCloud IQ via its API, processes the data, and exports it to both JSON and CSV formats.

## Description

The script performs the following operations:
- Authenticates with ExtremeCloud IQ using environment variables
- Retrieves device information paginated (100 devices per page)
- Saves raw JSON data for each page
- Combines all device data into a single JSON file
- Converts the data to CSV format
- Includes automatic token renewal functionality
- Shows progress bars during operation
- Maintains detailed logging

## Prerequisites

### Required Python Packages
```bash
pip install requests
pip install tqdm
```
## Environment Variables
The following environment variables must be set:

- ADMIN_MAIL: Your ExtremeCloud IQ account email

- XIQ_PASS: Your ExtremeCloud IQ password

- XIQ_API_SECRET: Your API token (will be auto-generated if not present)

Add to your .bashrc:

    export ADMIN_MAIL="your-email@example.com"
    export XIQ_PASS="your-password"
    export XIQ_API_SECRET="your-api-token"  # Optional

## Usage
Basic usage:

    python xiq_pull_devices_list.py


With debug output:

    python xiq_pull_devices_list.py --debug
    
With custom views:

    python xiq_pull_devices_list.py --views FULL
    
## Command Line Arguments
--views: Views parameter for the API request (default: "FULL")

--debug: Enable debug output

## Output Files
The script generates several files:

- raw_devices_page_*.json: Raw JSON responses for each page (temporary)

- devices.json: Combined JSON data for all devices

- output_extreme_api.csv: Final CSV output with formatted device data

## CSV Output Fields
id,create_time,update_time,serial_number,mac_address,device_function,product_type,hostname,ip_address,software_version,device_admin_state,connected,last_connect_time,network_policy_name,network_policy_id,primary_ntp_server_address,primary_dns_server_address,subnet_mask,default_gateway,ipv6_address,ipv6_netmask,simulated,display_version,location_id,org_id,org_name,city_id,city_name,building_id,building_name,floor_id,floor_name,country_code,description,remote_port_id,remote_system_id,remote_system_name,local_interface,system_up_time,config_mismatch,managed_by,thread0_eui64,thread0_ext_mac


Device ID       **! KEY indicator !**

Creation Time

Update Time     **! not in ms it`s the latest unix timestamp where the device was comming up !**

Serial Number

MAC Address

Device Function

Product Type

Hostname

IP Address

Software Version

Device Admin State

Connection Status

Last Connect Time

Network Policy Details

NTP/DNS Configuration

Location Information

LLDP/CDP Information

System Uptime

And more...

## Logging
The script logs its operations to xiq_api.log, including:

- API request status

- Number of devices found

- File operations

- Errors and warnings

Error Handling
The script includes comprehensive error handling for:

- API authentication failures

- Network connectivity issues

- Token expiration and renewal

- File operations

- Data processing errors

## Cleanup
After successful execution, the script automatically:

- Removes temporary raw JSON files

- Maintains only the final JSON and CSV outputs

## Notes
- The script uses a 3-second delay between API requests to prevent rate limiting

- Token renewal is automatic if the current token expires

- Progress bars show real-time status of data retrieval and processing

## To install the man page on a Linux system:

1. First, compress the man page:

    gzip -k xiq_pull_devices_list.1

2. Copy the compressed man page to the appropriate directory:

    sudo cp xiq_pull_devices_list.1.gz /usr/share/man/man1/

3. Update the man page database:

    sudo mandb
    
You can then view the man page using:

    man xiq_pull_devices_list
    
he man page includes:

1. Name and synopsis
2. Detailed description
3. Command-line options
4. Environment variables
5. File descriptions
6. Output format
7. Examples
8. Diagnostic information
9. Notes and bugs sections
10. Author and copyright information

This provides users with a standard Unix-style reference that can be accessed directly from the command line.
