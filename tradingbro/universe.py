"""NIFTY 50 universe, lot sizes and strike steps (loaded from data/instruments.json)."""
import json
from dataclasses import dataclass
from typing import Optional

from .config import DATA_DIR


@dataclass
class Instrument:
    symbol: str
    yahoo: str
    lot: int
    is_index: bool = False
    strike_step: Optional[float] = None
    expiry: str = "monthly"       # "weekly" | "monthly"
    margin_pct: float = 0.18      # approx SPAN+exposure margin as % of contract value
    upstox: str = ""              # Upstox stock / index page
    upstox_oc: str = ""           # Upstox option-chain page


def load_instruments():
    raw = json.loads((DATA_DIR / "instruments.json").read_text())
    stocks = [
        Instrument(
            symbol=s["symbol"],
            yahoo=s.get("yahoo", s["symbol"] + ".NS"),
            lot=int(s["lot"]),
            strike_step=s.get("strike_step"),
            margin_pct=s.get("margin_pct", 0.18),
            upstox=s.get("upstox", ""),
            upstox_oc=s.get("upstox_oc", ""),
        )
        for s in raw["stocks"]
    ]
    indices = [
        Instrument(
            symbol=i["symbol"],
            yahoo=i["yahoo"],
            lot=int(i["lot"]),
            is_index=True,
            strike_step=i.get("strike_step"),
            expiry=i.get("expiry", "monthly"),
            margin_pct=i.get("margin_pct", 0.11),
            upstox=i.get("upstox", ""),
            upstox_oc=i.get("upstox_oc", ""),
        )
        for i in raw["indices"]
    ]
    return stocks, indices


def estimate_strike_step(price: float) -> float:
    """Rough NSE stock-option strike interval. Real intervals are set per stock -
    always confirm the strike exists in the live option chain."""
    for limit, step in ((100, 1), (250, 2.5), (500, 5), (1000, 10), (2500, 20), (5000, 50), (10000, 100)):
        if price < limit:
            return step
    return 250


def filter_symbols(instruments, symbols):
    if not symbols:
        return instruments
    wanted = {s.strip().upper() for s in symbols}
    return [i for i in instruments if i.symbol.upper() in wanted]
