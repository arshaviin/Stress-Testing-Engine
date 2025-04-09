# margin.py

import numpy as np

def calculate_var_margin(pnl_list, confidence=0.99):
    """
    Calculate a simple Value-at-Risk (VaR) margin estimate.

    Parameters:
        pnl_list (list of float): List of P&L outcomes under stress scenarios
        confidence (float): Confidence level for VAR (e.g., 0.99)

    Returns:
        float: Estimated margin requirement
    """
    var = -np.percentile(pnl_list, (1 - confidence) * 100)
    return round(var, 2)

def calculate_worst_case_margin(pnl_list):
    """
    Estimate margin as the worst-case (most negative) P&L.

    Parameters:
        pnl_list (list of float): List of P&L outcomes under stress scenarios

    Returns:
        float: Margin based on max loss
    """
    return round(-min(pnl_list), 2)

def estimate_margin(pnl_list, method="var"):
    """
    Wrapper to switch between margin estimation methods.

    Parameters:
        pnl_list (list of float): List of P&L outcomes
        method (str): 'var' or 'worst_case'

    Returns:
        float: Estimated margin
    """
    if method == "var":
        return calculate_var_margin(pnl_list)
    elif method == "worst_case":
        return calculate_worst_case_margin(pnl_list)
    else:
        raise ValueError("Unknown method. Use 'var' or 'worst_case'.")
