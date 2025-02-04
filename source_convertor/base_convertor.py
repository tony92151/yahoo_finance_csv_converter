import argparse
from pathlib import Path

import pandas as pd


class BaseSourceConvertor:
    loader_name = "base"

    def __init__(self, **kwargs):
        pass

    def convert(self):
        raise NotImplementedError()

    @staticmethod
    def add_argument(parser: argparse.ArgumentParser):
        pass
