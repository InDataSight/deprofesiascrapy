    #!/bin/bash

# filepath: /Users/peterbizik/profesia_scrapy/deprofesiascrapy/unique_date_published.sh

# Get the last entry from ExtractCopiedData.log
last_entry=$(tail -n 1 ExtractCopiedData.log)
json_file=$(echo "$last_entry" | cut -d',' -f1)
log_datetime=$(echo "$last_entry" | cut -d',' -f2)

# Check if the JSON file exists
if [ ! -f "$json_file" ]; then
    echo "JSON file $json_file not found. Exiting."
    exit 1
fi

# Extract unique date_published values from the JSON file
unique_date_published=$(jq '[.[] | .date_published] | unique' "$json_file")

# Print the unique date_published values
echo "Unique date_published values:"
echo "$unique_date_published"

# Convert log_datetime to a format that can be used for date calculations
log_datetime=$(date -d "$log_datetime" +"%Y-%m-%dT%H:%M:%S")

# Function to calculate the actual datetime based on the date_published value
calculate_datetime() {
    local date_published=$1
    case $date_published in
        "Pred "*)
            if [[ $date_published == *"hodinou"* ]]; then
                hours=$(echo $date_published | grep -oP '\d+')
                date -d "$log_datetime - $hours hours" +"%Y-%m-%dT%H:%M:%S"
            elif [[ $date_published == *"minútami"* ]]; then
                minutes=$(echo $date_published | grep -oP '\d+')
                date -d "$log_datetime - $minutes minutes" +"%Y-%m-%dT%H:%M:%S"
            elif [[ $date_published == *"dňami"* ]]; then
                days=$(echo $date_published | grep -oP '\d+')
                date -d "$log_datetime - $days days" +"%Y-%m-%dT%H:%M:%S"
            elif [[ $date_published == *"týždňami"* ]]; then
                weeks=$(echo $date_published | grep -oP '\d+')
                date -d "$log_datetime - $((weeks * 7)) days" +"%Y-%m-%dT%H:%M:%S"
            elif [[ $date_published == *"mesiacom"* ]]; then
                date -d "$log_datetime - 1 month" +"%Y-%m-%dT%H:%M:%S"
            fi
            ;;
        "Pred týždňom")
            date -d "$log_datetime - 1 week" +"%Y-%m-%dT%H:%M:%S"
            ;;
        "Pred mesiacom")
            date -d "$log_datetime - 1 month" +"%Y-%m-%dT%H:%M:%S"
            ;;
        "Predvčerom")
            date -d "$log_datetime - 2 days" +"%Y-%m-%dT%H:%M:%S"
            ;;
        "Včera")
            date -d "$log_datetime - 1 day" +"%Y-%m-%dT%H:%M:%S"
            ;;
        *)
            echo "Unknown date format: $date_published"
            ;;
    esac
}

# Process each unique date_published value
echo "Mapping date_published values to actual datetimes:"
for date_published in $(echo "$unique_date_published" | jq -r '.[]'); do
    if [ "$date_published" != "null" ]; then
        actual_datetime=$(calculate_datetime "$date_published")
        echo "$date_published -> $actual_datetime"
    fi
done