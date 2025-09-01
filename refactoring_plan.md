# Yahoo Finance CSV Converter 重構計劃

## 概述
這份文檔詳述了 Yahoo Finance CSV Converter 專案的重構計劃。重構的主要目標是提高程式碼質量、可維護性和可擴展性。

## 第一階段：統一命名慣例

### 問題描述
目前專案中同時使用了 "convertor" 和 "converter" 兩種拼法，這造成了不必要的混亂。正確的英文拼寫是 "converter"。

### 解決方案
統一使用 "converter" 拼寫。

### 具體步驟

1. **目錄重命名**
   - 將 `source_convertor` 目錄重命名為 `source_converter`

2. **類名修改**
   - `BaseSourceConvertor` → `BaseSourceConverter`
   - `SchwabConvertor` → `SchwabConverter`

3. **變數名修改**
   - 將所有的 `convertor` 變數重命名為 `converter`
   - 如：`convertor_mapping` → `converter_mapping`
   - 如：`convertor_class` → `converter_class`
   - 如：`convertor_type` → `converter_type`

4. **修改所有引用**
   - 更新所有引用舊名稱的地方
   - 包括：imports, 變數引用, 實例化等

### 預期變更的檔案
- `main.py`
- `source_convertor/__init__.py` → `source_converter/__init__.py`
- `source_convertor/base_convertor.py` → `source_converter/base_converter.py`
- `source_convertor/schwab_convertor.py` → `source_converter/schwab_converter.py`
- `source_convertor/utils.py` → `source_converter/utils.py`
- `source_convertor/config.py` → `source_converter/config.py`
- `gradio_app/converter/schwab_converter.py`
- `gradio_app/main.py`

## 第二階段：重構專案結構

### 問題描述
現有結構存在核心轉換邏輯和UI層混合的問題，職責分離不明確，這使得維護和擴展變得困難。

### 解決方案
明確分離核心邏輯和UI層，重組專案結構。

### 具體步驟

1. **創建新的目錄結構**

```
yahoo_finance_csv_converter/
├── src/
│   ├── converter/       # 核心轉換邏輯
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── schwab.py
│   │   ├── firstrade.py
│   │   ├── utils.py
│   │   └── config.py
│   ├── cli/            # 命令行介面
│   │   ├── __init__.py
│   │   └── main.py
│   └── web/            # Web介面（Gradio）
│       ├── __init__.py
│       ├── main.py
│       └── converters/
│           ├── __init__.py
│           ├── schwab.py
│           └── firstrade.py
├── tests/              # 測試目錄
│   ├── __init__.py
│   └── test_converters/
│       ├── __init__.py
│       ├── test_base.py
│       └── test_schwab.py
└── main.py            # 主入口點
```

2. **移動和重構核心邏輯**
   - 將 `source_converter` (已重命名) 的內容移至 `src/converter`
   - 將類和函數重命名為更符合慣例的名稱
   - 例如: `BaseSourceConverter` → `BaseConverter`

3. **移動和重構 Web UI**
   - 將 `gradio_app` 的內容移至 `src/web`
   - 更新所有引用

4. **移動和重構命令行介面**
   - 將 `main.py` 內容移至 `src/cli/main.py`
   - 創建一個新的 `main.py` 作為入口點

5. **更新引用路徑**
   - 修改所有 import 語句以反映新的結構
   - 確保相對引用正確

6. **更新 pyproject.toml**
   - 更新專案結構相關設定
   - 確保入口點正確

### 預期改進

1. **更清晰的關注點分離**
   - 核心轉換邏輯與UI解耦
   - 命令行與Web介面分離

2. **更好的可測試性**
   - 核心邏輯可以獨立測試
   - 依賴可以更容易地模擬(mock)

3. **更簡單的擴展**
   - 添加新的轉換器更容易
   - 可以獨立更改UI而不影響核心邏輯

### 重構後示例

**核心轉換器類 (`src/converter/base.py`)**

```python
from typing import Optional
import pandas as pd
from .config import DEFAULT_DUMMY_DATE

class BaseConverter:
    """Base class for all data converters."""
    
    converter_name = "base"
    
    def __init__(
        self,
        positions_data_path: str,
        history_data_path: str,
        fix_exceed_range: bool = False,
        default_dummy_date: Optional[str] = None,
    ):
        self.positions_data_path = positions_data_path
        self.history_data_path = history_data_path
        self.fix_exceed_range = fix_exceed_range
        self.default_dummy_date = default_dummy_date or DEFAULT_DUMMY_DATE
        
        self.positions_data_df: pd.DataFrame = pd.read_csv(positions_data_path)
        self.history_data_df: pd.DataFrame = pd.read_csv(history_data_path)
    
    def convert(self) -> pd.DataFrame:
        """Convert source data to Yahoo Finance format.
        
        Returns:
            pd.DataFrame: Converted data in Yahoo Finance format
        """
        raise NotImplementedError("Subclasses must implement this method")
```

**命令行介面 (`src/cli/main.py`)**

```python
import argparse
import logging
from pathlib import Path
import pandas as pd

from src.converter import converter_registry

def main():
    parser = argparse.ArgumentParser(description="Convert broker CSV data to Yahoo Finance format")
    parser.add_argument(
        "--converter-type", 
        type=str, 
        choices=converter_registry.keys(), 
        required=True,
        help="Type of converter to use"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        required=True,
        help="Output file path"
    )
    
    args_, _ = parser.parse_known_args()
    
    output_path = args_.output
    
    # Get converter class
    converter_class = converter_registry[args_.converter_type]
    logging.info(f"Using converter: {converter_class.converter_name}")
    
    # Add converter-specific arguments
    converter_class.add_arguments(parser)
    args = parser.parse_args()
    
    # Remove general args
    args_dict = vars(args)
    args_dict.pop("converter_type", None)
    args_dict.pop("output", None)
    
    # Initialize converter
    converter = converter_class(**args_dict)
    
    # Convert data
    df: pd.DataFrame = converter.convert()
    
    # Save result
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logging.info(f"Saving to {output_path}")
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
```

**入口點 (`main.py`)**

```python
import sys
from src.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
```

## 後續階段
- 改進錯誤處理和日誌機制
- 為核心功能添加單元測試
- 完善文檔（README.md，函數註解等）
- 完成Firstrade轉換器的實現
- 改進代碼質量（類型提示，程式碼風格等）
- 統一API設計，使添加新轉換器更容易
- 建立設定管理系統，方便配置不同轉換器參數