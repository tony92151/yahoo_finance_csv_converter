import pandas as pd

from .base_loader import BaseSourceLoader

# 202501 record columns
schwab_columns = [
    "Date",
    "Action",
    "Symbol",
    "Description",
    "Quantity",
    "Price",
    "Fees & Comm",
    "Amount",
]
yf_columns = [
    "Symbol",
    "Trade Date",
    "Quantity",
    "Purchase Price",
    "Commission",
    "Comment",
]


column_mapping = {
    "Date": "Trade Date",
    "Quantity": "Quantity",
    "Price": "Purchase Price",
    "Fees & Comm": "Commission",
}


class SchwabLoader(BaseSourceLoader):
    loader_name = "schwab"

    def __init__(self, input_csv_path):
        super().__init__(input_csv_path)

        # check if self.data_df has the correct columns
        if not all(col in self.data_df.columns for col in schwab_columns):
            raise ValueError(
                f"Columns in {input_csv_path} do not match Schwab columns. Pleae update the schema."
            )

    def convert(self) -> pd.DataFrame:
        # map columns to yf_columns
        self.data_df = self.data_df.rename(columns=column_mapping)

        self.data_df = self.data_df.dropna(subset=["Quantity", "Purchase Price"])

        # add 'Comment' column to the dataframe if it doesn't exist
        if "Comment" not in self.data_df.columns:
            self.data_df["Comment"] = ""

        # edit "Quantity" to negative if "Action" is "Sell"
        self.data_df.loc[self.data_df["Action"] == "Sell", "Quantity"] = -abs(
            self.data_df["Quantity"]
        )

        # edit "Comment" column to 'correct to sell' if "Action" is "Sell"
        self.data_df.loc[
            self.data_df["Action"] == "Sell", "Comment"
        ] = "correct to sell"
        self.data_df.loc[
            self.data_df["Action"] == "Reinvest Shares", "Comment"
        ] = "Reinvest Shares"

        # return the dataframe only with yf_columns
        self.data_df = self.data_df[yf_columns]

        # remove the $ in "Purchase Price"	and "Commission"
        self.data_df["Purchase Price"] = self.data_df["Purchase Price"].str.replace(
            "$", ""
        )
        self.data_df["Commission"] = self.data_df["Commission"].str.replace("$", "")

        # the orignal "Trade Date" is in the format of "mm/dd/yyyy" update to "yyyymmdd"
        self.data_df["Trade Date"] = pd.to_datetime(
            self.data_df["Trade Date"]
        ).dt.strftime("%Y%m%d")

        return self.data_df
