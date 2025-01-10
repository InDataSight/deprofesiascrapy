# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
import re
from datetime import datetime
from dataiku import pandasutils as pdu

# Read recipe inputs
offer_ids_20241231101657 = dataiku.Dataset("offer_ids_20241231101657")
offer_ids_20241231101657_df = offer_ids_20241231101657.get_dataframe()

# Compute recipe outputs from inputs
# TODO: Replace this part by your actual code that computes the output, as a Pandas dataframe
# NB: DSS also supports other kinds of APIs for reading and writing data. Please see doc.

offer_ids_extracted_df = offer_ids_20241231101657_df.dropna() # For this sample code, simply copy input to output

dataset_name = "offer_ids_20241231101657"
match = re.search(r'(\d{14})', dataset_name)
if match:
    date_str = match.group(1)
    parsed_date = datetime.strptime(date_str, "%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    offer_ids_extracted_df["date_downloaded"] = parsed_date

# Write recipe outputs
offer_ids_extracted = dataiku.Dataset("offer_ids_extracted")
offer_ids_extracted.write_with_schema(offer_ids_extracted_df)
