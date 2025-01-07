import csv
import json
import os
import re

# Define file paths
detailedcrawlerlist = "/home/peter.bizik/profesiascrapy/profesia_crawler/profesia_crawler/spiders/detailedcrawlerlist.csv"
output_json_file = "processed_offers.json"

# Function to process the text file for each offer ID
def process_offer_text(offer_id):
    input_file = f"offer_{offer_id}.txt"
    if not os.path.exists(input_file):
        return None

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Remove text starting with "Hľadanie práce" and ending with "Hľadanie práce"
    text = re.sub(r'Hľadanie práce.*?Hľadanie práce', '', text, flags=re.DOTALL)

    # Remove text after "Reagovať na ponuku" including "Reagovať na ponuku"
    text = re.split(r'Reagovať na ponuku', text)[0]

    # Extract data from the remaining text
    data = {}
    try:
        data['ID'] = re.search(r'ID:\s*(\d+)', text).group(1)
        data['Dátum zverejnenia'] = re.search(r'Dátum zverejnenia:\s*([\d\.]+)', text).group(1)
        data['lokalita'] = re.search(r'lokalita:\s*(.+)', text).group(1)
        data['Pozícia'] = re.search(r'Pozícia:\s*(.+)', text).group(1)
        data['Spoločnosť'] = re.search(r'Spoločnosť:\s*(.+)', text).group(1)
        data['Základná zložka mzdy \(brutto\):'] = re.search(r'Základná zložka mzdy \(brutto\):\s*(.+)', text).group(1)
        data['remaining_text'] = text.strip()
    except AttributeError:
        # If any field is not found, set it to None
        for key in ['ID', 'Dátum zverejnenia', 'lokalita', 'Pozícia', 'Spoločnosť', 'Základná zložka mzdy \(brutto\):']:
            if key not in data:
                data[key] = None
        data['remaining_text'] = text.strip()

    return data

# Read the detailedcrawlerlist.csv file and process each offer ID with status 'Y'
processed_offers = []
with open(detailedcrawlerlist, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        offer_id, status, _ = row
        if status == 'Y':
            offer_data = process_offer_text(offer_id)
            if offer_data:
                processed_offers.append(offer_data)

# Save the processed data to a JSON file
with open(output_json_file, 'w', encoding='utf-8') as jsonfile:
    json.dump(processed_offers, jsonfile, ensure_ascii=False, indent=4)

print(f"Processed data saved to {output_json_file}")