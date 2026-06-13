from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from autocallable.backtest import rolling_backtest, summarize_results
from autocallable.data import load_prices
from autocallable.product import AutocallableTerms


st.set_page_config(page_title="AGQ Autocallable Simulator", layout="wide")

st.title("AGQ Autocallable Strategy Simulator")
st.caption("Educational structured-product simulator for interview preparation. Not financial advice.")

with st.sidebar:
    st.header("Product terms")
    ticker = st.text_input("Ticker", value="AGQ")
    start_date = st.date_input("Historical start date", value=pd.to_datetime("2015-01-01"))
    notional = st.number_input("Notional", min_value=10.0, value=100.0, step=10.0)
    maturity_months = st.slider("Maturity months", min_value=3, max_value=36, value=12, step=1)
    autocall_barrier_pct = st.slider("Autocall barrier (% of initial)", 80, 160, 110, 1)
    protection_barrier_pct = st.slider("Protection barrier (% of initial)", 30, 100, 70, 1)
    monthly_coupon_pct = st.slider("Monthly coupon (%)", 0.0, 10.0, 2.0, 0.1)

    st.header("Coupon settings")
    coupon_mode = st.radio("Coupon type", ["unconditional", "conditional"], index=0)
    coupon_barrier_pct = st.slider("Coupon barrier (% of initial)", 30, 120, 70, 1)
    coupon_memory = st.checkbox("Coupon memory", value=True)

terms = AutocallableTerms(
    notional=notional,
    maturity_months=maturity_months,
    autocall_barrier=autocall_barrier_pct / 100,
    protection_barrier=protection_barrier_pct / 100,
    monthly_coupon=monthly_coupon_pct / 100,
    coupon_barrier=coupon_barrier_pct / 100,
    coupon_mode=coupon_mode,
    coupon_memory=coupon_memory,
)

with st.expander("Simple explanation of the structure", expanded=True):
    st.markdown(
        f"""
        This simulator creates a simplified autocallable on **{ticker}**.

        - Initial investment: **${notional:,.2f}**
        - Monthly coupon: **{monthly_coupon_pct:.2f}%**
        - Autocall trigger: if {ticker} is at or above **{autocall_barrier_pct}%** of its starting price on an observation date
        - Protection barrier: **{protection_barrier_pct}%** of starting price
        - Maturity: **{maturity_months} months**

        In interview language: this is a path-dependent payoff. The outcome depends not only on the final price,
        but also whether the ETF crossed the autocall barrier on observation dates.
        """
    )

try:
    prices = load_prices(ticker=ticker, start=str(start_date))
    results, paths = rolling_backtest(prices, terms)
    summary = summarize_results(results)
except Exception as exc:
    st.error(f"Could not run simulation: {exc}")
    st.stop()

st.subheader(f"{ticker} historical price")
fig_price = px.line(prices, x="date", y="close", title=f"{ticker} adjusted close")
st.plotly_chart(fig_price, use_container_width=True)

st.subheader("Backtest summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Historical issuances", f"{summary['number_of_historical_issuances']}")
col2.metric("Autocall rate", f"{summary['autocall_rate']:.1%}")
col3.metric("Loss rate", f"{summary['loss_rate']:.1%}")
col4.metric("Avg annualized return", f"{summary['average_annualized_return']:.1%}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Avg total return", f"{summary['average_total_return']:.1%}")
col6.metric("Worst total return", f"{summary['worst_total_return']:.1%}")
col7.metric("Best total return", f"{summary['best_total_return']:.1%}")
avg_call = summary["average_call_month"]
col8.metric("Avg call month", "N/A" if avg_call is None else f"{avg_call:.1f}")

st.subheader("Distribution of historical note returns")
fig_hist = px.histogram(results, x="total_return", nbins=40, title="Total return distribution")
st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Rolling issuance results")
show = results.copy()
show["start_date"] = pd.to_datetime(show["start_date"]).dt.date
show["end_date"] = pd.to_datetime(show["end_date"]).dt.date
st.dataframe(show, use_container_width=True)

st.subheader("Inspect one historical path")
selected_idx = st.slider("Select issuance number", 0, len(paths) - 1, min(5, len(paths) - 1))
selected = paths[selected_idx]
obs = selected["observations"].copy()

st.write(
    f"Start: **{pd.to_datetime(selected['start_date']).date()}**, "
    f"End: **{pd.to_datetime(selected['end_date']).date()}**, "
    f"Called: **{selected['called']}**, "
    f"Total return: **{selected['total_return']:.1%}**"
)

if not obs.empty:
    fig_path = px.line(obs, x="date", y="price", title="Observation path")
    fig_path.add_hline(y=obs["autocall_level"].iloc[0], annotation_text="Autocall level")
    fig_path.add_hline(y=obs["protection_level"].iloc[0], annotation_text="Protection level")
    st.plotly_chart(fig_path, use_container_width=True)
    st.dataframe(obs, use_container_width=True)

st.subheader("How to explain this in an interview")
st.markdown(
    """
    **Short answer:** I designed a simplified AGQ autocallable simulator. It takes historical AGQ prices,
    creates rolling monthly issuances, checks whether the autocall barrier was hit, pays coupons, and applies
    downside protection at maturity.

    **Quant point:** The payoff is path-dependent because two paths with the same final price can have different
    outcomes if one path hit the autocall barrier earlier.

    **Model risk point:** This is a backtest, not a fair-value model. A real pricing model would need a volatility
    surface, funding curve, dividends, dealer margin, and probably Monte Carlo simulation under a risk-neutral measure.
    """
)
