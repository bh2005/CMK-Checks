# ExtremeCloud IQ CLI Command Execution Script

This Python script executes CLI commands on ExtremeCloud IQ devices via the API.

## Prerequisites

* Python 3.x
* The Python libraries `requests` and `argparse`. Install them with:

    ```bash
    pip install requests
    ```

* Environment variables `ADMIN_MAIL` and `XIQ_PASS` for API authentication.
* A CSV file containing device IDs and CLI commands (default: `commands.csv`).

## Usage

1.  Save the Python script as `xiq_cli_execute.py`.
2.  Create a CSV file with device IDs and CLI commands in the following format:

    ```csv
    123,configure vlan 10
    456,show interface status
    789,reboot device
    ```

3.  Run the script:

    ```bash
    python xiq_cli_execute.py
    ```

## Options

* `-c` or `--csv`: Specifies the path to the CSV file. Defaults to `commands.csv`.
* `-l` or `--log`: Specifies the path to the log file. Defaults to `xiq_api.log`.
* `-h` or `--help`: Displays a help message with the available options.

## Examples

* Run with default options:

    ```bash
    python xiq_cli_execute.py
    ```

* Specify a custom CSV file:

    ```bash
    python xiq_cli_execute.py -c my_commands.csv
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

2025-03-26

## Release Notes

* Init release

## Logging

The script logs all API calls and errors to a log file (default: `xiq_api.log`).

## Error Handling

The script attempts to detect and renew expired API tokens.

## Important Notes

* Ensure that the device IDs and CLI commands in the CSV file are correct.
* Thoroughly test the script in a test environment before using it in production.
* Consult the ExtremeCloud IQ API documentation for more information about the available API endpoints and commands.
