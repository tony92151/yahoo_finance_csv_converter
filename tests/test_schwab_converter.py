import warnings
from pathlib import Path

import pandas as pd
import pytest
from pandas.errors import SettingWithCopyWarning

from src.converter.cathay_sub_brokerage import CathaySubBrokerageConverter
from src.converter.config import DEFAULT_DUMMY_DATE
from src.converter.schwab import SchwabConverter, find_position_header_index
from src.converter.utils import yf_columns


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "example_data" / "schwab"
POSITIONS_PATH = FIXTURE_DIR / "positions.csv"
HISTORY_PATH = FIXTURE_DIR / "history.csv"

EXPECTED_SYMBOLS = [
    "AAPL",
    "AMD",
    "ARKF",
    "BAC",
    "BOXX",
    "GE",
    "JPM",
    "MRVL",
    "MSFT",
    "SNOW",
    "TSLA",
]

EXPECTED_CLOSED_SYMBOLS = [
    "CRWD",
    "HIMS",
    "INTC",
    "OKLO",
    "PYPL",
    "QQQ",
    "TEM",
    "URA",
]

EXPECTED_YF_COLUMNS = [
    "Symbol",
    "Trade Date",
    "Action",
    "Quantity",
    "Purchase Price",
    "Commission",
    "Comment",
]


def _load_expected_position_quantities() -> pd.Series:
    header_index = find_position_header_index(str(POSITIONS_PATH))
    assert header_index is not None

    positions = pd.read_csv(POSITIONS_PATH, skiprows=header_index)
    positions = positions.dropna(how="all").copy()
    positions = positions[positions["Symbol"].astype(str).str.isupper()].copy()

    quantities = positions.set_index("Symbol")["Qty (Quantity)"].astype(float)
    return quantities.sort_index()


def _signed_quantities_from_transaction_type(df: pd.DataFrame) -> pd.Series:
    signed_quantities = df["Quantity"].where(
        df["Action"] == "BUY",
        -df["Quantity"],
    )
    return signed_quantities.groupby(df["Symbol"]).sum().sort_index()


def test_schwab_fixture_converts_without_settingwithcopy_warning() -> None:
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
    )

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        result = converter.convert()

    settingwithcopy_warnings = [
        warning
        for warning in caught_warnings
        if issubclass(warning.category, SettingWithCopyWarning)
    ]
    assert settingwithcopy_warnings == []

    assert yf_columns == EXPECTED_YF_COLUMNS
    assert list(result.columns) == EXPECTED_YF_COLUMNS
    assert len(result) == 31
    required_columns = [
        "Symbol",
        "Trade Date",
        "Action",
        "Quantity",
        "Purchase Price",
    ]
    assert not result[required_columns].isna().any().any()
    assert set(result["Action"]) == {"BUY", "SELL"}


def test_schwab_fixture_exports_sell_rows_with_positive_quantity_positive_price_and_sell_type() -> (
    None
):
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
        include_closed_positions=True,
    )

    result = converter.convert()
    sell_rows = result[result["Comment"] == "correct to sell"]

    assert not sell_rows.empty
    assert (sell_rows["Action"] == "SELL").all()
    assert (sell_rows["Quantity"] > 0).all()
    assert (sell_rows["Purchase Price"] > 0).all()


def test_schwab_fixture_reconciles_quantities_to_positions() -> None:
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
    )

    result = converter.convert()
    expected_quantities = _load_expected_position_quantities()
    actual_quantities = _signed_quantities_from_transaction_type(result)

    assert expected_quantities.index.tolist() == EXPECTED_SYMBOLS
    pd.testing.assert_index_equal(
        actual_quantities.index,
        expected_quantities.index,
    )

    for symbol, expected_quantity in expected_quantities.items():
        assert actual_quantities[symbol] == pytest.approx(expected_quantity)


