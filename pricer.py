# pricer.py

import numpy as np
from scipy.stats import norm

def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    """
    Vanilla Black-Scholes pricing for European options.

    Parameters:
        S (float): Spot price
        K (float): Strike price
        T (float): Time to maturity (in years)
        r (float): Risk-free interest rate
        sigma (float): Implied volatility
        option_type (str): 'call' or 'put'

    Returns:
        float: Option price
    """
    if T <= 0:
        return max(S - K, 0) if option_type == "call" else max(K - S, 0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")


def price_asian_monte_carlo(S, K, T, r, sigma, option_type="call", n_paths=10000, n_steps=50, seed=None):
    """
    Monte Carlo pricing for Asian options using arithmetic average of spot prices.

    Parameters:
        S (float): Spot price
        K (float): Strike price
        T (float): Time to maturity (years)
        r (float): Risk-free rate
        sigma (float): Volatility
        option_type (str): 'call' or 'put'
        n_paths (int): Number of Monte Carlo paths
        n_steps (int): Number of timesteps per path
        seed (int): Optional random seed for reproducibility

    Returns:
        float: Estimated option price
    """
    if seed is not None:
        np.random.seed(seed)

    dt = T / n_steps
    discount = np.exp(-r * T)

    payoffs = []
    for _ in range(n_paths):
        path = [S]
        for _ in range(n_steps):
            z = np.random.normal()
            S_next = path[-1] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
            path.append(S_next)
        avg_price = np.mean(path)
        payoff = max(avg_price - K, 0) if option_type == "call" else max(K - avg_price, 0)
        payoffs.append(payoff)

    return discount * np.mean(payoffs)


def price_option(S, K, T, r, sigma, option_type="call", style="european", exotic_type=None, **kwargs):
    """
    General pricing dispatcher for vanilla and exotic options.

    Parameters:
        S, K, T, r, sigma, option_type: Standard option inputs
        style (str): 'european', 'asian', 'barrier', etc.
        exotic_type (str): Optional identifier for exotic structure
        kwargs: Extra arguments (n_paths, barrier level, etc.)

    Returns:
        float: Option price
    """
    style = style.lower()

    if style == "european":
        return black_scholes_price(S, K, T, r, sigma, option_type)

    elif style == "asian":
        return price_asian_monte_carlo(S, K, T, r, sigma, option_type,
                                       n_paths=kwargs.get("n_paths", 10000),
                                       n_steps=kwargs.get("n_steps", 50),
                                       seed=kwargs.get("seed", None))

    # elif style == "digital":
    #     payoffs = []
    #     for _ in range(n_paths):
    #         Z = np.random.normal()
    #         ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    #         if option_type == "call":
    #             payoffs.append(1.0 if ST > K else 0.0)
    #         else:
    #             payoffs.append(1.0 if ST < K else 0.0)
    #     return np.exp(-r * T) * np.mean(payoffs)

    # elif style == "barrier":
    #     barrier = S * 0.9 if barrier_level is None else barrier_level  # Default barrier
    #     payoffs = []
    #     for _ in range(n_paths):
    #         breached = False
    #         S_path = S
    #         for _ in range(n_steps):
    #             Z = np.random.normal()
    #             S_path *= np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z)
    #             if (option_type == "call" and S_path >= barrier_level) or \
    #                (option_type == "put" and S_path <= barrier_level):
    #                 breached = True
    #         if breached:
    #             if option_type == "call":
    #                 payoffs.append(max(S_path - K, 0))
    #             else:
    #                 payoffs.append(max(K - S_path, 0))
    #         else:
    #             payoffs.append(0)
    #     return np.exp(-r * T) * np.mean(payoffs)

    else:
        raise ValueError(f"Unsupported option style: '{style}'")
