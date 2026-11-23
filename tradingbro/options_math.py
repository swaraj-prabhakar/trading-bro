"""Black-Scholes pricing, NSE expiry calendar and strike selection.

Historical option prices are not available from free sources, so premiums are
*modelled* from the underlying's price path with Black-Scholes. Real premiums differ
(IV smile, bid-ask spreads, IV crush) - always check the live option chain.
"""
import math
from datetime import date, timedelta

import pandas as pd

from .config import NSE_HOLIDAYS, RISK_FREE_RATE, TZ

TUESDAY = 1


def _ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def bs_price(S, K, T, sigma, kind, r=RISK_FREE_RATE):
    """kind: 'CE' or 'PE'. T in years."""
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K) if kind == "CE" else max(0.0, K - S)
    sq = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / sq
    d2 = d1 - sq
    if kind == "CE":
        return S * _ncdf(d1) - K * math.exp(-r * T) * _ncdf(d2)
    return K * math.exp(-r * T) * _ncdf(-d2) - S * _ncdf(-d1)


def bs_delta(S, K, T, sigma, kind, r=RISK_FREE_RATE):
    if T <= 0 or sigma <= 0:
        return (1.0 if S > K else 0.0) if kind == "CE" else (-1.0 if S < K else 0.0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return _ncdf(d1) if kind == "CE" else _ncdf(d1) - 1


def last_tuesday(year, month):
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - timedelta(days=1)
    while d.weekday() != TUESDAY:
        d -= timedelta(days=1)
    return d


def _shift_for_holidays(e: date) -> date:
    while e.weekday() >= 5 or e.isoformat() in NSE_HOLIDAYS:
        e -= timedelta(days=1)
    return e


def _raw_expiry(d: date, kind):
    if kind == "weekly":
        return d + timedelta(days=(TUESDAY - d.weekday()) % 7)
    e = last_tuesday(d.year, d.month)
    if e < d:
        y, m = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
        e = last_tuesday(y, m)
    return e


def next_expiry(d: date, kind="monthly", skip_today=False) -> date:
    """NSE F&O expiries are on Tuesdays (since Sep 2025); an expiry on a holiday
    (config.NSE_HOLIDAYS) moves to the previous trading day. With skip_today=True an
    expiry falling on `d` itself is rolled to the following one."""
    probe = d
    while True:
        e = _shift_for_holidays(_raw_expiry(probe, kind))
        if e > d or (e == d and not skip_today):
            return e
        probe = _raw_expiry(probe, kind) + timedelta(days=1)


def years_to_expiry(ts: pd.Timestamp, expiry: date) -> float:
    exp_ts = pd.Timestamp(expiry).tz_localize(TZ) + pd.Timedelta(hours=15, minutes=30)
    secs = (exp_ts - ts).total_seconds()
    return max(secs, 1800) / (365 * 24 * 3600)


def pick_strike(S, step, kind, otm=0):
    atm = round(S / step) * step
    return atm + otm * step if kind == "CE" else atm - otm * step
