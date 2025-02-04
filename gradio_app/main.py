import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

import gradio as gr
from converter import firstrade_converter, schwab_converter

logging.basicConfig(level=logging.INFO)

demo = gr.TabbedInterface(
    [schwab_converter, firstrade_converter],
    ["schwab converter", "firstrade converter"],
    title="Yahoo Finance history data converter",
)

demo.launch()
