from portfolio import OptionPosition, Portfolio
from pricer import price_option
from scenarios import generate_heston_scenarios
from margin import estimate_margin
from report import plot_pnl_distribution, display_scenario_table, plot_volatility_distribution
from greeks import bs_greeks

from datetime import datetime, timedelta
import yfinance as yf
import random

# === Step 1: Define underlying symbols (no crypto) ===
symbols = ["AAPL", "TSLA", "SPY", "GLD", "XOM", "EURUSD=X", "JPY=X"]
portfolio = Portfolio()

greeks_summary = {"delta": 0, "gamma": 0, "vega": 0}
total_investment = 100000  # Baseline capital

# === Step 2: Fetch spot prices from 1 month ago ===
spot_data = {}
print("Fetching spot prices from 1 month ago (pre-crash)...")
for sym in symbols:
    try:
        ticker = yf.Ticker(sym)
        history = ticker.history(start=(datetime.today() - timedelta(days=35)).strftime("%Y-%m-%d"),
                                 end=(datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d"))
        if not history.empty:
            price = history["Close"].iloc[-1]
            spot_data[sym] = float(price)
        else:
            print(f"⚠️ No data for {sym} 1 month ago.")
    except Exception as e:
        print(f"⚠️ Failed to fetch {sym}: {e}")

print("1-Month-Ago Spot Prices:", spot_data)

# === Step 3: Generate exotic-rich portfolio ===
for _ in range(20):
    symbol = random.choice(list(spot_data.keys()))
    S = spot_data[symbol]

    option_type = random.choice(["call", "put"])
    quantity = random.choice([10, 20, -10, -20])
    strike = round(random.uniform(0.95, 1.05) * S, 2)
    expiry_days = random.choice([30, 60, 90, 180])
    expiry = (datetime.today() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
    implied_vol = round(random.uniform(0.25, 0.5), 2)

    # Exotic styles
    style = random.choices(
        ["european", "asian"],
        weights=[0.6, 0.4]
    )[0]

    portfolio.add_position(OptionPosition(symbol, strike, expiry, option_type, quantity, implied_vol, spot=S, style=style))

risk_free_rate = 0.03
current_date = datetime.today()

# === Step 4: Simulate scenarios, price, and compute Greeks ===
all_scenarios = []
all_pnls = []
total_cost = 0

for pos in portfolio.get_positions():
    if pos.symbol not in spot_data:
        continue

    T = pos.time_to_maturity(current_date)
    if T <= 0:
        continue

    scenarios = generate_heston_scenarios(pos.spot, pos.implied_vol, n=10)

    base_price = price_option(
        S=pos.spot, K=pos.strike, T=T, r=risk_free_rate, sigma=pos.implied_vol,
        option_type=pos.option_type, style=getattr(pos, "style", "european"),
        n_paths=5000, n_steps=30
    )

    total_cost += base_price * abs(pos.quantity)

    greeks = bs_greeks(pos.spot, pos.strike, T, risk_free_rate, pos.implied_vol, pos.option_type)
    greeks_summary["delta"] += greeks["delta"] * pos.quantity
    greeks_summary["gamma"] += greeks["gamma"] * pos.quantity
    greeks_summary["vega"] += greeks["vega"] * pos.quantity

    for s in scenarios:
        stressed_price = price_option(
            S=s['spot'], K=pos.strike, T=T, r=risk_free_rate, sigma=s['vol'],
            option_type=pos.option_type, style=getattr(pos, "style", "european"),
            n_paths=5000, n_steps=30
        )
        pnl = (stressed_price - base_price) * pos.quantity * (-1 if pos.option_type == "put" else 1)
        scenario_record = s.copy()
        scenario_record.update({
            "symbol": pos.symbol,
            "strike": pos.strike,
            "type": pos.option_type,
            "qty": pos.quantity,
            "vol": pos.implied_vol,
            "expiry": pos.expiry.strftime("%Y-%m-%d"),
            "delta": greeks["delta"],
            "gamma": greeks["gamma"],
            "vega": greeks["vega"],
            "style": getattr(pos, "style", "european")
        })
        all_scenarios.append(scenario_record)
        all_pnls.append(pnl)

# === Step 5: Margin Estimation ===
margin = estimate_margin(all_pnls, method="worst_case")
loss_pct = (margin / total_investment) * 100

print(f"\n Estimated Margin Requirement: ${margin:.2f} ({loss_pct:.2f}% of $100K portfolio)")
print(f" Total Option Cost: ${total_cost:.2f} ({(total_cost / total_investment) * 100:.2f}% of portfolio value)")

# === Step 6: Greeks Summary ===
print("\nPortfolio Greeks Summary:")
for g, val in greeks_summary.items():
    print(f"  {g.capitalize()}: {round(val, 4)}")

# === Step 7: Scenario Table + P&L Distribution ===
df = display_scenario_table(all_scenarios, all_pnls)
plot_pnl_distribution(all_pnls)
plot_volatility_distribution(all_scenarios)

