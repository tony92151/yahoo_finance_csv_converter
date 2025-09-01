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
        raise NotImplementedError("Subclasses must implement this method")
