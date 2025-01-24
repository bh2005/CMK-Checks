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

Environment Variables
The following environment variables must be set:

ADMIN_MAIL: Your ExtremeCloud IQ account email

XIQ_PASS: Your ExtremeCloud IQ password

XIQ_API_SECRET: Your API token (will be auto-generated if not present)

Add to your .bashrc:

    export ADMIN_MAIL="your-email@example.com"
    export XIQ_PASS="your-password"
    export XIQ_API_SECRET="your-api-token"  # Optional

Usage
Basic usage:
    python xiq_pull_devices_list.py


With debug output:
    python xiq_pull_devices_list.py --debug
    
With custom views:
    python xiq_pull_devices_list.py --views FULL
    
Command Line Arguments
--views: Views parameter for the API request (default: "FULL")

--debug: Enable debug output

Output Files
The script generates several files:

raw_devices_page_*.json: Raw JSON responses for each page (temporary)

devices.json: Combined JSON data for all devices

output_extreme_api.csv: Final CSV output with formatted device data

CSV Output Fields
Device ID

Creation Time

Update Time

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

Logging
The script logs its operations to xiq_api.log, including:

API request status

Number of devices found

File operations

Errors and warnings

Error Handling
The script includes comprehensive error handling for:

API authentication failures

Network connectivity issues

Token expiration and renewal

File operations

Data processing errors

Cleanup
After successful execution, the script automatically:

Removes temporary raw JSON files

Maintains only the final JSON and CSV outputs

Notes
The script uses a 3-second delay between API requests to prevent rate limiting

Token renewal is automatic if the current token expires

Progress bars show real-time status of data retrieval and processing


## Here's how you can securely store the username and password on Debian and allow any user to run the script:

### Use Environment Variables:

Store the username and password in a file that is only readable by the root user.
Export these variables in the .bashrc or .profile file of the root user.

    echo "export API_USER='your_username'" >> /root/.bashrc
    echo "export API_PASS='your_password'" >> /root/.bashrc

### Create a Wrapper Script:

Create a wrapper script that loads the environment variables and then runs the Python script.

    #!/bin/bash
    source /root/.bashrc
    python3 /path/to/xiq_pull_api_token.py

Make this script executable:

    chmod +x /path/to/wrapper_script.sh

Set the Correct Permissions:

Ensure the wrapper script can be executed by all users, but the file with the environment variables can only be read by the root user.

    chmod 755 /path/to/wrapper_script.sh
    chmod 600 /root/.bashrc

Use sudo for the Script:

Configure sudo to allow the script to be run without a password prompt. Add a rule in the /etc/sudoers file:

    ALL ALL=(ALL) NOPASSWD: /path/to/wrapper_script.sh

This method ensures that the username and password are stored securely while allowing any user to execute the script.
