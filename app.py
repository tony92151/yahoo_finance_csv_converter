import gradio as gr
import pandas as pd
import io
import time

def convert_file(data_source, csv_file):
    """
    這裡是主要的轉換函式。
    data_source: 下拉式選單的選擇 (schwab, firstrade, binance)
    csv_file: 上傳的 CSV 檔案
    """
    # 若未上傳檔案，直接回傳空值
    if csv_file is None:
        return gr.update(value=None, visible=False), None, None

    # 模擬「轉換動畫」或進度，例如：等待 2 秒
    time.sleep(2)

    # 使用 pandas 讀取上傳的 CSV
    df = pd.read_csv(csv_file.name)

    # (示範) 在此處根據 data_source 進行對應的處理或轉換
    # 這裡只是簡單示範新增一個欄位
    df["data_source"] = data_source

    # 將轉換後的 df 轉回 CSV 字串
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # 產生可供下載的檔案內容 (tuple 格式: (檔案內容, 檔名))
    download_file = (csv_buffer.getvalue(), "converted.csv")

    return gr.update(value=None, visible=False), df, download_file


with gr.Blocks() as demo:
    gr.Markdown("# CSV 轉換工具")

    # 1. 下拉式選單選擇資料來源
    data_source = gr.Dropdown(
        label="選擇資料來源",
        choices=["schwab", "firstrade", "binance"],
        value="schwab",
    )

    # 2. 上傳 CSV 檔
    csv_upload = gr.File(
        label="上傳您的 CSV 檔",
        file_types=[".csv"]
    )

    # 3. 轉換按鈕
    convert_button = gr.Button("開始轉換")

    # 4. 轉換動畫 / 進度顯示
    #    這裡簡易使用一個 Markdown 來顯示「轉換中...」，在函式執行時顯示
    with gr.Box(visible=False) as converting_box:
        converting_text = gr.Markdown("### 轉換中，請稍候...")

    # 5. 用表格顯示轉換結果
    result_table = gr.DataFrame(
        label="轉換後的資料預覽",
        headers=[],
        datatype="auto"
    )

    # 6. 下載轉換後的 CSV 檔鈕 (gr.File 可以作為可下載連結)
    download_file = gr.File(label="下載轉換後的 CSV", interactive=False)

    # 綁定 convert_button 點擊事件：
    # - 先顯示 converting_box
    # - 執行 convert_file 函式
    # - 結束後隱藏 converting_box
    convert_button.click(
        fn=None,
        inputs=None,
        outputs=converting_box,
        _js="(x) => { return {visible:true}; }",  # 先讓動畫/提示出現
        queue=False
    )

    convert_button.click(
        fn=convert_file,
        inputs=[data_source, csv_upload],
        outputs=[converting_box, result_table, download_file],
        queue=True
    )

demo.launch()