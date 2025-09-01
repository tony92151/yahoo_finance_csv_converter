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

from src.converter.cathay_sub_brokerage import CathaySubBrokerageConverter


def process_file(statement_of_account: Any, file_position: Any) -> Tuple[str, str]:
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(stream_handler)

    try:
        # Initialize and run the converter
        converter = CathaySubBrokerageConverter(
            statement_of_account_file_path=statement_of_account.name,
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
cathay_sub_brokerage_converter = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload Statement of Account file (CSV format)"),
    ],
    outputs=[
        gr.File(label="Download Yahoo Finance Format CSV"),
        gr.Textbox(label="Conversion Logs", lines=20),
    ],
    title="Cathay sub-brokerage to Yahoo Finance Converter",
    description="Convert Cathay sub-brokerage CSV files to Yahoo Finance format for portfolio import.",
    article="""
    ### Instructions
    1. Upload your Statement of Account file (transactions)
    2. Click "Submit" to convert the files
    3. Download the resulting Yahoo Finance compatible CSV
    """,
    flagging_mode="never",
)
