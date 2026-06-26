"""
Data Loader Module
Responsibility: Handles loading, cleaning, and preprocessing of reservoir data
"""

import pandas as pd


def load_reservoir_data(file_path: str) -> pd.DataFrame:
    """
    Load reservoir data from Excel/CSV file
    """
    try:
        # Try as CSV first (since our file is CSV with .xls extension)
        df = pd.read_csv(file_path, delimiter=',', engine='python')
        return df
    except Exception:
        try:
            # Try with xlrd
            df = pd.read_excel(file_path, engine='xlrd')
            return df
        except Exception as e:
            raise ValueError(f"Failed to load data from {file_path}: {e}")


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess raw reservoir data
    - Handle missing values
    - Convert data types
    - Derive new features
    """
    df = df.copy()
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate storage percentage
    df['Storage_Percentage'] = (df['Storage'] / df['Live_Capacity_FRL']) * 100
    
    return df


def filter_data(
    df: pd.DataFrame,
    reservoirs: list = None,
    basins: list = None,
    years: list = None,
    months: list = None
) -> pd.DataFrame:
    """
    Filter data based on multiple criteria
    """
    filtered = df.copy()
    
    if reservoirs and len(reservoirs) > 0:
        filtered = filtered[filtered['Reservoir_Name'].isin(reservoirs)]
    
    if basins and len(basins) > 0:
        filtered = filtered[filtered['Basin'].isin(basins)]
    
    if years and len(years) > 0:
        filtered = filtered[filtered['Year'].isin(years)]
    
    if months and len(months) > 0:
        filtered = filtered[filtered['Month'].isin(months)]
    
    return filtered
