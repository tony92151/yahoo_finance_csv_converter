"""
Base converter class that all specific broker converters should inherit from.
"""

import argparse
from typing import Optional

import pandas as pd

from .config import DEFAULT_DUMMY_DATE


class BaseConverter:
    """
    Base class for all data converters.

    This class provides the foundation for converting broker-specific CSV data
    into Yahoo Finance compatible format.
    """

    converter_name = "base"

    def __init__(
        self,
        positions_data_path: str,
        history_data_path: str,
        fix_exceed_range: bool,
        default_dummy_date: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the base converter.

        Args:
            positions_data_path: Path to the positions CSV file
            history_data_path: Path to the transaction history CSV file
            fix_exceed_range: Whether to attempt fixing quantity mismatches
            default_dummy_date: Date to use for dummy transactions if needed
            **kwargs: Additional keyword arguments for specific converters
        """
        self.positions_data_path = positions_data_path
        self.history_data_path = history_data_path
        self.fix_exceed_range = fix_exceed_range
        self.default_dummy_date = default_dummy_date or DEFAULT_DUMMY_DATE

        self.positions_data_df: pd.DataFrame = pd.read_csv(positions_data_path)
        self.history_data_df: pd.DataFrame = pd.read_csv(history_data_path)

    def convert(self) -> pd.DataFrame:
        """
        Convert broker-specific data to Yahoo Finance format.

        Returns:
            DataFrame in Yahoo Finance format

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add converter-specific arguments to the parser.

        Args:
            parser: The argument parser to add arguments to
        """
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
