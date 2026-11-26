"""Real option premiums from Upstox: 1-minute candles of the exact contract (free, no login).

Used by the options scanner (actual "Buy at" premium, sizing, premium stop/target) and by the
review (fill on the real premium, P&L from the real premium at entry and exit). When a contract
or its candles cannot be found, callers fall back to the Black-Scholes estimate and mark it.
"""
import urllib.parse
from datetime import datetime

import pandas as pd

from . import upstox_data as ud
from .options_math import bs_price

_contracts = None
_bars = {}


def _book():
    global _contracts
    if _contracts is None:
        try:
            from .upstox import Contracts, instruments
            _contracts = Contracts(instruments())
        except Exception as e:                           # no instruments file: everything falls back to estimates
            print(f"Upstox instruments file unavailable ({e}); option premiums will be estimates", flush=True)
            _contracts = False
    return _contracts


def contract_key(symbol, kind, strike, expiry):
    """Upstox instrument key of e.g. ('HDFCLIFE', 'CE', 610, '2026-12-29'), or None."""
    c = _book()
    if not c:
        return None
    rec, exact = c.option(symbol, str(expiry), kind, float(strike))
    return rec["instrument_key"] if rec is not None and exact else None


def day_bars(key, day):
    """The contract's 1-minute candles for `day` (None if unavailable)."""
    if not key:
        return None
    if (key, day) not in _bars:
        k = urllib.parse.quote(key, safe="")
        if day >= datetime.now(ud.IST).date():
            url = f"{ud.BASE}/intraday/{k}/minutes/1"
        else:
            url = f"{ud.BASE}/{k}/minutes/1/{day:%Y-%m-%d}/{day:%Y-%m-%d}"
        try:
            df = ud.candles_to_df(ud._get(url).get("data", {}).get("candles"))
            df = df[df.index.date == day]
        except Exception as e:
            print(f"Upstox option candles for {key} failed ({e})", flush=True)
            df = None
        _bars[(key, day)] = df if df is not None and len(df) else None
    return _bars[(key, day)]


def price_at(bars, ts):
    """Last traded premium known at `ts`: close of the last 1-minute candle that ended by then."""
    if bars is None:
        return None
    b = bars[bars.index + pd.Timedelta(minutes=1) <= ts]
    return float(b["close"].iloc[-1]) if len(b) else None


def first_fill(bars, start, limit, deadline):
    """Buy limit at `limit` from `start`: (fill time, fill price) of the first candle that traded at or
    below it before `deadline` (HH:MM), else None. The fill price is the better of the limit and the open."""
    if bars is None:
        return None
    for ts, row in bars[bars.index >= start].iterrows():
        if ts.strftime("%H:%M") > deadline:
            return None
        if row["low"] <= limit:
            return ts, float(min(limit, row["open"]))
    return None


def implied_vol(price, S, K, T, kind):
    """Volatility that makes Black-Scholes match the traded premium (None if it cannot)."""
    intrinsic = max(0.0, S - K) if kind == "CE" else max(0.0, K - S)
    if T <= 0 or price <= intrinsic + 0.01:
        return None
    lo, hi = 0.01, 3.0
    if bs_price(S, K, T, hi, kind) < price:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if bs_price(S, K, T, mid, kind) > price:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2
