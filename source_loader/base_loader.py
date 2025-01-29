import argparse
from pathlib import Path

import pandas as pd


class BaseSourceLoader:
    loader_name = "base_loader"

    def __init__(self, history_data: str, output: str, **kwargs):
        if not Path(history_data).exists():
            raise FileNotFoundError(f"File {history_data} not found")

        self.history_data = history_data
        self.history_data_df: pd.DataFrame = pd.read_csv(history_data)
        self.output = output

    def convert(self):
        raise NotImplementedError()

    @staticmethod
    def add_argument(parser: argparse.ArgumentParser):
        pass


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
yf_columns = [
    "Symbol",
    "Trade Date",
    "Quantity",
    "Purchase Price",
    "Commission",
    "Comment",
]

column_mapping = {
    "Date": "Trade Date",
    "Quantity": "Quantity",
    "Price": "Purchase Price",
    "Fees & Comm": "Commission",
}
