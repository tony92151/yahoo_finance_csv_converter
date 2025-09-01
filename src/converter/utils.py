"""
Utility functions and constants for the converter module.
"""

import pandas as pd

# Column names required by Yahoo Finance format
yf_columns = [
    "Symbol",
    "Trade Date",
    "Quantity",
    "Purchase Price",
    "Commission",
    "Comment",
]


def check_final_df(df: pd.DataFrame) -> bool:
    """
    Check if the DataFrame conforms to the Yahoo Finance format requirements.

    Args:
        df: The DataFrame to check

    Returns:
        bool: True if the DataFrame is valid, False otherwise
    """
    # Check if all required columns are present
    if not all(col in df.columns for col in yf_columns):
        return False

    # Check if there are no null values in essential columns
    essential_cols = ["Symbol", "Trade Date", "Quantity", "Purchase Price"]
    if df[essential_cols].isnull().any().any():
        return False

    # All checks passed
    return True
