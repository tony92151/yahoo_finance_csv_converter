"""
Schwab broker data converter implementation.
"""

import argparse
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .base import BaseConverter
from .utils import yf_columns

# 2025-01 record columns definition for Schwab CSV format
cathay_columns = [
    "交易日期",
    "商品代碼",
    "商品名稱",
    "交易市場",
    "交易種類",
    "交易幣別",
    "交割幣別",
    "股數",
    "價格",
    "匯率",
    "成交金額",
    "手續費",
    "其他費用",
    "應收/付(-)金額",
]

# Mapping from Schwab columns to Yahoo Finance columns
column_mapping = {
    "交易日期": "Trade Date",
    "股數": "Quantity",
    "價格": "Purchase Price",
    "手續費": "Commission",
}


class CathaySubBrokerageConverter(BaseConverter):
    converter_name = "CathaySubBrokerage"

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add Schwab specific arguments to CLI parser.

        Args:
            parser: The argument parser to add arguments to
        """
        BaseConverter.add_arguments(parser)

    def __init__(
        self,
        statement_of_account_file_path: str,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.df = pd.read_csv(statement_of_account_file_path)

        self.pre_check()

    def pre_check(self) -> None:
        if not all(col in self.df.columns for col in cathay_columns):
            raise ValueError(
                f"Columns in {self.history_data_path} do not match columns. Please update the schema."
            )

    def convert(self) -> pd.DataFrame:

        # add column "total_Commission" = "手續費" + "其他費用"
        self.df["total_commission"] = self.df["手續費"] + self.df["其他費用"]

        # remove rows where "交易種類" is not "買進" or "賣出"
        self.df = self.df[self.df["交易種類"].isin(["買進", "賣出"])]

        # if column "交易種類" is "賣出" then "股數" should be negative
        comment_list = []
        quantity_list = []

        for _, row in self.df.iterrows():
            if row["交易種類"] == "賣出":
                quantity_list.append(float(row["股數"]) * -1)
                comment_list.append("correct to sell")
            else:
                quantity_list.append(row["股數"])
                comment_list.append("")

        self.df["Quantity"] = quantity_list
        self.df["Comment"] = comment_list

        # reformat daate from yyyy/mm/dd to yyyymmdd
        self.df["Trade Date"] = pd.to_datetime(self.df["交易日期"]).dt.strftime(
            "%Y%m%d"
        )

        # rename columns
        self.df = self.df.rename(
            columns={
                "商品代碼": "Symbol",
                "價格": "Purchase Price",
                "total_commission": "Commission",
            }
        )

        self.df = self.df[
            [
                "Trade Date",
                "Symbol",
                "Quantity",
                "Purchase Price",
                "Commission",
                "Comment",
            ]
        ]

        return self.df
