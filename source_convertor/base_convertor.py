import argparse

import pandas as pd

from .config import DEFAULT_DUMMY_DATE


class BaseSourceConvertor:
    loader_name = "base"

    def __init__(
        self,
        positions_data_path: str,
        history_data_path: str,
        fix_exceed_range: bool,
        default_dummy_date: str | None,
        **kwargs,
    ):
        self.positions_data_path = positions_data_path
        self.history_data_path = history_data_path
        self.fix_exceed_range = fix_exceed_range
        self.default_dummy_date = default_dummy_date or DEFAULT_DUMMY_DATE

        self.positions_data_df: pd.DataFrame = pd.read_csv(positions_data_path)
        self.history_data_df: pd.DataFrame = pd.read_csv(history_data_path)

    def convert(self):
        raise NotImplementedError()

    @staticmethod
    def add_argument(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--positions-data",
            dest="positions_data_path",
            type=str,
            required=True,
            help="positions csv file",
        )
        parser.add_argument(
            "--history-data",
            dest="history_data_path",
            type=str,
            required=True,
            help="history csv file",
        )
        parser.add_argument(
            "--fix-exceed-range",
            action="store_true",
            help="try to fix quantity mismatch when history range is incomplete",
        )
        parser.add_argument(
            "--default-dummy-date",
            type=str,
            default=DEFAULT_DUMMY_DATE,
            help="date used when filling dummy transactions",
        )
