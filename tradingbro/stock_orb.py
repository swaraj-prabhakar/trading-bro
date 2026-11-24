"""Stock entry method: 30-minute Opening Range Breakout with relative volume (ORB-30 + RVOL).

A classic intraday stock method (Toby Crabel's opening range breakout, filtered by relative
volume as popularised by day-trading desks):
  * opening range = high/low of 09:15-09:45
  * SETUP when the scan bar closes above the opening-range high, today's volume so far is at
    least RVOL_MIN x the average volume by the same time over the previous RVOL_DAYS sessions,
    and the market trend is BULLISH (optional: the stock's previous close above its 20-day EMA)
  * ENTRY (default "breakout"): buy at the scan price. Optional "pullback": a LIMIT buy at the
    opening-range high (the broken level), valid until PULLBACK_UNTIL; no fill = no trade.
  * stop = opening-range low, target = 2 x the risk, square-off 15:15

1-year Upstox study (50 stocks, decision at the 10:05 bar, after ~0.11% costs per trade),
net return per trade / profit factor:
                                       older 165 sessions    latest 60 sessions
  original 5-strategy ensemble          -0.18% / 0.60         -0.02% / 0.94
  ORB-30 + RVOL, buy at breakout        -0.01% / 0.98         +0.32% / 1.93
  + pullback entry + daily EMA20        +0.15% / 1.44         +0.44% / 2.12   (opt-in)
The two refinements cut the trades to about one every three sessions, and in a 30-day replay of a
strong market (Oct-Nov 2026) they lowered profit, so they are off by default.
"""
import numpy as np
import pandas as pd

from .config import StrategyParams
from .engine import Signal, walk
from .indicators import ema

OR_END = "09:45"
RVOL_MIN = 1.5
RVOL_DAYS = 10
PULLBACK_UNTIL = "11:30"
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


def daily_trend(daily: pd.DataFrame) -> pd.Series:
    """date -> +1 / -1: the PREVIOUS session's close vs its 20-day EMA (known before the open)."""
    if daily is None or not len(daily):
        return pd.Series(dtype=float)
    c = daily["close"].copy()
    c.index = pd.Index(pd.DatetimeIndex(c.index).date)
    c = c[~c.index.duplicated(keep="last")]
    return np.sign(c - ema(c, 20)).shift(1)


def _setup(row):
    price, orh, rv = float(row["close"]), row["or30h"], row["rvol"]
    return not (pd.isna(orh) or pd.isna(rv)) and price > orh and rv >= RVOL_MIN


def _levels(row, p: StrategyParams, entry: str):
    """(entry price, stop, target) for a setup bar, or None when the risk is too small."""
    price = float(row["or30h"]) if entry == "pullback" else float(row["close"])
    stop = float(row["or30l"])
    if price - stop < price * 0.001:
        return None
    return price, stop, price + p.rr * (price - stop)


def _fill(times, o, l, start, end, limit, until):
    """First bar index in [start, end] where a buy limit at `limit` fills before `until`."""
    for j in range(start, end + 1):
        if times[j] > until:
            return None, None
        if l[j] <= limit:
            return j, min(limit, o[j])
    return None, None


def signal_at(df, asof, p: StrategyParams, market_dir=None, with_outcome=False, d_trend=None, entry="breakout"):
    """Long-only signal on the last closed bar at/before `asof`. Returns a Signal, None,
    "against_trend" (market not BULLISH) or "below_ema" (stock below its 20-day EMA)."""
    day = df[df.index.date == asof.date()]
    upto = day[day.index <= asof]
    if not len(upto):
        return None
    t = upto.index[-1].strftime("%H:%M")
    if t < p.entry_start or t > p.entry_end:
        return None
    row = upto.iloc[-1]
    if not _setup(row):
        return None
    if market_dir is not None and market_dir != 1:
        return "against_trend"
    if d_trend is not None and d_trend != 1:
        return "below_ema"
    lv = _levels(row, p, entry)
    if lv is None:
        return None
    price, stop, target = lv
    sig = Signal(upto.index[-1], 1, price, stop, target, 0, ["orb30", "rvol"])
    sig.rvol = float(row["rvol"])
    if with_outcome and len(upto) < len(day):
        times = day.index.strftime("%H:%M").values
        o, h, l, c = day.open.values, day.high.values, day.low.values, day.close.values
        start = len(upto)
        if entry == "pullback":
            j, px_in = _fill(times, o, l, start, len(day) - 1, price, PULLBACK_UNTIL)
            if j is None:
                sig.outcome = dict(exit_time="-", exit=price, reason="not filled", move_pct=0.0)
                return sig
            start = j
        j, px, reason = walk(times, o, h, l, c, start, 1, price, stop, target, p.squareoff)
        sig.outcome = dict(exit_time=day.index[j].strftime("%H:%M"), exit=float(px), reason=reason,
                           move_pct=round((px - price) / price * 100, 3))
    return sig


def universe_backtest(prepared: dict, at: str, p: StrategyParams, market=None, before_date=None,
                      trends: dict = None, entry="breakout"):
    """Every past session before `before_date`: the same decision at clock time `at` on every
    stock (market BULLISH and daily EMA20 trend required when given), the same entry rule,
    stop at the opening-range low, 2R target, square-off. Returns per-trade R and returns."""
    mtr = market["trend"] if market is not None else None
    rs, rets = [], []
    for sym, df in prepared.items():
        times = df.index.strftime("%H:%M").values
        dates = df.index.date
        o, h, l, c = df.open.values, df.high.values, df.low.values, df.close.values
        tr = trends.get(sym) if trends else None
        for i in np.flatnonzero(times == at):
            if before_date is not None and dates[i] >= before_date:
                continue
            row = df.iloc[i]
            if not _setup(row):
                continue
            if mtr is not None and mtr.asof(df.index[i]) != 1:
                continue
            if tr is not None and tr.get(dates[i]) != 1:
                continue
            end = i
            while end + 1 < len(c) and dates[end + 1] == dates[i]:
                end += 1
            if end == i:
                continue
            stop = float(row["or30l"])
            if entry == "pullback":
                limit = float(row["or30h"])
                j, e = _fill(times, o, l, i + 1, end, limit, PULLBACK_UNTIL)
                if j is None:
                    continue
            else:
                j, e = i + 1, o[i + 1]
            if e - stop < e * 0.001:
                continue
            tg = e + p.rr * (e - stop)
            sl = slice(j, end + 1)
            _, px, _ = walk(times[sl], o[sl], h[sl], l[sl], c[sl], 0, 1, e, stop, tg, p.squareoff)
            rs.append((px - e) / (e - stop))
            rets.append((px - e) / e)
    return np.array(rs), np.array(rets)
