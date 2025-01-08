#!/bin/bash

# API Configuration (use environment variables)
API_KEY="${XIQ_API_KEY}"
API_SECRET="${XIQ_API_SECRET}"
XIQ_BASE_URL=https://api.extremecloudiq.com

# Function to get access points with location (with pagination and better error handling)
get_access_points_with_location() {
    if [[ -z "$API_KEY" || -z "$API_SECRET" ]]; then
        echo "Error: API_KEY or API_SECRET environment variables not set." >&2 # Redirect error to stderr
        return 1
    fi

    local page=1
    local page_size=100
    local all_aps="[]" # Initialize as an empty JSON array

    while true; do
        local response=$(curl -s -X GET "$XIQ_BASE_URL/devices?page=$page&limit=$page_size" \
            -H "Authorization: Bearer $API_KEY")

        local http_code=$(echo "$response" | jq -r '.http_status')

        if [[ "$http_code" != "200" ]]; then
            echo "Error: API request failed with HTTP status $http_code." >&2
            echo "$response" | jq . >&2 # Print the error response for debugging
            return 1
        fi

        local aps=$(echo "$response" | jq -r '.data[] | select(.type == "AP") | {
            serial_number: .serial_number,
            name: .name,
            model: .model,
            location: if .location then .location.name else "No location set" end
        }')

        if [[ -z "$aps" ]]; then # Check if no more APs on this page
            break
        fi

        all_aps=$(echo "$all_aps" "$aps" | jq -s add) # Append to the array

        local returned_count=$(echo "$response" | jq -r 'length(.data)')
        if [[ "$returned_count" -lt "$page_size" ]]; then
          break # last page
        fi
        page=$((page + 1))
    done

    echo "$all_aps"
}

# Main script execution
access_points_with_location=$(get_access_points_with_location)

if [[ $? -eq 0 ]]; then # Check the return code of the function
    if [[ -n "$access_points_with_location" ]]; then
        echo "$access_points_with_location" | jq .
    else
        echo "No access points found."
    fi
else
    echo "Error retrieving access point information." >&2
    exit 1
fi
