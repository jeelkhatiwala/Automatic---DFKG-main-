import os
import shutil
import hashlib
import time
import datetime
import sqlite3
import pandas as pd

def convertFileToStrings(in_path, db_out_base, csv_out_base, db_excel_report_path, csv_excel_report_path):
    """
    Converts SQLite database files found in the specified input directory and its subdirectories to strings.

    Args:
        in_path (str): Path to the input directory containing SQLite database files.
        db_out_base (str): Base path to the output directory where processed database files will be saved.
        csv_out_base (str): Base path to the output directory where converted CSV files will be saved.
        db_excel_report_path (str): Path to the output Excel file where database records will be saved.
        csv_excel_report_path (str): Path to the output Excel file where CSV file records will be saved.
    """
    start_time = time.time()

    # Create the output directories if they don't exist
    os.makedirs(db_out_base, exist_ok=True)
    os.makedirs(csv_out_base, exist_ok=True)

    # Find files with SQLite 3 signature
    all_files = find_sqlite_files(in_path)
    print("SQLite database files found: ", all_files)

    # Lists to store logs for the Excel reports
    db_rename_log = []
    csv_log = []

    # Process each file
    for f in all_files:
        print("Processing ", f)

        # Generate unique file name using SHA1 hash
        hashed_name = sha1_hash(f)
        db_output_file = os.path.join(db_out_base, hashed_name)

        try:
            # Process SQLite file to copy it to db_out_base
            process_sqlite_file(f, db_output_file)

            # Process SQLite file to CSV files, one per table
            csv_files = process_sqlite_to_csv(f, csv_out_base, hashed_name)

            # Log the database renaming
            original_filename = os.path.basename(f)
            db_rename_log.append((original_filename, f, hashed_name))

            # Log the CSV files
            for table_name, csv_file in csv_files:
                csv_filename = os.path.basename(csv_file)
                csv_log.append((csv_filename, table_name, original_filename, f))

        except Exception as e:
            print("Processing error ", f, ":", e)

    # Write database rename log to an Excel file
    db_rename_log_df = pd.DataFrame(db_rename_log, columns=["Original Filename", "Original Path", "Renamed Filename"])
    db_rename_log_df.to_excel(db_excel_report_path, index=False)

    # Write CSV file log to an Excel file
    csv_log_df = pd.DataFrame(csv_log, columns=["CSV Filename", "Table Name", "Original Database Filename", "Original Database Path"])
    csv_log_df.to_excel(csv_excel_report_path, index=False)

    end_time = time.time()
    computing_time = end_time - start_time
    current_time = datetime.datetime.now()

    append_to_file(os.path.join(db_out_base, "report.txt"), "SQLite 3.x database" + ",  " + str(len(all_files)) + ",  " + str(
        current_time) + ",  " + str(computing_time) + "\n")


def sha1_hash(text):
    """
    Compute the SHA1 hash of a string.

    Args:
        text (str): Input string to be hashed.

    Returns:
        str: SHA1 hash of the input string.
    """
    sha1 = hashlib.sha1()
    sha1.update(text.encode('utf-8'))
    return sha1.hexdigest()


def append_to_file(file_path, text):
    """
    Append a string to a file.

    Args:
        file_path (str): Path to the file to append the text to.
        text (str): Text to be appended to the file.
    """
    with open(file_path, 'a') as f:
        f.write(text)


def find_sqlite_files(in_path):
    """
    Find SQLite database files in the specified directory and its subdirectories.

    Args:
        in_path (str): Path to the input directory to search.

    Returns:
        list: List of paths to SQLite database files found.
    """
    sqlite_files = []
    for root, dirs, files in os.walk(in_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_sqlite_file(file_path):
                sqlite_files.append(file_path)
    return sqlite_files


def is_sqlite_file(file_path):
    """
    Check if the file content has a SQLite 3 signature.

    Args:
        file_path (str): Path to the file to check.

    Returns:
        bool: True if the file has a SQLite 3 signature, False otherwise.
    """
    with open(file_path, 'rb') as file:
        signature = file.read(16)
        return signature == b'SQLite format 3\x00'


def process_sqlite_file(input_file, output_file):
    """
    Process SQLite database files.

    This function currently copies the input file to the output location.

    Args:
        input_file (str): Path to the input SQLite database file.
        output_file (str): Path to the output location to save the processed file.
    """
    print("Processing SQLite file:", input_file)
    shutil.copy(input_file, output_file)


def process_sqlite_to_csv(input_file, csv_out_base, hashed_name):
    """
    Convert SQLite database files to CSV files, with each table in a separate CSV file.

    Args:
        input_file (str): Path to the input SQLite database file.
        csv_out_base (str): Base path to the output directory where converted CSV files will be saved.
        hashed_name (str): Hashed name to be used for the output CSV files.

    Returns:
        list: List of tuples containing table names and paths to the generated CSV files.
    """
    print("Converting SQLite file to CSV:", input_file)
    csv_files = []

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(input_file)
        cursor = conn.cursor()

        # Fetch all table names in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Export each table to a separate CSV file
        for table_name in tables:
            table_name = table_name[0]
            table_data = pd.read_sql_query(f"SELECT * from {table_name}", conn)
            csv_output_file = os.path.join(csv_out_base, f"{hashed_name}_{table_name}.csv")
            
            if table_data.empty:
                print(f"Warning: Table {table_name} in {input_file} is empty.")
            else:
                table_data.to_csv(csv_output_file, index=False)
                print(f"Exported {table_name} to {csv_output_file}")
                csv_files.append((table_name, csv_output_file))

        conn.close()

    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        if conn:
            conn.close()

    return csv_files


if __name__ == '__main__':
    # Specify input and output paths
    in_path = "/home/strikerpopa/Desktop/RA /Automatic DFKG/step1/data"
    db_out_base = "/home/strikerpopa/Desktop/RA /Automatic DFKG/step1/Database_files"
    csv_out_base = "/home/strikerpopa/Desktop/RA /Automatic DFKG/step2/CSV_files"
    db_excel_report_path = "/home/strikerpopa/Desktop/RA /Automatic DFKG/step1/db_report.xlsx"
    csv_excel_report_path = "/home/strikerpopa/Desktop/RA /Automatic DFKG/step2/csv_report.xlsx"
    convertFileToStrings(in_path, db_out_base, csv_out_base, db_excel_report_path, csv_excel_report_path)

