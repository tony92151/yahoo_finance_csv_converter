import io
import logging
import os
import shutil
import tempfile

import gradio as gr

from source_convertor.schwab_convertor import SchwabConvertor


def process_file(file_history, file_position):
    # Set up a StringIO stream to capture logs
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)

    # Attach the handler to the root logger (or a specific logger if desired)
    logger = logging.getLogger()  # or e.g. logging.getLogger("source_convertor")
    logger.addHandler(stream_handler)

    try:
        # Initialize and run the convertor
        convertor = SchwabConvertor(
            history_data=file_history.name,
            positions_data=file_position.name,
            fix_exceed_range=True,
        )
        converted_result = convertor.convert()

        # Write the converted result to a temporary file
        temp_result = tempfile.NamedTemporaryFile(
            delete=False, mode="w", newline="", suffix=".csv"
        )
        converted_result.to_csv(temp_result, index=False)
        temp_result.close()

        # Create a new filename for the edited positions file
        output_position_file_name = os.path.basename(file_position.name).replace(
            ".csv", "_edit.csv"
        )
        shutil.move(temp_result.name, output_position_file_name)
    finally:
        # Remove our custom handler so we don't affect global logging
        logger.removeHandler(stream_handler)

    # Get the log output from our StringIO stream
    logs = log_stream.getvalue()

    # Return both the file and the logs
    return output_position_file_name, logs


# Update the Gradio interface to include an extra output for logs
schwab_converter = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload history file"),
        gr.File(label="Upload position file"),
    ],
    outputs=[
        gr.File(label="Download Position File"),
        gr.Textbox(label="Logs", lines=20),  # A textbox to display the logs
    ],
    flagging_mode="never",
)
