"""
Base converter class that all specific broker converters should inherit from.
"""

import argparse
from typing import Optional

import pandas as pd


class BaseConverter:
    """
    Base class for all data converters.

    This class provides the foundation for converting broker-specific CSV data
    into Yahoo Finance compatible format.
    """

    converter_name = "base"

    def __init__(
        self,
        **kwargs,
    ):
        """
        Initialize the base converter.

        Args:
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
