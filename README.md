---
title: Yahoo Finance CSV Converter
emoji: 😻
colorFrom: green
colorTo: indigo
sdk: gradio
sdk_version: 5.23.2
app_file: app.py
pinned: false
license: mit
---

# Yahoo Finance CSV Converter

App on [HuggingFace space](https://huggingface.co/spaces/tony92151/yahoo_finance_csv_converter)

Convert broker CSV data to Yahoo Finance compatible format for portfolio import.

## Command Line Usage

```bash
python main.py \
    --converter-type schwab \
    --output ./output.csv \
    --history-data ./Individual_XXXXXX_Transactions.csv \
    --positions-data XXX-Positions-2025-01-28--XXXXXX.csv \
    --fix-exceed-range
```

## Web Interface

```bash
python app.py
```

## Supported Brokers

- Schwab
