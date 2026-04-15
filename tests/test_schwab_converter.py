import warnings
from pathlib import Path

import pandas as pd
import pytest
from pandas.errors import SettingWithCopyWarning

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


def _load_expected_position_quantities() -> pd.Series:
    header_index = find_position_header_index(str(POSITIONS_PATH))
    assert header_index is not None

    positions = pd.read_csv(POSITIONS_PATH, skiprows=header_index)
    positions = positions.dropna(how="all").copy()
    positions = positions[positions["Symbol"].astype(str).str.isupper()].copy()

    quantities = positions.set_index("Symbol")["Qty (Quantity)"].astype(float)
    return quantities.sort_index()


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

    assert list(result.columns) == yf_columns
    assert len(result) == 31
    required_columns = ["Symbol", "Trade Date", "Quantity", "Purchase Price"]
    assert not result[required_columns].isna().any().any()


def test_schwab_fixture_reconciles_quantities_to_positions() -> None:
    converter = SchwabConverter(
        positions_data_path=str(POSITIONS_PATH),
        history_data_path=str(HISTORY_PATH),
        fix_exceed_range=True,
    )

    result = converter.convert()
    expected_quantities = _load_expected_position_quantities()
    actual_quantities = result.groupby("Symbol")["Quantity"].sum().sort_index()

    assert expected_quantities.index.tolist() == EXPECTED_SYMBOLS
    pd.testing.assert_index_equal(
        actual_quantities.index,
        expected_quantities.index,
    )

    for symbol, expected_quantity in expected_quantities.items():
        assert actual_quantities[symbol] == pytest.approx(expected_quantity)
