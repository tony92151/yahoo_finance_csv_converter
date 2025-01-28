import gradio as gr
import pandas as pd
import time

# 轉換處理函式範例
def convert_data(source, file):
    # 模擬轉換過程
    time.sleep(2)
    
    # 載入 CSV 檔案
    df = pd.read_csv(file.name)
    
    # 假設轉換是某種數據處理，這裡可以根據選擇的資料來源進行不同處理
    if source == "schwab":
        df["Converted"] = df["Amount"] * 1.1  # 假設轉換邏輯
    elif source == "firstrade":
        df["Converted"] = df["Amount"] * 1.2
    elif source == "binance":
        df["Converted"] = df["Amount"] * 1.3
    
    return df

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 轉換工具")
    
    # 步驟 1: 資料來源選擇
    source_dropdown = gr.Dropdown(choices=["schwab", "firstrade", "binance"], label="選擇資料來源")
    
    # 步驟 2: 上傳CSV檔案
    file_upload = gr.File(file_types=[".csv"], label="上傳CSV檔")
    
    # 步驟 3: 轉換鈕
    convert_button = gr.Button("開始轉換")
    
    # 步驟 4: 顯示轉換動畫
    with gr.Row():
        loading_animation = gr.Image("https://loading.io/spinners/rolling/lg.roll-gear-loader.gif", visible=False)
    
    # 步驟 5: 顯示轉換結果的Table
    result_table = gr.DataFrame(label="轉換結果")
    
    # 步驟 6: 下載轉換後的CSV檔案
    download_button = gr.File(label="下載轉換後的CSV檔案", visible=False)

    # 轉換按鈕觸發的動作
    def on_convert_button_click(source, file):
        loading_animation.visible = True
        # 轉換過程
        converted_data = convert_data(source, file)
        # 顯示結果
        result_table.update(converted_data)
        # 顯示下載按鈕
        download_button.update(value=converted_data.to_csv(index=False), visible=True)
        loading_animation.visible = False

    convert_button.click(on_convert_button_click, inputs=[source_dropdown, file_upload], outputs=[result_table, download_button, loading_animation])

demo.launch()
