# AGQ Autocallable Strategy Simulator

Educational Python/Streamlit project to design and backtest a simplified **autocallable structured note** on **AGQ** — the ProShares Ultra Silver leveraged ETF.

> This is for interview preparation and learning only. It is **not financial advice**, not a tradable recommendation, and not a production-grade pricing model.

## What this project demonstrates

This project is designed to help you explain, in a quant interview, how an autocallable can be structured, priced conceptually, and backtested.

It shows:

- How an autocallable note is layered
- How coupon payments work
- How an autocall barrier triggers early redemption
- How downside protection works
- How to run a rolling historical backtest on AGQ
- How to simulate different coupon, barrier, maturity, and protection assumptions

## Product intuition

An autocallable is a structured product linked to an underlying asset.

For this project, the underlying is AGQ.

A simplified autocallable works like this:

1. Investor invests a notional amount, for example $100.
2. Every month, the product observes AGQ's price.
3. If AGQ is above the autocall barrier, the note ends early.
4. If it autocalls, investor receives principal plus the coupon for that period.
5. If it does not autocall, the note continues.
6. At maturity, if AGQ is above the protection barrier, principal is returned.
7. If AGQ is below the protection barrier, investor participates in the downside loss.

## Example

Assume:

- Initial AGQ price: 100
- Autocall barrier: 110% of initial price = 110
- Protection barrier: 70% of initial price = 70
- Monthly coupon: 2%
- Maturity: 12 months
- Notional: $100

Scenario A: AGQ reaches 112 at month 4

- Product autocalls
- Investor receives $100 principal + accumulated coupons
- Product ends early

Scenario B: AGQ never reaches 110, but ends at 90

- No autocall
- Principal is returned at maturity
- Investor keeps coupons already earned

Scenario C: AGQ never reaches 110, and ends at 55

- No autocall
- Downside barrier is breached
- Investor receives approximately $55 instead of $100
- Coupons may reduce part of the loss, depending on structure

## Why AGQ is interesting

AGQ is a leveraged silver ETF, so it can be highly volatile. Autocallables are sensitive to volatility, path behavior, and barrier levels. This makes AGQ useful for learning how structured products behave under extreme price movement.

## Project structure

```text
.
├── app.py                         # Streamlit localhost app
├── autocallable/
│   ├── __init__.py
│   ├── data.py                    # Download/load AGQ prices
│   ├── product.py                 # Product parameters and payoff engine
│   └── backtest.py                # Rolling historical backtest
├── requirements.txt
└── README.md
```

## Setup

Clone the repository:

```bash
git clone https://github.com/deepsanghavi1002/Personal-trading-project.git
cd Personal-trading-project
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the localhost app:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## How to use

In the app sidebar, adjust:

- Ticker: AGQ by default
- Start date
- Maturity months
- Observation frequency
- Autocall barrier
- Coupon rate
- Protection barrier
- Coupon memory on/off
- Notional amount

Then review:

- AGQ historical price chart
- Rolling autocallable backtest results
- Distribution of note returns
- Summary metrics
- Sample trade paths

## Interview explanation

A good interview explanation:

> I built a simplified autocallable simulator on AGQ to understand how structured product payoffs depend on path behavior. The model checks monthly observation dates, pays coupons, triggers early redemption when the autocall barrier is reached, and applies downside protection at maturity. The goal is not to produce a bank-grade price, but to demonstrate product intuition, payoff logic, backtesting discipline, and Python implementation.

## What is simplified here

A real bank model would also include:

- Full volatility surface
- Funding curve
- Dividend assumptions
- Borrow/financing costs
- Dealer margin
- Secondary-market unwind value
- Stochastic volatility or local volatility models
- Monte Carlo pricing under a risk-neutral measure
- Dynamic hedging and Greeks

This project intentionally keeps the first version simple so the payoff logic is easy to understand and explain.

## Next improvements

Good follow-up improvements for interview discussion:

1. Add Monte Carlo pricing.
2. Add delta and vega estimation.
3. Add volatility regime filters.
4. Compare AGQ with SLV.
5. Add PCA/clustering to identify hedge instruments.
6. Add option-implied volatility assumptions.
7. Add transaction costs and slippage.