def test_schwab_fixture_can_include_closed_positions_from_history() -> None:
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
        include_closed_positions=True,
    )

    result = converter.convert()
    actual_closed_symbols = sorted(set(result["Symbol"]) - set(EXPECTED_SYMBOLS))

    assert actual_closed_symbols == EXPECTED_CLOSED_SYMBOLS
    assert len(result) > 31
    for symbol in EXPECTED_CLOSED_SYMBOLS:
        assert not result[result["Symbol"] == symbol].empty


def test_schwab_fixture_reconciles_closed_positions_to_zero(monkeypatch) -> None:
    completed_symbols: list[str] = []
    original_complete_history_data = SchwabConverter._complete_history_data

    def spy_complete_history_data(
        self: SchwabConverter,
        symbol: str,
        filtered_position_data_df: pd.DataFrame,
        filtered_history_data_df: pd.DataFrame,
    ) -> pd.DataFrame:
        completed_symbols.append(symbol)
        return original_complete_history_data(
            self,
            symbol,
            filtered_position_data_df,
            filtered_history_data_df,
        )

    monkeypatch.setattr(
        SchwabConverter,
        "_complete_history_data",
        spy_complete_history_data,
    )
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
        include_closed_positions=True,
    )

    result = converter.convert()
    closed_position_rows = result[result["Symbol"].isin(EXPECTED_CLOSED_SYMBOLS)]
    dummy_trade_date = pd.to_datetime(DEFAULT_DUMMY_DATE).strftime("%Y%m%d")
    closed_quantities = _signed_quantities_from_transaction_type(closed_position_rows)

    assert sorted(completed_symbols) == EXPECTED_SYMBOLS
    assert dummy_trade_date in closed_position_rows["Trade Date"].to_list()
    for symbol in EXPECTED_CLOSED_SYMBOLS:
        assert closed_quantities[symbol] == pytest.approx(0)


def test_schwab_fixture_reconciles_open_positions_when_closed_positions_included() -> (
    None
):
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
        include_closed_positions=True,
    )

    result = converter.convert()
    expected_quantities = _load_expected_position_quantities()
    open_position_rows = result[result["Symbol"].isin(EXPECTED_SYMBOLS)]
    actual_quantities = _signed_quantities_from_transaction_type(open_position_rows)

    pd.testing.assert_index_equal(
        actual_quantities.index,
        expected_quantities.index,
    )

    for symbol, expected_quantity in expected_quantities.items():
        assert actual_quantities[symbol] == pytest.approx(expected_quantity)


def test_cathay_converter_exports_sell_rows_with_positive_quantity_positive_price_and_sell_type(
    tmp_path: Path,
) -> None:
    statement_path = tmp_path / "cathay_statement.csv"
    pd.DataFrame(
        [
            {
                "交易日期": "2026/05/01",
                "商品代碼": "AAPL",
                "商品名稱": "Apple Inc.",
                "交易市場": "US",
                "交易種類": "買進",
                "交易幣別": "USD",
                "交割幣別": "USD",
                "股數": 2,
                "價格": 100,
                "匯率": 1,
                "成交金額": 200,
                "手續費": 1,
                "其他費用": 0.5,
                "應收/付(-)金額": -201.5,
            },
            {
                "交易日期": "2026/05/02",
                "商品代碼": "AAPL",
                "商品名稱": "Apple Inc.",
                "交易市場": "US",
                "交易種類": "賣出",
                "交易幣別": "USD",
                "交割幣別": "USD",
                "股數": 1,
                "價格": 110,
                "匯率": 1,
                "成交金額": 110,
                "手續費": 1,
                "其他費用": 0.5,
                "應收/付(-)金額": 108.5,
            },
        ]
    ).to_csv(statement_path, index=False)

    result = CathaySubBrokerageConverter(
        statement_of_account_file_path=str(statement_path)
    ).convert()
    sell_rows = result[result["Comment"] == "correct to sell"]

    assert not sell_rows.empty
    assert (sell_rows["Action"] == "SELL").all()
    assert (sell_rows["Quantity"] > 0).all()
    assert (sell_rows["Purchase Price"] > 0).all()
    assert set(result["Action"]) == {"BUY", "SELL"}
    assert list(result.columns) == EXPECTED_YF_COLUMNS
