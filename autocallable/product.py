from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


CouponMode = Literal["unconditional", "conditional"]


@dataclass(frozen=True)
class AutocallableTerms:
    """Simplified autocallable note terms.

    This is intentionally beginner-friendly and not a bank-grade term sheet.
    """

    notional: float = 100.0
    maturity_months: int = 12
    autocall_barrier: float = 1.10
    protection_barrier: float = 0.70
    monthly_coupon: float = 0.02
    coupon_barrier: float = 0.70
    coupon_mode: CouponMode = "unconditional"
    coupon_memory: bool = True


def evaluate_path(path: pd.DataFrame, terms: AutocallableTerms) -> dict:
    """Evaluate one autocallable trade path.

    path must contain monthly observation rows with columns date and close.
    The first row is treated as the trade start.
    """
    if len(path) < 2:
        raise ValueError("Path must contain at least start and one observation.")

    start_date = path.iloc[0]["date"]
    initial_price = float(path.iloc[0]["close"])
    autocall_level = initial_price * terms.autocall_barrier
    protection_level = initial_price * terms.protection_barrier
    coupon_level = initial_price * terms.coupon_barrier

    coupons_paid = 0.0
    missed_coupons = 0
    observations = []
    called = False
    final_price = float(path.iloc[-1]["close"])
    final_date = path.iloc[-1]["date"]

    # Observations start after trade date.
    for obs_number, (_, row) in enumerate(path.iloc[1:].iterrows(), start=1):
        obs_date = row["date"]
        price = float(row["close"])
        coupon_paid_this_obs = 0.0

        if terms.coupon_mode == "unconditional":
            coupon_paid_this_obs = terms.notional * terms.monthly_coupon
        else:
            if price >= coupon_level:
                coupon_count = 1 + missed_coupons if terms.coupon_memory else 1
                coupon_paid_this_obs = terms.notional * terms.monthly_coupon * coupon_count
                missed_coupons = 0
            else:
                missed_coupons += 1

        coupons_paid += coupon_paid_this_obs

        observations.append(
            {
                "obs_number": obs_number,
                "date": obs_date,
                "price": price,
                "return_from_initial": price / initial_price - 1.0,
                "coupon_paid": coupon_paid_this_obs,
                "autocall_level": autocall_level,
                "coupon_level": coupon_level,
                "protection_level": protection_level,
            }
        )

        if price >= autocall_level:
            called = True
            final_price = price
            final_date = obs_date
            principal_repaid = terms.notional
            total_payoff = principal_repaid + coupons_paid
            return {
                "start_date": start_date,
                "end_date": final_date,
                "initial_price": initial_price,
                "final_price": final_price,
                "called": True,
                "call_month": obs_number,
                "principal_repaid": principal_repaid,
                "coupons_paid": coupons_paid,
                "total_payoff": total_payoff,
                "total_return": total_payoff / terms.notional - 1.0,
                "annualized_return": (total_payoff / terms.notional) ** (12 / obs_number) - 1.0,
                "observations": pd.DataFrame(observations),
            }

    # If not autocalled, evaluate final maturity protection.
    if final_price >= protection_level:
        principal_repaid = terms.notional
    else:
        # Downside participation: if AGQ falls 50%, investor receives roughly 50% of principal.
        principal_repaid = terms.notional * (final_price / initial_price)

    total_payoff = principal_repaid + coupons_paid
    months_held = max(1, len(path) - 1)
    return {
        "start_date": start_date,
        "end_date": final_date,
        "initial_price": initial_price,
        "final_price": final_price,
        "called": False,
        "call_month": None,
        "principal_repaid": principal_repaid,
        "coupons_paid": coupons_paid,
        "total_payoff": total_payoff,
        "total_return": total_payoff / terms.notional - 1.0,
        "annualized_return": (total_payoff / terms.notional) ** (12 / months_held) - 1.0,
        "observations": pd.DataFrame(observations),
    }
