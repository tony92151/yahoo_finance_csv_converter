"""
Schwab broker data converter implementation.
"""

import argparse
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .base import BaseConverter
from .utils import yf_columns

# 2025-01 record columns definition for Schwab CSV format
schwab_columns = [
    "Date",
    "Action",
    "Symbol",
    "Description",
    "Quantity",
    "Price",
    "Fees & Comm",
    "Amount",
]

# Mapping from Schwab columns to Yahoo Finance columns
column_mapping = {
    "Date": "Trade Date",
    "Quantity": "Quantity",
    "Price": "Purchase Price",
    "Fees & Comm": "Commission",
}


def find_position_header_index(
    file_path: str,
    header_keywords: List[str] = ["Symbol", "Description", "Qty (Quantity)"],
) -> Optional[int]:
    """
    Find the row index where the header starts in Schwab positions file.

    Args:
        file_path: Path to the positions CSV file
        header_keywords: Keywords to identify the header row

    Returns:
        The index of the header row, or None if not found
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if all(keyword in line for keyword in header_keywords):
                return i  # Return the correct header index
    return None  # Return None if not found


class SchwabConverter(BaseConverter):
    """
    Converter for Schwab broker CSV data to Yahoo Finance format.

    This converter handles Schwab's specific CSV format and transforms it
    into the format required by Yahoo Finance for portfolio import.
    """

    converter_name = "schwab"

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--positions-data",
            dest="positions_data_path",
            type=str,
            required=True,
            help="Path to positions CSV file",
        )
        parser.add_argument(
            "--history-data",
            dest="history_data_path",
            type=str,
            required=True,
            help="Path to history CSV file",
        )
        parser.add_argument(
            "--fix-exceed-range",
            action="store_true",
            help="Try to fix quantity mismatch when history range is incomplete",
        )
        parser.add_argument(
            "--default-dummy-date",
            type=str,
            default=DEFAULT_DUMMY_DATE,
            help="Date used when filling dummy transactions",
        )

    def __init__(
        self,
        positions_data_path: str,
        history_data_path: str,
        fix_exceed_range: bool,
        default_dummy_date: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Schwab converter.

        Args:
            positions_data_path: Path to the positions CSV file
            history_data_path: Path to the transaction history CSV file
            fix_exceed_range: Whether to attempt fixing quantity mismatches
            default_dummy_date: Date to use for dummy transactions if needed
            **kwargs: Additional keyword arguments
        """

        self.positions_data_path = positions_data_path
        self.history_data_path = history_data_path
        self.fix_exceed_range = fix_exceed_range
        self.default_dummy_date = default_dummy_date or DEFAULT_DUMMY_DATE

        self.positions_data_df: pd.DataFrame = pd.read_csv(positions_data_path)
        self.history_data_df: pd.DataFrame = pd.read_csv(history_data_path)

        super().__init__(**kwargs)

        self.pre_check()

    def pre_check(self) -> None:
        """
        Check if the input data has the expected format.

        Raises:
            ValueError: If the history data doesn't match expected Schwab format
        """
        if not all(col in self.history_data_df.columns for col in schwab_columns):
            raise ValueError(
                f"Columns in {self.history_data_path} do not match Schwab columns. Please update the schema."
            )

    def clean_column(self, df: pd.DataFrame, column_name: str) -> None:
        """
        Clean columns that contain dollar signs or non-numeric values.

        Args:
            df: DataFrame to modify
            column_name: Column name to clean
        """
        df[column_name] = df[column_name].replace(r"[$,]", "", regex=True).astype(float)

    def pre_process_history_data(self) -> None:
        """
        Preprocess the history data to prepare for conversion.
        """
        df = self.history_data_df
        df = df.dropna(subset=["Quantity", "Price"])
        if "Comment" not in df.columns:
            df["Comment"] = ""
        self.clean_column(df, "Price")
        self.clean_column(df, "Fees & Comm")
        df["Quantity"] = df["Quantity"].astype(float)
        self.history_data_df = df

    def pre_process_positions_data(self) -> None:
        """
        Preprocess the positions data to prepare for conversion.

        Raises:
            ValueError: If the header row can't be found in the positions file
        """
        header_index = find_position_header_index(self.positions_data_path)
        if header_index is None:
            raise ValueError(f"Could not find header row in {self.positions_data_path}")

        df = pd.read_csv(self.positions_data_path, skiprows=header_index)
        df = df.dropna(how="all")

        df = df[df["Symbol"].str.isupper()]
        self.clean_column(df, "Price")
        self.clean_column(df, "Cost Basis")
        self.positions_data_df = df

    def _complete_history_data(
        self,
        symbol: str,
        filtered_position_data_df: pd.DataFrame,
        filtered_history_data_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Complete history data for a given symbol by fixing quantity mismatches.

        Args:
            symbol: Stock symbol to process
            filtered_position_data_df: Position data for the symbol
            filtered_history_data_df: History data for the symbol

        Returns:
            Completed history data for the symbol

        Raises:
            NotImplementedError: If fix_exceed_range is False and data is incomplete
        """
        target_quantity = float(filtered_position_data_df["Qty (Quantity)"].values[0])
        target_total_value = float(filtered_position_data_df["Cost Basis"].values[0])

        df = filtered_history_data_df.copy()
        df.loc[df["Action"] == "Sell", "Quantity"] = -abs(df["Quantity"])

        if df["Quantity"].sum() == target_quantity:
            logging.info(f"Symbol: {symbol} has the correct quantity. Skip fix.")
            return df

        logging.info(f"Symbol: {symbol} has incorrect quantity. Fixing...")

        # if Quantity not match probably due to the missing data because exceed time range
        if self.fix_exceed_range:
            df["Value"] = df["Quantity"] * df["Price"]
            sum_value = df["Value"].sum()
            add_quantity = abs(target_quantity - df["Quantity"].sum())
            add_action = "Buy" if target_total_value > sum_value else "Sell"
            add_price = abs(target_total_value - sum_value) / add_quantity

            if add_action == "Sell" and (target_quantity > df["Quantity"].sum()):
                logging.info(
                    f"Break Symbol {symbol} because the quantity is less than the target quantity. Replace all with dummy data."
                )
                new_row = {
                    "Date": self.default_dummy_date,
                    "Action": "Buy",
                    "Symbol": symbol,
                    "Quantity": target_quantity,
                    "Price": target_total_value / target_quantity,
                }
                df = pd.DataFrame.from_dict(new_row, orient="index").T
            else:
                new_row = {
                    "Date": self.default_dummy_date,
                    "Action": add_action,
                    "Symbol": symbol,
                    "Quantity": add_quantity,
                    "Price": add_price,
                }
                new_row_df = pd.DataFrame.from_dict(new_row, orient="index").T
                df = pd.concat([df, new_row_df], ignore_index=True)

            if "Value" in df.columns:
                df = df.drop(columns=["Value"])
            df["Quantity"] = abs(df["Quantity"])
        else:
            raise NotImplementedError(
                "Quantity mismatch fixing is not implemented for fix_exceed_range=False"
            )

        return df

    def _parse_history_and_check(self, target_symbol: str) -> pd.DataFrame:
        """
        Parse history data for a given symbol and check against position data.

        Args:
            target_symbol: Stock symbol to process

        Returns:
            Processed history data for the symbol
        """
        history_data_df = self.history_data_df
        positions_data_df = self.positions_data_df
        filtered_history_data_df = history_data_df[
            history_data_df["Symbol"] == target_symbol
        ]
        filtered_positions_data_df = positions_data_df[
            positions_data_df["Symbol"] == target_symbol
        ]

        return self._complete_history_data(
            target_symbol, filtered_positions_data_df, filtered_history_data_df
        )

    def convert(self) -> pd.DataFrame:
        """
        Convert Schwab data to Yahoo Finance format.

        Returns:
            DataFrame in Yahoo Finance format
        """
        self.pre_process_history_data()
        self.pre_process_positions_data()

        symbol_to_process = self.positions_data_df["Symbol"].to_list()
        complete_dfs = [
            self._parse_history_and_check(symbol) for symbol in symbol_to_process
        ]
        total_complete_df = pd.concat(complete_dfs, ignore_index=True)
        total_complete_df = total_complete_df.rename(columns=column_mapping)

        # Mark sell transactions with negative quantity
        total_complete_df.loc[total_complete_df["Action"] == "Sell", "Quantity"] = -abs(
            total_complete_df["Quantity"]
        )

        # Add comments for certain transaction types
        total_complete_df["Comment"] = total_complete_df["Action"].map(
            {"Sell": "correct to sell", "Reinvest Shares": "Reinvest Shares"}
        )

        # Select only the required columns and format the date
        total_complete_df = total_complete_df[yf_columns]
        total_complete_df["Trade Date"] = pd.to_datetime(
            total_complete_df["Trade Date"]
        ).dt.strftime("%Y%m%d")

        return total_complete_df
