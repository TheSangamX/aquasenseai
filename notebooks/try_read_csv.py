import pandas as pd
import os

file_path = "../clean_reservoir_data.xls"

print("=== Trying to read as CSV ===")
try:
    # Try reading as CSV with different delimiters
    for delimiter in [',', ';', '\t', '|']:
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, engine='python')
            print(f"Success with delimiter: {repr(delimiter)}")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print("\nFirst 5 rows:")
            print(df.head())
            print("\nData types:")
            print(df.dtypes)
            break
        except Exception as e:
            print(f"Failed with delimiter {repr(delimiter)}: {e}")
except Exception as e:
    print(f"Failed to read as CSV: {e}")

print("\n=== Checking first 100 bytes of file ===")
with open(file_path, 'rb') as f:
    print(f.read(100))
