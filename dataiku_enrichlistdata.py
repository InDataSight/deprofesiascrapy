# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
import re
from datetime import datetime, timedelta
from dataiku import pandasutils as pdu

# Extract date from dataset name and convert it to a standard format
DATASET_NAME = "offer_ids_20241231101657"

def calculate_datetime(date_published, log_datetime_str):
    """
    Python equivalent of the Bash function to calculate the actual datetime
    based on the 'date_published' value.
    """
    log_datetime = datetime.strptime(log_datetime_str, "%Y-%m-%dT%H:%M:%S")
    num_pattern = re.compile(r"\d+")

    if date_published.startswith("Pred "):
        # e.g. "Pred 2 hodinou", "Pred 10 hodinami", "Pred 7 dňami", etc.
        if "hodinou" in date_published or "hodinami" in date_published:
            match = num_pattern.search(date_published)
            hours = int(match.group()) if match else 1
            return (log_datetime - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")
        elif "minútami" in date_published:
            match = num_pattern.search(date_published)
            minutes = int(match.group()) if match else 1
            return (log_datetime - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")
        elif "dňami" in date_published:
            match = num_pattern.search(date_published)
            days = int(match.group()) if match else 1
            return (log_datetime - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        elif "týždňami" in date_published:
            match = num_pattern.search(date_published)
            weeks = int(match.group()) if match else 1
            return (log_datetime - timedelta(days=weeks * 7)).strftime("%Y-%m-%dT%H:%M:%S")
        elif "mesiacom" in date_published:
            # Approximate 1 month as 30 days
            return (log_datetime - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
        elif "týždňom" in date_published:
            # Approximate 1 month as 30 days
            return (log_datetime - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")

    elif date_published == "Pred týždňom":
        return (log_datetime - timedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%S")

    elif date_published == "Pred mesiacom":
        # Approximate 1 month as 30 days
        return (log_datetime - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")

    elif date_published == "Predvčerom":
        # 2 days ago
        return (log_datetime - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")

    elif date_published == "Včera":
        # 1 day ago
        return (log_datetime - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

    else:
        print(f"Unknown date format: {date_published}")
        return None

# Read recipe inputs
offer_ids_20241231101657 = dataiku.Dataset("offer_ids_20241231101657")
offer_ids_20241231101657_df = offer_ids_20241231101657.get_dataframe()

# Replace null values in the "money_text" column with 0
offer_ids_20241231101657_df["money_text"] = offer_ids_20241231101657_df["money_text"].fillna(0)

# For this sample code, simply copy input to output, but drop other NaNs
offer_ids_extracted_df = offer_ids_20241231101657_df.dropna()

match = re.search(r'(\d{14})', DATASET_NAME)
if match:
    date_str = match.group(1)
    parsed_date = datetime.strptime(date_str, "%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    offer_ids_extracted_df["date_downloaded"] = parsed_date

# Apply the calculate_datetime function to each row
offer_ids_extracted_df["converted_datetime"] = offer_ids_extracted_df.apply(
    lambda row: calculate_datetime(row["date_published"], parsed_date), axis=1
)

# Write recipe outputs
offer_ids_extracted = dataiku.Dataset("offer_ids_extracted")
offer_ids_extracted.write_with_schema(offer_ids_extracted_df)
