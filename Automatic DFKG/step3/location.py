import os
import csv
import re
import pandas as pd
from collections import defaultdict

# Increase the maximum field size limit
csv.field_size_limit(1000000000)  # Set a larger limit as needed

# Define a refined regex pattern for extracting full addresses
address_pattern = re.compile(
    r'\b\d{1,6}\s+\w+(?:\s\w+)*(?:\s(?:Avenue|Ave|Street|St|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Parkway|Pkwy|Place|Pl))?(?:\s(?:Apt|Suite|Unit)\s?\d+)?(?:,\s*\w+){1,3},?\s+[A-Z]{2}\s+\d{5}\b'
)

# Function to extract addresses from a CSV file
def extract_addresses_from_csv(csv_file):
    addresses_info = defaultdict(lambda: {'SourceFiles': defaultdict(list)})
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        try:
            headers = next(csv_reader)
        except StopIteration:
            # The CSV file is empty
            return addresses_info
        for row_idx, row in enumerate(csv_reader):
            for col_idx, entry in enumerate(row):
                address_matches = re.findall(address_pattern, entry)
                for address in address_matches:
                    file_name = os.path.basename(csv_file)
                    addresses_info[address]['SourceFiles'][file_name].append(f"Column number: {col_idx}, Row number: {row_idx}")
    return addresses_info

# Folder containing CSV files
input_folder = '/home/strikerpopa/Desktop/RA /Automatic DFKG/step2/CSV_files'

# Dictionary to store addresses and their corresponding information
addresses_info = defaultdict(lambda: {'SourceFiles': defaultdict(list)})

# Iterate through CSV files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        csv_file = os.path.join(input_folder, filename)
        file_addresses_info = extract_addresses_from_csv(csv_file)
        for address, info in file_addresses_info.items():
            addresses_info[address]['SourceFiles'].update(info['SourceFiles'])

# Sum up the occurrences of each location across all source files
for address, info in addresses_info.items():
    info['TotalOccurrences'] = sum(len(files) for files in info['SourceFiles'].values())

# Create DataFrame
data = []
for address, info in addresses_info.items():
    source_files_info = []
    for source_file, positions in info['SourceFiles'].items():
        positions_str = '\n'.join(positions)
        source_files_info.append(f"{source_file}:\n{positions_str}")
    source_files_info_str = '\n\n'.join(source_files_info)
    data.append({
        'Location': address,
        'SourceFiles': source_files_info_str,
        'TotalOccurrences': info['TotalOccurrences']
    })

df_addresses = pd.DataFrame(data)

# Define the output Excel file path
output_excel_addresses = '/home/strikerpopa/Desktop/RA /Automatic DFKG/step3/address_info.xlsx'

# Write DataFrame to Excel file
df_addresses.to_excel(output_excel_addresses, index=False)

print("Excel file with addresses saved successfully!")

