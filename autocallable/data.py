from __future__ import annotations

import pandas as pd
import yfinance as yf


def load_prices(ticker: str = "AGQ", start: str = "2015-01-01") -> pd.DataFrame:
    """Download adjusted close prices from Yahoo Finance.

    Returns a dataframe with columns: date, close.
    """
    raw = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if raw.empty:
        raise ValueError(f"No price data returned for ticker={ticker}")

    close = raw["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    df = close.rename("close").reset_index()
    df.columns = ["date", "close"]
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna().sort_values("date").reset_index(drop=True)
    return df


def month_end_observation_dates(price_df: pd.DataFrame) -> pd.DataFrame:
    """Return one observation row per month using last available trading day."""
    df = price_df.copy()
    df["month"] = df["date"].dt.to_period("M")
    obs = df.groupby("month", as_index=False).tail(1)
    return obs[["date", "close"]].reset_index(drop=True)
