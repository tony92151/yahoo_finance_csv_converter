"""
Converter module for transforming broker CSV data to Yahoo Finance format.

This package contains converters for different brokers, all implementing
a common interface to transform CSV data into Yahoo Finance compatible format.
"""

from .base import BaseConverter
from .cathay_sub_brokerage import CathaySubBrokerageConverter
from .schwab import SchwabConverter

# Simple mapping of converter names to their classes
converter_mapping = {
    SchwabConverter.converter_name: SchwabConverter,
    CathaySubBrokerageConverter.converter_name: CathaySubBrokerageConverter,
}

__all__ = ["BaseConverter", "SchwabConverter", "converter_mapping"]
