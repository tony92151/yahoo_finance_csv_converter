"""
Converter module for transforming broker CSV data to Yahoo Finance format.

This package contains converters for different brokers, all implementing
a common interface to transform CSV data into Yahoo Finance compatible format.
"""

from .base import BaseConverter
from .schwab import SchwabConverter

# Simple mapping of converter names to their classes
converter_mapping = {
    SchwabConverter.converter_name: SchwabConverter,
}

__all__ = ["BaseConverter", "SchwabConverter", "converter_mapping"]
