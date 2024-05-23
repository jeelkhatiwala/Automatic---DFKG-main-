import os
import csv
import re
import pandas as pd
from collections import defaultdict

# Increase the maximum field size limit
csv.field_size_limit(1000000000)  # Set a larger limit as needed

# Define regex patterns for extracting names and emails
name_pattern = re.compile(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b')
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# List of common product names (you should extend this list as needed)
common_product_names = {'Product', 'Model', 'Item', 'Brand', 'Type', 'Category'}

# Function to determine if a name is likely to be a person's name
def is_person_name(name):
    return name.split()[0] not in common_product_names

# Function to extract names and emails from a CSV file
def extract_info_from_csv(csv_file):
    name_email_mapping = defaultdict(lambda: {'emails': set(), 'RowColumn': defaultdict(list)})
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row_idx, row in enumerate(csv_reader):
            for col_idx, entry in enumerate(row):
                name_matches = re.findall(name_pattern, entry)
                email_matches = re.findall(email_pattern, entry)
                for name in name_matches:
                    if is_person_name(name):
                        name_email_mapping[name]['emails'].update(email_matches)
                        file_name = os.path.basename(csv_file)
                        name_email_mapping[name]['RowColumn'][file_name].append(f"Column number: {col_idx}\nRow number: {row_idx}")
    return name_email_mapping

# Folder containing CSV files
input_folder = '/home/strikerpopa/Desktop/RA /Automatic DFKG/step2/CSV_files'

# Dictionary to store name-email associations
name_email_mapping = defaultdict(lambda: {'emails': set(), 'RowColumn': defaultdict(list)})

# Iterate through CSV files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        csv_file = os.path.join(input_folder, filename)
        file_name_email_mapping = extract_info_from_csv(csv_file)
        # Update the main name-email mapping dictionary
        for name, info in file_name_email_mapping.items():
            name_email_mapping[name]['emails'].update(info['emails'])
            for file, row_col_list in info['RowColumn'].items():
                name_email_mapping[name]['RowColumn'][file].extend(row_col_list)

# Prepare data for the DataFrame
data = []
for name, info in name_email_mapping.items():
    row_column_info = {file: '\n'.join(entries) for file, entries in info['RowColumn'].items()}
    data.append({
        'Name': name,
        'Email': ', '.join(info['emails']),
        'Row/Column Info': '\n\n'.join([f"{file}\n{info}" for file, info in row_column_info.items()]),
        'Occurrence': len(info['RowColumn'])  # Add a count of occurrences for sorting purposes
    })

# Create DataFrame and sort by Occurrence in descending order
df = pd.DataFrame(data)
df.sort_values(by='Occurrence', ascending=False, inplace=True)
df.drop(columns=['Occurrence'], inplace=True)  # Drop the Occurrence column after sorting

# Write DataFrame to Excel file
output_excel = '/home/strikerpopa/Desktop/RA /Automatic DFKG/step3/names_emails.xlsx'
df.to_excel(output_excel, index=False)

print("Excel file with names and emails saved successfully!")

