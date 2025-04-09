# greeks.py

import numpy as np
from scipy.stats import norm

def bs_greeks(S, K, T, r, sigma, option_type="call"):
    """
    Calculate Black-Scholes Greeks for a European option.

    Parameters:
        S (float): Spot price
        K (float): Strike price
        T (float): Time to maturity (in years)
        r (float): Risk-free rate
        sigma (float): Implied volatility (annualized)
        option_type (str): 'call' or 'put'

    Returns:
        dict: delta, gamma, vega, theta, rho
    """
    # Edge handling
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "vega": 0.0,
            "theta": 0.0,
            "rho": 0.0
        }

    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    Nd1 = norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1
    Nd2 = norm.cdf(d2) if option_type == "call" else norm.cdf(d2) - 1

    delta = Nd1
    gamma = norm.pdf(d1) / (S * sigma * sqrt_T)
    vega = S * norm.pdf(d1) * sqrt_T / 100  # scaled to 1% vol change

    if option_type == "call":
        theta = (-S * norm.pdf(d1) * sigma / (2 * sqrt_T)
                 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    elif option_type == "put":
        theta = (-S * norm.pdf(d1) * sigma / (2 * sqrt_T)
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "vega": round(vega, 4),
        "theta": round(theta, 4),
        "rho": round(rho, 4)
    }
