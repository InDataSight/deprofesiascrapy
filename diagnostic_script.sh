#!/bin/bash

# Variables
STORAGE_ACCOUNT_NAME=$1
CONTAINER_NAME=$2
BLOB_FILE_NAME="offer_ids_$(date -u +%Y%m%d%H%M%S).json"
JSON_FILE=$3

# Log the VM's UTC time
echo "VM UTC Time Check" > azure_time_issue.log
date -u +"VM Current UTC: %Y-%m-%dT%H:%M:%SZ" >> azure_time_issue.log
echo "" >> azure_time_issue.log

# Create a dummy JSON file if not provided
if [ -z "$JSON_FILE" ]; then
  echo '{"test": "data"}' > $BLOB_FILE_NAME
  echo "File Created: $BLOB_FILE_NAME" >> azure_time_issue.log
  date -u +"File Creation Time UTC: %Y-%m-%dT%H:%M:%SZ" >> azure_time_issue.log
  echo "" >> azure_time_issue.log
else
  cp "$JSON_FILE" "$BLOB_FILE_NAME"
  echo "File Copied: $BLOB_FILE_NAME from $JSON_FILE" >> azure_time_issue.log
  date -u +"File Copy Time UTC: %Y-%m-%dT%H:%M:%SZ" >> azure_time_issue.log
  echo "" >> azure_time_issue.log
fi

# Upload the file to Blob Storage
az storage blob upload \
  --account-name $STORAGE_ACCOUNT_NAME \
  --container-name $CONTAINER_NAME \
  --name $BLOB_FILE_NAME \
  --file $BLOB_FILE_NAME \
  --only-show-errors

# Log upload completion time
echo "File Uploaded to Blob Storage" >> azure_time_issue.log
date -u +"Upload Time UTC: %Y-%m-%dT%H:%M:%SZ" >> azure_time_issue.log
echo "" >> azure_time_issue.log

# Retrieve Blob metadata
echo "Retrieving Blob Metadata" >> azure_time_issue.log
az storage blob show \
  --account-name $STORAGE_ACCOUNT_NAME \
  --container-name $CONTAINER_NAME \
  --name $BLOB_FILE_NAME \
  --query "{name: name, lastModified: properties.lastModified, created: properties.creationTime}" \
  --only-show-errors >> azure_time_issue.log

# Extract unique employers from the JSON file
if [ -n "$JSON_FILE" ]; then
  unique_employers=$(jq '[.[] | .employer] | unique' "$JSON_FILE")
  echo "Unique Employers:" >> azure_time_issue.log
  echo "$unique_employers" >> azure_time_issue.log
fi

# Display the log
cat azure_time_issue.log