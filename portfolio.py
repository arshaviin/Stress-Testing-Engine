from datetime import datetime
from typing import List, Dict

class OptionPosition:
    def __init__(self, symbol: str, strike: float, expiry: str, option_type: str,
                 quantity: int, implied_vol: float, spot: float, style: str = "european", risk_free_rate: float = 0.01):
        self.symbol = symbol
        self.strike = strike
        self.expiry = datetime.strptime(expiry, "%Y-%m-%d")
        self.option_type = option_type.lower()  # 'call' or 'put'
        self.quantity = quantity
        self.implied_vol = implied_vol
        self.spot = spot
        self.style = style.lower()
        self.risk_free_rate = risk_free_rate

    def time_to_maturity(self, valuation_date: datetime = None) -> float:
        if valuation_date is None:
            valuation_date = datetime.today()
        delta = (self.expiry - valuation_date).days
        return max(delta / 365.0, 0.0)

    def update_vol(self, new_vol: float):
        self.implied_vol = new_vol

    def update_quantity(self, new_qty: int):
        self.quantity = new_qty

    def __repr__(self):
        return (f"OptionPosition({self.symbol}, {self.option_type.upper()} {self.strike}, "
                f"Exp: {self.expiry.strftime('%Y-%m-%d')}, Qty: {self.quantity}, "
                f"Vol: {self.implied_vol}, Spot: {self.spot}, Style: {self.style})")


class Portfolio:
    def __init__(self):
        self.positions: List[OptionPosition] = []

    def add_position(self, position: OptionPosition):
        self.positions.append(position)

    def get_positions(self) -> List[OptionPosition]:
        return self.positions

    def summary(self) -> List[Dict]:
        return [
            {
                "symbol": p.symbol,
                "strike": p.strike,
                "expiry": p.expiry.strftime("%Y-%m-%d"),
                "type": p.option_type,
                "qty": p.quantity,
                "vol": p.implied_vol,
                "spot": p.spot
            }
            for p in self.positions
        ]

    def __repr__(self):
        return f"Portfolio({len(self.positions)} positions)"
