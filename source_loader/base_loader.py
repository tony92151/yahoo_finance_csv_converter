from pathlib import Path

import pandas as pd


class BaseSourceLoader:
    loader_name = "base_loader"

    def __init__(self, input_csv_path: str):
        if not Path(input_csv_path).exists():
            raise FileNotFoundError(f"File {input_csv_path} not found")

        self.data_df = pd.read_csv(input_csv_path)

    def convert(self):
        raise NotImplementedError()
