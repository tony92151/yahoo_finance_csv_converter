"""
Schwab converter web interface component.
"""

import io
import logging
import os
import shutil
import tempfile
from typing import Any, Tuple

import gradio as gr

from src.converter.schwab import SchwabConverter


def process_file(file_history: Any, file_position: Any) -> Tuple[str, str]:
    """
    Process uploaded Schwab files and convert to Yahoo Finance format.

    Args:
        file_history: Uploaded history file
        file_position: Uploaded position file

    Returns:
        Tuple containing the output file name and log messages
    """
    # Set up a StringIO stream to capture logs
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)

    # Attach the handler to the root logger
    logger = logging.getLogger()
    logger.addHandler(stream_handler)

    try:
        # Initialize and run the converter
        converter = SchwabConverter(
            history_data_path=file_history.name,
            positions_data_path=file_position.name,
            fix_exceed_range=True,
        )
        converted_result = converter.convert()

        # Write the converted result to a temporary file
        temp_result = tempfile.NamedTemporaryFile(
            delete=False, mode="w", newline="", suffix=".csv"
        )
        converted_result.to_csv(temp_result, index=False)
        temp_result.close()

        # Create a new filename for the converted file
        output_position_file_name = os.path.basename(file_position.name).replace(
            ".csv", "_yahoo_finance.csv"
        )
        shutil.move(temp_result.name, output_position_file_name)
    except Exception as e:
        # Log any exceptions
        logger.error(f"Error processing files: {e}", exc_info=True)
        output_position_file_name = None
    finally:
        # Remove our custom handler so we don't affect global logging
        logger.removeHandler(stream_handler)

    # Get the log output from our StringIO stream
    logs = log_stream.getvalue()

    # Return both the file and the logs
    return output_position_file_name, logs


# Gradio interface for Schwab converter
schwab_converter = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload history file (CSV format)"),
        gr.File(label="Upload position file (CSV format)"),
    ],
    outputs=[
        gr.File(label="Download Yahoo Finance Format CSV"),
        gr.Textbox(label="Conversion Logs", lines=20),
    ],
    title="Schwab to Yahoo Finance Converter",
    description="Convert Schwab CSV files to Yahoo Finance format for portfolio import.",
    article="""
    ### Instructions
    1. Upload your Schwab history file (transactions)
    2. Upload your Schwab positions file (current holdings)
    3. Click "Submit" to convert the files
    4. Download the resulting Yahoo Finance compatible CSV
    """,
    flagging_mode="never",
)
