---
title: Yahoo Finance source csv data converter
emoji: 😻
colorFrom: green
colorTo: indigo
sdk: gradio
sdk_version: 5.23.2
app_file: gradio_app/main.py
pinned: false
license: mit
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# yahoo finance csv converter

App on [HuggingFace space](https://huggingface.co/spaces/tony92151/yahoo_finance_csv_converter)

### schwab converter
```bash
python main.py \
    --convertor-type schwab \
    --output ./output.csv \
    --history-data ./Individual_XXXXXX_Transactions.csv \
    --positions-data XXX-Positions-2025-01-28--XXXXXX.csv \
    --fix-exceed-range
```
