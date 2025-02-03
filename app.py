import gradio as gr

title = "Yahoo Finance history data converter"

#app 1
def schwab_converter(path: str):
    return "Hi! " + path + " Welcome to your first Gradio application!😎"

#app 2
def firstrade_converter(do):
    return "So today we will do " + do + "using Gradio. Great choice!"

#interface 1
app1 =  gr.Interface(fn = schwab_converter, inputs="text", outputs="text")
#interface 2

app2 =  gr.Interface(fn = firstrade_converter, inputs="text", outputs="text")

demo = gr.TabbedInterface([app1, app2], ["schwab converter", "firstrade converter"], title=title)

demo.launch()