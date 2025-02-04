import os
import shutil
import tempfile

import gradio as gr
import pandas as pd

from source_convertor.schwab_convertor import SchwaConvertor


def process_file(file_history, file_position):
    convertor = SchwaConvertor(
        history_data=file_history.name,
        positions_data=file_position.name,
        fix_exceed_range=True,
    )

    converted_result = convertor.convert()

    temp_result = tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", suffix=".csv"
    )

    converted_result.to_csv(temp_result, index=False)

    temp_result.close()

    output_position_file_name = os.path.basename(file_position.name).replace(
        ".csv", "_edit.csv"
    )
    shutil.move(temp_result.name, output_position_file_name)

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
