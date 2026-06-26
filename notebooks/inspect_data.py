import pandas as pd

# Load the Excel file
file_path = "../clean_reservoir_data.xls"

print("=== Checking Excel file ===")
try:
    # Try with xlrd
    df = pd.read_excel(file_path, engine='xlrd')
    print("Successfully loaded with xlrd engine")
except Exception as e1:
    print(f"xlrd failed: {e1}")
    try:
        # Try with openpyxl
        df = pd.read_excel(file_path, engine='openpyxl')
        print("Successfully loaded with openpyxl engine")
    except Exception as e2:
        print(f"openpyxl also failed: {e2}")
        exit(1)

print(f"\nShape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\nFirst 5 rows:")
print(df.head())
print("\nData types:")
print(df.dtypes)
