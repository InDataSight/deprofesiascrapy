#!/bin/bash

# Define variables
detailedcrawlerlist="/home/peter.bizik/profesiascrapy/profesia_crawler/profesia_crawler/spiders/detailedcrawlerlist.csv"
blob_storage_account="scrapyprofesia"
blob_container_name="profesiafulldata"
python_script="profesia_bs_fulltext.py"

# Step 2: Activate the Python virtual environment
source ~/profesiascrapy/bin/activate

# Read offer IDs with status 'N' from detailedcrawlerlist
offer_ids=$(awk -F, '$2 == "N" {print $1}' $detailedcrawlerlist)

# Function to process each offer ID
process_offer_id() {
    offer_id=$1
    url="https://www.profesia.sk/O${offer_id}"
    output_file="offer_${offer_id}.txt"

    # Run the Python script to extract text content
    python3 $python_script $url $output_file

    # Check if the output file was created
    if [ -f "$output_file" ]; then
        # Upload the file to Blob Storage
        az storage blob upload \
          --account-name $blob_storage_account \
          --container-name $blob_container_name \
          --name $output_file \
          --file $output_file \
          --auth-mode login

        if [ $? -eq 0 ]; then
            # Update detailedcrawlerlist with status 'Y' and current datetime
            sed -i "s/^${offer_id},N/${offer_id},Y,$(date -u +%Y-%m-%dT%H:%M:%SZ)/" $detailedcrawlerlist
            echo "File Uploaded to Blob Storage: $output_file"
        else
            echo "Failed to upload file to Blob Storage: $output_file"
        fi
    else
        echo "Failed to create output file: $output_file"
    fi
}

# Export the function to be used by parallel
export -f process_offer_id
export blob_storage_account
export blob_container_name
export python_script
export detailedcrawlerlist

# Process each offer ID in parallel (2 at a time)
echo "$offer_ids" | xargs -n 1 -P 2 -I {} bash -c 'process_offer_id "$@"' _ {}