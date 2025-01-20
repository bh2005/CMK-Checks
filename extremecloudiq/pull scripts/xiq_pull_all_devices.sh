#!/bin/bash

# API Configuration (use environment variables)
API_SECRET="${XIQ_API_SECRET}"
XIQ_BASE_URL=https://api.extremecloudiq.com

# Function to get devices (with pagination and better error handling)
get_devices() {
  if [[ -z "$API_SECRET" ]]; then
    echo "Error: API_SECRET environment variable not set." >&2
    return 1
  fi

  local page=1
  local page_size=100
  local all_devices="[]" # Initialize as an empty JSON array
  local max_devices=1000
  local total_devices=0
  local total_pages=9  # Set to 9 pages
  local views=DETAIL  #BASIC, FULL, STATUS, LOCATION, CLIENT, DETAIL

  for page in $(seq 1 $total_pages); do
    # Get response from API for the current page
    local response=$(curl -s -X GET "$XIQ_BASE_URL/devices?page=$page&limit=$page_size&connected=true&adminStates=MANAGED&views=$views&fields=MANAGED_BY&deviceTypes=REAL&nullField=LOCATION_ID&async=false" \
      -H "Authorization: Bearer $API_SECRET")

    # Print response to stdout for debugging
    echo "DEBUG: Raw API response for page $page:"
    echo "$response"
    
    local http_code=$(echo "$response" | jq -r '.http_status')

    # Save the raw response for each page to a separate file
    echo "$response" > "raw_devices_page_${page}.json"

    if [[ "$http_code" != "200" ]]; then
      echo "Error: API request failed with HTTP status $http_code." >&2
      echo "$response" | jq . >&2 # Print the error response for debugging
      continue
    fi

    # Extract devices from the response
    local devices=$(echo "$response" | jq -r '.data[]')

    if [[ -z "$devices" ]]; then
      echo "No devices found on page $page, skipping."
      continue
    fi

    # Append devices to the all_devices array
    all_devices=$(echo "$all_devices $devices" | jq -s add)

    total_devices=$((total_devices + $(echo "$devices" | jq -r 'length')))

    # If we reach the max number of devices, stop fetching more
    if [[ "$total_devices" -ge "$max_devices" ]]; then
      break
    fi

    # Pause for 3 seconds before requesting the next page
    sleep 3
  done

  # Write all devices data to devices.json (after collecting from all pages)
  echo "$all_devices" > devices.json

  # Check the return code and print success/error message
  if [[ $? -eq 0 ]]; then
    echo "Devices data has been written to devices.json (formatted with jq)."
  else
    echo "Error writing device information to file." >&2
  fi
}

# Function to combine all raw JSON files into one output file
combine_json_files() {
  local output_file="output_extreme_api.json"
  jq -s 'flatten' raw_devices_page_*.json > "$output_file"

  if [[ $? -eq 0 ]]; then
    echo "All raw JSON files have been combined into $output_file."
  else
    echo "Error combining JSON files." >&2
  fi
}

# Main script execution
get_devices
combine_json_files

# Exit script regardless of the function's return code (already handled within the function)
exit 0
