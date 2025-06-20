import logging
import argparse

import pandas as pd

from .base_convertor import BaseSourceConvertor
from .utils import yf_columns

# 202501 record columns
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


column_mapping = {
    "Date": "Trade Date",
    "Quantity": "Quantity",
    "Price": "Purchase Price",
    "Fees & Comm": "Commission",
}


def find_position_header_index(
    file_path, header_keywords=["Symbol", "Description", "Qty (Quantity)"]
):
    """
    Finds the row index where the header starts.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if all(keyword in line for keyword in header_keywords):
                return i  # Return the correct header index
    return None  # Return None if not found


class SchwabConvertor(BaseSourceConvertor):
    loader_name = "schwab"

    @staticmethod
    def add_argument(parser: argparse.ArgumentParser):
        """Add Schwab specific arguments to CLI parser."""
        BaseSourceConvertor.add_argument(parser)

    def __init__(
        self,
        positions_data_path: str,
        history_data_path: str,
        fix_exceed_range: bool,
        default_dummy_date: str | None = None,
        **kwargs,
    ):
        super().__init__(
            positions_data_path=positions_data_path,
            history_data_path=history_data_path,
            fix_exceed_range=fix_exceed_range,
            default_dummy_date=default_dummy_date,
            **kwargs,
        )

        self.pre_check()

    def pre_check(self):
        if not all(col in self.history_data_df.columns for col in schwab_columns):
            raise ValueError(
                f"Columns in {self.history_data_path} do not match Schwab columns. Please update the schema."
            )

    def clean_column(self, df, column_name):
        """Helper function to clean columns that contain dollar signs or non-numeric values."""
        df[column_name] = df[column_name].replace(r"[$,]", "", regex=True).astype(float)

    def pre_process_history_data(self):
        df = self.history_data_df
        df = df.dropna(subset=["Quantity", "Price"])
        if "Comment" not in df.columns:
            df["Comment"] = ""
        self.clean_column(df, "Price")
        self.clean_column(df, "Fees & Comm")
        df["Quantity"] = df["Quantity"].astype(float)
        self.history_data_df = df

    def pre_process_positions_data(self):
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
        self, symbol, filtered_position_data_df, filtered_history_data_df
    ):
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
            raise NotImplementedError("Not implemented yet")

        return df

    def _parse_history_and_check(self, target_symbol):
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
        self.pre_process_history_data()
        self.pre_process_positions_data()

        symbol_to_process = self.positions_data_df["Symbol"].to_list()
        complete_dfs = [
            self._parse_history_and_check(symbol) for symbol in symbol_to_process
        ]
        total_complete_df = pd.concat(complete_dfs, ignore_index=True)
        total_complete_df = total_complete_df.rename(columns=column_mapping)

        total_complete_df.loc[total_complete_df["Action"] == "Sell", "Quantity"] = -abs(
            total_complete_df["Quantity"]
        )
        total_complete_df["Comment"] = total_complete_df["Action"].map(
            {"Sell": "correct to sell", "Reinvest Shares": "Reinvest Shares"}
        )

        total_complete_df = total_complete_df[yf_columns]
        total_complete_df["Trade Date"] = pd.to_datetime(
            total_complete_df["Trade Date"]
        ).dt.strftime("%Y%m%d")

        return total_complete_df
