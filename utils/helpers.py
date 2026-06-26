"""
Helpers Module
Responsibility: General utility functions used across the application
"""

import pandas as pd


def calculate_storage_percentage(storage: float, capacity: float) -> float:
    """
    Calculate storage as percentage of live capacity
    """
    pass


def format_number(num: float, decimal_places: int = 2) -> str:
    """
    Format numbers for display
    """
    pass


def get_month_name(month: int) -> str:
    """
    Get month name from month number
    """
    pass


def export_data(df: pd.DataFrame, file_format: str = "csv") -> bytes:
    """
    Export DataFrame to specified format (csv, excel)
    """
    pass
