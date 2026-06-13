from __future__ import annotations

import pandas as pd

from .data import month_end_observation_dates
from .product import AutocallableTerms, evaluate_path


def rolling_backtest(price_df: pd.DataFrame, terms: AutocallableTerms) -> tuple[pd.DataFrame, list[dict]]:
    """Run a rolling monthly backtest.

    Each month starts a fresh hypothetical autocallable and observes it monthly
    until autocall or maturity.
    """
    obs = month_end_observation_dates(price_df)
    records: list[dict] = []
    paths: list[dict] = []

    max_start = len(obs) - terms.maturity_months - 1
    if max_start <= 0:
        raise ValueError("Not enough data for selected maturity.")

    for start_idx in range(max_start):
        path = obs.iloc[start_idx : start_idx + terms.maturity_months + 1].copy()
        result = evaluate_path(path, terms)
        records.append(
            {
                "start_date": result["start_date"],
                "end_date": result["end_date"],
                "initial_price": result["initial_price"],
                "final_price": result["final_price"],
                "called": result["called"],
                "call_month": result["call_month"],
                "principal_repaid": result["principal_repaid"],
                "coupons_paid": result["coupons_paid"],
                "total_payoff": result["total_payoff"],
                "total_return": result["total_return"],
                "annualized_return": result["annualized_return"],
            }
        )
        paths.append(result)

    return pd.DataFrame(records), paths


def summarize_results(results: pd.DataFrame) -> dict:
    """Create simple metrics for the strategy backtest."""
    if results.empty:
        return {}

    called_rate = float(results["called"].mean())
    loss_rate = float((results["total_return"] < 0).mean())
    avg_return = float(results["total_return"].mean())
    avg_ann_return = float(results["annualized_return"].mean())
    worst_return = float(results["total_return"].min())
    best_return = float(results["total_return"].max())
    avg_call_month = results.loc[results["called"], "call_month"].dropna().mean()

    return {
        "number_of_historical_issuances": int(len(results)),
        "autocall_rate": called_rate,
        "loss_rate": loss_rate,
        "average_total_return": avg_return,
        "average_annualized_return": avg_ann_return,
        "worst_total_return": worst_return,
        "best_total_return": best_return,
        "average_call_month": None if pd.isna(avg_call_month) else float(avg_call_month),
    }
