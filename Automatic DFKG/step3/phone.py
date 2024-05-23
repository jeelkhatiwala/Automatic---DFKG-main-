import os
import csv
import re
import pandas as pd
from collections import defaultdict

# Increase the maximum field size limit
csv.field_size_limit(1000000000)  # Set a larger limit as needed

# Define regex patterns for extracting names and phone numbers
name_pattern = re.compile(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b')
phone_pattern = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

# Function to remove phone numbers from messages
def remove_phone_numbers(text):
    return re.sub(phone_pattern, '', text)

# Function to extract information from a CSV file
def extract_info_from_csv(csv_file):
    info_dict = defaultdict(lambda: {'Name': [], 'Messages': [], 'Count': 0, 'RowColumn': defaultdict(list)})
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row_idx, row in enumerate(csv_reader):
            for col_idx, entry in enumerate(row):
                name_matches = re.findall(name_pattern, entry)
                phone_matches = re.findall(phone_pattern, entry)
                cleaned_entry = remove_phone_numbers(entry)
                for phone in phone_matches:
                    info_dict[phone]['Name'].extend(name_matches)
                    if cleaned_entry.strip():  # Add message only if not empty
                        info_dict[phone]['Messages'].append(cleaned_entry.strip())
                    info_dict[phone]['Count'] += 1
                    file_name = os.path.basename(csv_file)
                    info_dict[phone]['RowColumn'][file_name].append(f"Column number: {col_idx}\nRow number: {row_idx}")
    return info_dict

# Folder containing CSV files
input_folder = '/home/strikerpopa/Desktop/RA /Automatic DFKG/step2/CSV_files'

# Dictionary to store phone-number associated information
phone_info_mapping = defaultdict(lambda: {'Name': [], 'Messages': [], 'Count': 0, 'RowColumn': defaultdict(list)})

# Iterate through CSV files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        csv_file = os.path.join(input_folder, filename)
        info_mapping_in_file = extract_info_from_csv(csv_file)
        # Update the phone-info mapping dictionary
        for phone, info in info_mapping_in_file.items():
            phone_info_mapping[phone]['Name'].extend(info['Name'])
            phone_info_mapping[phone]['Messages'].extend(info['Messages'])
            phone_info_mapping[phone]['Count'] += info['Count']
            for file, row_col_list in info['RowColumn'].items():
                phone_info_mapping[phone]['RowColumn'][file].extend(row_col_list)

# Create a list to hold structured data
structured_data = []

# Process the dictionary and structure the data
for phone, info in phone_info_mapping.items():
    row_column_info = {file: '\n'.join(entries) for file, entries in info['RowColumn'].items()}
    structured_data.append({
        'Phone': phone,
        'Name': ', '.join(set(info['Name'])),  # Remove duplicates and join
        'Messages': '\n\n'.join(set(info['Messages'])),  # Remove duplicates and join with double newline for readability
        'Row/Column Info': '\n\n'.join([f"{file}\n{info}" for file, info in row_column_info.items()])
    })

# Create DataFrame
df = pd.DataFrame(structured_data)

# Write DataFrame to Excel file
output_excel = '/home/strikerpopa/Desktop/RA /Automatic DFKG/step3/phone_info.xlsx'
df.to_excel(output_excel, index=False)

print("Excel file saved successfully!")

