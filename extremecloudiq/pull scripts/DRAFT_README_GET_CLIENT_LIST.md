# ExtremeCloud IQ Client List Retrieval Script

This Python script retrieves the client list from ExtremeCloud IQ via the API and outputs it to JSON and CSV files. It supports pagination to retrieve all available data.

## Prerequisites

* Python 3.x
* The Python libraries `requests`, `argparse`, `csv`, `tqdm`. Install them with:

    ```bash
    pip install requests argparse tqdm
    ```

* Environment variables `ADMIN_MAIL` and `XIQ_PASS` for API authentication.
* ExtremeCloud IQ API access (see [ExtremeCloud™ IQ API Reference](https://api.extremecloudiq.com/)).

## Usage

1.  Save the Python script as `get_client_list.py`.
2.  Run the script:

    ```bash
    python get_client_list.py <views> [options]
    ```

## Options

* `<views>`: The `views` parameter for the API request (e.g., `summary`, `detail`). Required.
* `-l` or `--log`: Path to the log file. Defaults to `client_list.log`.
* `--page`: Page number for pagination or `all` to retrieve all pages. Defaults to `1`.
* `--page_size`: Number of items per page. Defaults to `100`.
* `--sort`: Field to sort by.
* `--dir`: Sort direction (`asc` or `desc`).
* `--where`: Filter criteria (e.g., `'name=test'`).

## Examples

* Retrieve the client list with the `summary` view:

    ```bash
    python get_client_list.py summary
    ```

* Retrieve all pages of the client list with the `detail` view and save to a custom log file:

    ```bash
    python get_client_list.py detail --page all -l my_client_list.log
    ```

* Retrieve the client list with the `detail` view, page size 50, sorted by name in ascending order, and filtered by the name 'test':

    ```bash
    python get_client_list.py detail --page_size 50 --sort name --dir asc --where 'name=test'
    ```

## Output

The script outputs the client list to two files:

* `all_clients.json`: Client list in JSON format.
* `all_clients.csv`: Client list in CSV format.

## License

This script is licensed under the GNU General Public License v2.

## Author

bh2005

## URL

https://github.com/bh2005

## Date

2024-03-01

## Release Notes

* Init release

## Logging

The script logs all API calls and errors to a log file (default: `client_list.log`).

## Error Handling

The script attempts to detect and renew expired API tokens.

## Important Notes

* Ensure that the environment variables `ADMIN_MAIL` and `XIQ_PASS` are set correctly.
* Thoroughly test the script in a test environment before using it in production.
* Consult the [ExtremeCloud IQ API documentation](https://api.extremecloudiq.com/) for more information about the available API endpoints and parameters.
