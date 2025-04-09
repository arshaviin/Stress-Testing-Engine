# scenarios.py

import numpy as np
import random

def generate_heston_vol_path(v0, kappa, theta, xi, dt, n):
    vols = [v0]
    for _ in range(n - 1):
        v_prev = vols[-1]
        dv = kappa * (theta - v_prev) * dt + xi * np.sqrt(max(v_prev, 0)) * np.random.normal()
        v_new = max(v_prev + dv, 0.01)
        vols.append(v_new)
    return vols

def generate_heston_scenarios(base_spot, base_vol, n=10):
    """
    Generates stress scenarios using Heston stochastic volatility model.

    Parameters:
        base_spot (float): Starting spot price
        base_vol (float): Starting implied vol (as decimal, e.g. 0.25)
        n (int): Number of scenarios

    Returns:
        List of dicts with spot, vol, and shocks
    """
    dt = 1 / 252  # one day step (not used for multi-step simulation here)
    kappa = 2.0
    theta = base_vol
    xi = 0.2

    vol_path = generate_heston_vol_path(base_vol, kappa, theta, xi, dt, n)
    scenarios = []

    for i in range(n):
        spot_shock = random.uniform(-0.2, 0.2)
        spot = round(base_spot * (1 + spot_shock), 2)
        vol = round(vol_path[i], 4)
        scenarios.append({
            "spot": spot,
            "vol": vol,
            "spot_shock": spot_shock,
            "vol_shock": round(vol - base_vol, 4)
        })

    return scenarios
