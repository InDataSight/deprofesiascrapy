#!/bin/bash

# Variables
STORAGE_ACCOUNT_NAME="your_storage_account_name"
CONTAINER_NAME="profesiafulldata"
DETAILED_CRAWLER_LIST="detailedcrawlerlist.csv"
PYTHON_SCRIPT="DataExtractFullCopyPipeline.py"

# Log the VM's UTC time
echo "VM UTC Time Check" > azure_time_issue.log
date -u +"VM Current UTC: %Y-%m-%dT%H:%M:%SZ" >> azure_time_issue.log
echo "" >> azure_time_issue.log

# Read offer IDs with status 'N' from detailedcrawlerlist
offer_ids=$(awk -F, '$2 == "N" {print $1}' $DETAILED_CRAWLER_LIST)

# Function to process each offer ID
process_offer_id() {
    offer_id=$1
    url="https://www.profesia.sk/O${offer_id}"
    output_file="offer_${offer_id}.txt"

    # Run the Python script to extract text content
    python3 $PYTHON_SCRIPT $url $output_file

    # Check if the output file was created
    if [ -f "$output_file" ]; then
        # Upload the file to Blob Storage
        az storage blob upload \
          --account-name $STORAGE_ACCOUNT_NAME \
          --container-name $CONTAINER_NAME \
          --name $output_file \
          --file $output_file \
          --auth-mode login

        if [ $? -eq 0 ]; then
            # Update detailedcrawlerlist with status 'Y' and current datetime
            sed -i "s/^${offer_id},N/${offer_id},Y,$(date -u +%Y-%m-%dT%H:%M:%SZ)/" $DETAILED_CRAWLER_LIST
            echo "File Uploaded to Blob Storage: $output_file" >> azure_time_issue.log
            date -u +"Upload Time UTC: %Y-%m-%dT%H:%M:%SZ" >> azure_time_issue.log
            echo "" >> azure_time_issue.log
        else
            echo "Failed to upload file to Blob Storage: $output_file" >> azure_time_issue.log
        fi
    else
        echo "Failed to create output file: $output_file" >> azure_time_issue.log
    fi
}

# Export the function to be used by parallel
export -f process_offer_id
export STORAGE_ACCOUNT_NAME
export CONTAINER_NAME
export PYTHON_SCRIPT
export DETAILED_CRAWLER_LIST

# Process each offer ID in parallel (2 at a time)
echo "$offer_ids" | xargs -n 1 -P 2 -I {} bash -c 'process_offer_id "$@"' _ {}

# Display the log
cat azure_time_issue.log