import os
import shutil
import tempfile

import gradio as gr
import pandas as pd


def process_file(file_history, file_position):
    df_history = pd.read_csv(file_history.name)
    df_position = pd.read_csv(file_position.name)

    temp_history = tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", suffix=".csv"
    )
    temp_position = tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", suffix=".csv"
    )

    # TODO:
    # Implement the logic to convert Schwab history and position file

    df_position.to_csv(temp_position, index=False)

    temp_history.close()
    temp_position.close()

    output_position_file_name = os.path.basename(file_position.name).replace(
        ".csv", "_edit.csv"
    )
    shutil.move(temp_position.name, output_position_file_name)

    return output_position_file_name


schwab_converter = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload history file"),
        gr.File(label="Upload position file"),
    ],
    outputs=[gr.File(label="Download Position File")],
    flagging_mode="never",
)
