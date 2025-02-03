import gradio as gr


def process_text(text):
    return f"Processed text: {text}"


firstrade_converter = gr.Interface(fn=process_text, inputs="text", outputs="text")
