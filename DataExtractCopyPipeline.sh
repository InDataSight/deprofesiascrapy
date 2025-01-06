#!/bin/bash

# Step 1: Start the script
echo "Starting Scrapy crawler and Blob Storage sync process."

# Step 2: Activate the Python virtual environment
source ~/profesiascrapy/bin/activate

# Step 3: Navigate to the spiders directory
cd ~/profesiascrapy/profesia_crawler/profesia_crawler/spiders/

# Define variables
json_file="offer_ids_$(date +%Y%m%d%H%M%S).json"
detailedcrawlerlist="detailedcrawlerlist.csv"
logfile="ExtractCopiedData.log"
blob_storage_account="scrapyprofesia"
blob_container_name="profesialistsdata"
blob_storage_path="/home/peter.bizik/profesiascrapy/profesia_crawler/profesia_crawler/spiders/$json_file"

# Run the Scrapy spider and save the output to a JSON file
scrapy crawl profesia_spider -o "$json_file"

# Check if the JSON file was created
if [ ! -f "$json_file" ]; then
    echo "JSON file not created. Exiting."
    exit 1
fi

# Analyze the JSON file using jq
echo "Basic JSON analysis:"
total_entries=$(jq '. | length' "$json_file")

# Sum of the .title for each .employer and order by the sum value
employer_title_counts=$(jq -r '
  group_by(.employer) |
  map({
    employer: .[0].employer,
    title_count: map(select(.title != null) | .title) | length
  }) |
  sort_by(.title_count) |
  reverse' "$json_file")

# Extract unique employers and their title counts
unique_employers_with_counts=$(echo "$employer_title_counts" | jq -r '.[] | "\(.employer), \(.title_count)"')

echo "Total entries: $total_entries"
echo "Unique employers with sum of titles:"
echo "$unique_employers_with_counts"

# Extract offer IDs and update detailedcrawlerlist
echo "Updating detailedcrawlerlist..."
jq -r '.[] | select(.offer_id != null) | .offer_id' "$json_file" | while read -r offer_id; do
    if ! grep -q "^$offer_id," "$detailedcrawlerlist"; then
        echo "$offer_id,N,$(date +%Y-%m-%dT%H:%M:%S)" >> "$detailedcrawlerlist"
    fi
done

# Add entry to ExtractCopiedData.log
echo "Adding entry to ExtractCopiedData.log..."
if [ ! -f "$logfile" ]; then
    echo "filename created,datetime,filename copied" > "$logfile"
fi
echo "$json_file,$(date +%Y-%m-%dT%H:%M:%S)," >> "$logfile"

# Copy the JSON file to blob storage
echo "Copying JSON file to blob storage..."
az storage blob upload \
  --account-name "$blob_storage_account" \
  --container-name "$blob_container_name" \
  --name "$json_file" \
  --file "$blob_storage_path" \
  --auth-mode login

if [ $? -eq 0 ]; then
    # Update ExtractCopiedData.log with the copied filename
    sed -i "s|^$json_file,.*|&$json_file|" "$logfile"
else
    echo "Failed to copy JSON file to blob storage."
    exit 1
fi

# Compress the JSON file using zip
echo "Compressing JSON file..."
zip "$json_file.zip" "$json_file"
if [ $? -eq 0 ]; then
    echo "JSON file compressed successfully."
else
    echo "Failed to compress JSON file."
    exit 1
fi

echo "Pipeline completed successfully."