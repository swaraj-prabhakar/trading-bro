"""Stock entry method: 30-minute Opening Range Breakout with relative volume (ORB-30 + RVOL).

A classic intraday stock method (Toby Crabel's opening range breakout, filtered by relative
volume as popularised by day-trading desks):
  * opening range = high/low of 09:15-09:45
  * BUY when the scan bar closes above the opening-range high, today's volume so far is at
    least RVOL_MIN x the average volume by the same time over the previous RVOL_DAYS sessions,
    and the market trend is BULLISH
  * stop = opening-range low, target = 2 x the risk, square-off 15:15

1-year Upstox study (50 stocks, decision at the 10:05 bar, after ~0.11% costs per trade):
  older 165 sessions: -0.01% / trade, profit factor 0.98 (current ensemble: -0.18%, PF 0.60)
  latest 60 sessions: +0.32% / trade, profit factor 1.93 (current ensemble: -0.02%, PF 0.94)
It is the only tested method that beat the ensemble in both periods; on its own it is roughly
break-even over the older year, so treat it as an edge to verify, not a sure thing.
"""
import numpy as np
import pandas as pd

from .config import StrategyParams
from .engine import Signal, walk

OR_END = "09:45"
RVOL_MIN = 1.5
RVOL_DAYS = 10
METHOD = "ORB-30 + RVOL"


def add_orb_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Adds or30h / or30l (NaN while the range forms) and rvol. All causal."""
    df = df.copy()
    t = df.index.strftime("%H:%M")
    day = df.index.date
    in_or = t < OR_END
    df["or30h"] = df["high"].where(in_or).groupby(day).transform("max").where(~in_or)
    df["or30l"] = df["low"].where(in_or).groupby(day).transform("min").where(~in_or)
    cumv = df["volume"].groupby(day).cumsum()
    hist = cumv.groupby(t).transform(lambda s: s.shift(1).rolling(RVOL_DAYS, min_periods=5).mean())
    df["rvol"] = cumv / hist.replace(0, np.nan)
    return df


def _setup(row, p: StrategyParams):
    """(price, stop, target) if the bar is a long ORB-30 + RVOL setup, else None."""
    price, orh, orl, rv = float(row["close"]), row["or30h"], row["or30l"], row["rvol"]
    if pd.isna(orh) or pd.isna(rv) or not (price > orh and rv >= RVOL_MIN):
        return None
    stop = float(orl)
    if price - stop < price * 0.001:
        return None
    return price, stop, price + p.rr * (price - stop)


def signal_at(df, asof, p: StrategyParams, market_dir=None, with_outcome=False):
    """Long-only signal on the last closed bar at/before `asof`. Returns Signal, None, or
    "against_trend" when the setup exists but the market is not BULLISH."""
    day = df[df.index.date == asof.date()]
    upto = day[day.index <= asof]
    if not len(upto):
        return None
    t = upto.index[-1].strftime("%H:%M")
    if t < p.entry_start or t > p.entry_end:
        return None
    s = _setup(upto.iloc[-1], p)
    if s is None:
        return None
    if market_dir is not None and market_dir != 1:
        return "against_trend"
    price, stop, target = s
    sig = Signal(upto.index[-1], 1, price, stop, target, 0, ["orb30", "rvol"])
    sig.rvol = float(upto.iloc[-1]["rvol"])
    if with_outcome and len(upto) < len(day):
        times = day.index.strftime("%H:%M").values
        j, px, reason = walk(times, day.open.values, day.high.values, day.low.values, day.close.values,
                             len(upto), 1, price, stop, target, p.squareoff)
        sig.outcome = dict(exit_time=day.index[j].strftime("%H:%M"), exit=float(px), reason=reason,
                           move_pct=round((px - price) / price * 100, 3))
    return sig


def universe_backtest(prepared: dict, at: str, p: StrategyParams, market=None, before_date=None):
    """Every past session before `before_date`: the same decision at clock time `at` on every stock
    (market trend BULLISH required when `market` is given), entry at the next bar's open, stop at
    the opening-range low, 2R target, square-off. Returns per-trade R and return arrays."""
    mtr = market["trend"] if market is not None else None
    rs, rets = [], []
    for df in prepared.values():
        times = df.index.strftime("%H:%M").values
        dates = df.index.date
        o, h, l, c = df.open.values, df.high.values, df.low.values, df.close.values
        for i in np.flatnonzero(times == at):
            if before_date is not None and dates[i] >= before_date:
                continue
            if _setup(df.iloc[i], p) is None:
                continue
            if mtr is not None and mtr.asof(df.index[i]) != 1:
                continue
            end = i
            while end + 1 < len(c) and dates[end + 1] == dates[i]:
                end += 1
            if end == i:
                continue
            e, stop = o[i + 1], float(df["or30l"].iloc[i])
            if e - stop < e * 0.001:
                continue
            tg = e + p.rr * (e - stop)
            sl = slice(i + 1, end + 1)
            _, px, _ = walk(times[sl], o[sl], h[sl], l[sl], c[sl], 0, 1, e, stop, tg, p.squareoff)
            rs.append((px - e) / (e - stop))
            rets.append((px - e) / e)
    return np.array(rs), np.array(rets)
