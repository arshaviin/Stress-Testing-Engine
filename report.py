# report.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_pnl_distribution(pnl_list, capital_base=100000, margin_threshold=None, save_path=None):
    """
    Plot histogram of P&L outcomes normalized to capital base.
    """
    normalized_pnl = [p / capital_base * 100 for p in pnl_list]  # % of capital

    plt.figure(figsize=(10, 5))
    sns.histplot(normalized_pnl, kde=True, bins=25, color="steelblue")
    plt.axvline(x=0, linestyle="--", color="black", linewidth=1)

    if margin_threshold is not None:
        threshold_pct = margin_threshold / capital_base * 100
        plt.axvline(x=threshold_pct, color="red", linestyle="--", label=f"Margin Trigger ({threshold_pct:.1f}%)")
        plt.legend()

    plt.title("Normalized P&L Distribution Under Stress Scenarios")
    plt.xlabel("P&L (% of Capital)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

def plot_volatility_distribution(scenarios, save_path=None):
    """
    Plot histogram of scenario volatilities.
    """
    vol_values = [s['vol'] for s in scenarios if 'vol' in s]

    plt.figure(figsize=(10, 4))
    sns.histplot(vol_values, bins=20, kde=True, color="orange")
    plt.title("Distribution of Implied Volatility Across Scenarios")
    plt.xlabel("Implied Volatility")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

def display_scenario_table(scenarios, pnl_list, capital_base=100000, top_n=10):
    """
    Display sorted table of scenarios with normalized P&L and risk summary.
    """
    df = pd.DataFrame(scenarios)
    df['PnL ($)'] = pnl_list
    df['PnL (%)'] = df['PnL ($)'] / capital_base * 100

    df_sorted = df.sort_values(by='PnL ($)').reset_index(drop=True)

    print("\n Worst-Case Scenarios:")
    print(df_sorted.head(top_n))

    # Summary stats
    pnl_array = np.array(pnl_list)
    mean = np.mean(pnl_array)
    var_95 = np.percentile(pnl_array, 5)
    es_95 = pnl_array[pnl_array <= var_95].mean()

    print("\n Risk Summary:")
    print(f"  Mean P&L:     ${mean:,.2f}")
    print(f"  95% VaR:      ${var_95:,.2f}")
    print(f"  95% ES:       ${es_95:,.2f}")
    print(f"  Capital Base: ${capital_base:,.2f}")

    return df_sorted
