import gradio as gr
from converter import firstrade_converter, schwab_converter

demo = gr.TabbedInterface(
    [schwab_converter, firstrade_converter],
    ["schwab converter", "firstrade converter"],
    title="Yahoo Finance history data converter",
)

demo.launch()
