"""Intraday trade simulation (backtest), live/replay signals and statistics.

Rules (identical for backtest and live, so the backtest measures what you trade):
  * signal = ensemble votes >= min_votes (long) or <= -min_votes (short), checked on
    each closed 5-minute bar inside [entry_start, entry_end]; first signal of the day wins
  * entry at the next bar's open (backtest) / current price (live)
  * stop  = entry -/+ sl_atr_mult x ATR,  target = entry +/- rr x stop distance
  * exit on stop, target, or square-off time. If a single bar touches both the stop and
    the target, the stop is assumed to hit first (conservative).
"""
from dataclasses import dataclass, asdict
from typing import Optional

import numpy as np
import pandas as pd

from .config import StrategyParams


@dataclass
class Trade:
    date: object
    direction: int          # +1 long / buy CE,  -1 short / buy PE
    entry_time: pd.Timestamp
    entry: float
    stop: float
    target: float
    exit_time: pd.Timestamp
    exit: float
    reason: str             # target | stop | squareoff
    votes: int

    @property
    def risk(self):
        return abs(self.entry - self.stop)

    @property
    def ret(self):
        return self.direction * (self.exit - self.entry) / self.entry

    @property
    def r_multiple(self):
        return self.direction * (self.exit - self.entry) / self.risk if self.risk else 0.0

    def to_dict(self):
        d = asdict(self)
        d.update(ret_pct=round(self.ret * 100, 3), r=round(self.r_multiple, 2))
        return d


def levels(entry, atr, direction, p: StrategyParams):
    risk = max(p.sl_atr_mult * atr, entry * 0.001)  # floor stop distance at 0.1%
    return entry - direction * risk, entry + direction * p.rr * risk


def walk(times, o, h, l, c, start, direction, entry, stop, target, squareoff):
    """Walk bars from index `start` until stop/target/square-off. Returns (i, price, reason)."""
    for j in range(start, len(c)):
        if times[j] >= squareoff:
            return j, o[j], "squareoff"
        if direction == 1:
            if l[j] <= stop:
                return j, min(stop, o[j]), "stop"          # gap through stop fills at open
            if h[j] >= target:
                return j, max(target, o[j]), "target"
        else:
            if h[j] >= stop:
                return j, max(stop, o[j]), "stop"
            if l[j] <= target:
                return j, min(target, o[j]), "target"
    j = len(c) - 1
    return j, c[j], "squareoff"


def _signal_col(df, strategy):
    return df["votes"] if strategy == "ensemble" else df["s_" + strategy]


def align_market(df, market):
    """Market trend (+1/-1/0) for every bar of df (last known value at or before the bar)."""
    if market is None:
        return None
    return market["trend"].reindex(df.index, method="ffill").fillna(0).astype(int).values


def simulate(df: pd.DataFrame, p: StrategyParams, allow_short=False, strategy="ensemble",
             before_date=None, market=None):
    """Backtest one symbol. `df` must already contain signals (strategies.add_signals).
    With `market` (market.trend_series), a trade is only taken when its direction matches
    the market trend on the signal bar."""
    sig = _signal_col(df, strategy).values
    mk = align_market(df, market)
    thresh = p.min_votes if strategy == "ensemble" else 1
    times_all = df.index.strftime("%H:%M").values
    trades = []
    dates = pd.Index(df.index.date)
    uniq = dates.unique()
    for day in uniq[1:]:                       # first day only warms up CPR
        if before_date is not None and day >= before_date:
            break
        idx = np.flatnonzero(dates == day)
        times = times_all[idx]
        o, h, l, c = (df[k].values[idx] for k in ("open", "high", "low", "close"))
        a, s = df["atr"].values[idx], sig[idx]
        m = mk[idx] if mk is not None else None
        for i in range(len(idx) - 1):
            if times[i] < p.entry_start or times[i] > p.entry_end:
                continue
            direction = 1 if s[i] >= thresh else (-1 if (allow_short and s[i] <= -thresh) else 0)
            if direction == 0 or (m is not None and m[i] != direction):
                continue
            entry = o[i + 1]
            stop, target = levels(entry, a[i], direction, p)
            j, px, reason = walk(times, o, h, l, c, i + 1, direction, entry, stop, target, p.squareoff)
            trades.append(Trade(day, direction, df.index[idx[i + 1]], float(entry), float(stop),
                                float(target), df.index[idx[j]], float(px), reason, int(s[i])))
            break
    return trades


def stats(trades):
    if not trades:
        return dict(n=0, win_rate=0.0, avg_r=0.0, avg_ret_pct=0.0, profit_factor=0.0, total_r=0.0)
    r = np.array([t.r_multiple for t in trades])
    ret = np.array([t.ret for t in trades])
    gains, losses = r[r > 0].sum(), -r[r < 0].sum()
    return dict(
        n=len(trades),
        win_rate=float((r > 0).mean()),
        avg_r=float(r.mean()),
        avg_ret_pct=float(ret.mean() * 100),
        profit_factor=float(gains / losses) if losses > 0 else float("inf"),
        total_r=float(r.sum()),
    )


@dataclass
class Signal:
    ts: pd.Timestamp
    direction: int
    price: float
    stop: float
    target: float
    votes: int
    agreeing: list
    outcome: Optional[dict] = None      # filled in replay mode (what actually happened)


def signal_at(df: pd.DataFrame, asof: pd.Timestamp, p: StrategyParams, allow_short=False,
              with_outcome=False, market_dir=None):
    """Signal on the last closed bar at/before `asof` on asof's date (or None).
    With `market_dir` (+1/-1/0) only a signal in the market's direction is returned;
    a counter-trend signal returns the string "against_trend"."""
    day_mask = df.index.date == asof.date()
    day = df[day_mask]
    upto = day[day.index <= asof]
    if len(upto) == 0:
        return None
    bar = upto.iloc[-1]
    t = upto.index[-1].strftime("%H:%M")
    if t < p.entry_start or t > p.entry_end:          # same entry window as the backtest
        return None
    v = int(bar["votes"])
    direction = 1 if v >= p.min_votes else (-1 if (allow_short and v <= -p.min_votes) else 0)
    if direction == 0:
        return None
    if market_dir is not None and market_dir != direction:
        return "against_trend"
    from .strategies import STRATEGIES
    agreeing = [n for n in STRATEGIES if int(bar["s_" + n]) == direction]
    price = float(bar["close"])
    stop, target = levels(price, float(bar["atr"]), direction, p)
    sig = Signal(upto.index[-1], direction, price, float(stop), float(target), v, agreeing)
    if with_outcome:
        start = len(upto)
        if start < len(day):
            times = day.index.strftime("%H:%M").values
            j, px, reason = walk(times, day.open.values, day.high.values, day.low.values,
                                 day.close.values, start, direction, price, stop, target, p.squareoff)
            sig.outcome = dict(exit_time=day.index[j].strftime("%H:%M"), exit=float(px), reason=reason,
                               move_pct=round(direction * (px - price) / price * 100, 3))
    return sig
