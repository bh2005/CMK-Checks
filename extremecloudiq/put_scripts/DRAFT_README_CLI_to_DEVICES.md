# ExtremeCloud IQ CLI Command Execution Script

This Python script executes CLI commands on ExtremeCloud IQ devices via the API, using JSON as the input format.

## Prerequisites

* Python 3.x
* The Python libraries `requests` and `argparse`. Install them with:

    ```bash
    pip install requests
    ```

* Environment variables `ADMIN_MAIL` and `XIQ_PASS` for API authentication.
* A JSON file containing device IDs and CLI commands (default: `commands.json`).

## Usage

1.  Save the Python script as `xiq_cli_execute.py`.
2.  Create a JSON file with device IDs and CLI commands in the following format:

    ```json
    {
      "devices": [
        {
          "id": "123",
          "commands": [
            "configure vlan 10",
            "show interface status"
          ]
        },
        {
          "id": "456",
          "commands": [
            "reboot device",
            "show version"
          ]
        }
      ]
    }
    ```

3.  Run the script:

    ```bash
    python xiq_cli_execute.py
    ```

## Options

* `-j` or `--json`: Specifies the path to the JSON file. Defaults to `commands.json`.
* `-l` or `--log`: Specifies the path to the log file. Defaults to `xiq_api.log`.
* `-h` or `--help`: Displays a help message with the available options.

## Examples

* Run with default options:

    ```bash
    python xiq_cli_execute.py
    ```

* Specify a custom JSON file:

    ```bash
    python xiq_cli_execute.py -j my_commands.json
    ```

* Specify a custom log file:

    ```bash
    python xiq_cli_execute.py -l my_log.log
    ```

* Display the help message:

    ```bash
    python xiq_cli_execute.py -h
    ```

## License

This script is licensed under the GNU General Public License v2.

## Author

bh2005

## URL

https://github.com/bh2005

## Date

2024-03-27

## Release Notes

* Init release

## Logging

The script logs all API calls and errors to a log file (default: `xiq_api.log`).

## Error Handling

The script attempts to detect and renew expired API tokens.

## Important Notes

* Ensure that the device IDs and CLI commands in the JSON file are correct.
* Thoroughly test the script in a test environment before using it in production.
* Consult the ExtremeCloud IQ API documentation for more information about the available API endpoints and commands.
