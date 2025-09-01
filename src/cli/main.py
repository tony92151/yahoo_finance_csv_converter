"""
Command line interface for Yahoo Finance CSV converter.
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from src.converter import converter_mapping
from src.converter.base import BaseConverter


def main() -> int:
    """
    Main entry point for the command line interface.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Convert broker CSV data to Yahoo Finance format"
    )
    parser.add_argument(
        "--converter-type",
        type=str,
        choices=list(converter_mapping.keys()),
        required=True,
        help="Type of converter to use (e.g., schwab)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output file path for the converted CSV",
    )

    # Parse initial arguments to get the converter type
    args_, _ = parser.parse_known_args()
    output_path = args_.output

    try:
        # Get converter class
        converter_class = converter_mapping[args_.converter_type]
        logging.info(f"Using converter: {converter_class.converter_name}")

        # Add converter-specific arguments
        converter_class.add_arguments(parser)
        args = parser.parse_args()

        # Remove common args from the dictionary
        args_dict = vars(args)
        args_dict.pop("converter_type", None)
        args_dict.pop("output", None)

        # Initialize converter
        converter: BaseConverter = converter_class(**args_dict)

        # Convert data
        df: pd.DataFrame = converter.convert()

        # Ensure output directory exists
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Save the result
        logging.info(f"Saving to {output_path}")
        df.to_csv(output_path, index=False)
        logging.info(f"Successfully converted data to {output_path}")

        return 0
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logging.error(f"Value error: {e}")
        return 2
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 3


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    sys.exit(main())
