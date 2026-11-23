"""Overall market trend (NIFTY 50), used to keep only trades that go WITH the market.

For every 5-minute bar the trend is scored from three independent views:
  1. Intraday index trend - the 5-strategy vote on NIFTY itself (+1 / -1 / 0)
  2. Breadth - share of NIFTY 50 stocks with a bullish vs bearish ensemble signal
     (+1 if bulls lead by more than `breadth_edge`, -1 if bears do, else 0)
  3. Daily trend - previous session's NIFTY close vs its 20-day EMA (+1 / -1)
score = sum of the three;  >= +TREND_MIN_SCORE -> BULLISH (+1),  <= -TREND_MIN_SCORE -> BEARISH (-1),
else SIDEWAYS (0). Backtest (60 sessions, NIFTY 50 + indices): a majority lean (1) beat requiring
2 of 3 agreeing - avg R +0.116 vs +0.108 for CE/PE trades and positive in both halves of the sample.
Everything is causal: the value at a bar uses only data up to that bar.
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from .config import StrategyParams
from .data import fetch_universe
from .indicators import ema
from .strategies import add_signals
from .universe import load_instruments

LABEL = {1: "BULLISH", -1: "BEARISH", 0: "SIDEWAYS"}
BREADTH_EDGE = 0.20
TREND_MIN_SCORE = 1


def trend_series(nifty: pd.DataFrame, stocks: dict, p: StrategyParams, nifty_daily: pd.DataFrame = None):
    """nifty / stocks: DataFrames that already contain signals. Returns a DataFrame indexed
    like `nifty` with columns trend, score, index_vote, breadth, daily."""
    v = nifty["votes"]
    index_vote = np.sign(v.where(v.abs() >= p.min_votes, 0)).astype(int)

    sig = []
    for df in stocks.values():
        s = df["votes"]
        sig.append(np.sign(s.where(s.abs() >= p.min_votes, 0)).reindex(nifty.index, method="ffill"))
    if sig:
        m = pd.concat(sig, axis=1)
        bulls, bears = (m > 0).sum(axis=1), (m < 0).sum(axis=1)
        breadth = (bulls - bears) / m.notna().sum(axis=1).replace(0, np.nan)
    else:
        breadth = pd.Series(0.0, index=nifty.index)
    breadth_vote = np.where(breadth > BREADTH_EDGE, 1, np.where(breadth < -BREADTH_EDGE, -1, 0))

    # daily trend from the previous session only
    if nifty_daily is not None and len(nifty_daily):
        dc = nifty_daily["close"]
        dc = dc.set_axis(pd.Index(dc.index.date))
    else:
        dc = nifty["close"].groupby(nifty.index.date).last()
    bias = np.sign(dc - ema(dc, 20)).shift(1)                 # yesterday's close vs EMA20
    daily_vote = pd.Series(nifty.index.date, index=nifty.index).map(bias).fillna(0).astype(int)

    score = index_vote + breadth_vote + daily_vote
    trend = np.where(score >= TREND_MIN_SCORE, 1, np.where(score <= -TREND_MIN_SCORE, -1, 0))
    return pd.DataFrame(dict(trend=trend, score=score, index_vote=index_vote, breadth=breadth,
                             daily=daily_vote), index=nifty.index)


@lru_cache(maxsize=4)
def _market(p_key, refresh):
    p = StrategyParams(**dict(p_key))
    stocks, indices = load_instruments()
    nifty_inst = [i for i in indices if i.symbol == "NIFTY"]
    intraday, daily, _ = fetch_universe(nifty_inst + stocks, refresh)
    nifty = add_signals(intraday[nifty_inst[0].yahoo], p)
    prepared = {i.symbol: add_signals(intraday[i.yahoo], p) for i in stocks if i.yahoo in intraday}
    return trend_series(nifty, prepared, p, daily.get(nifty_inst[0].yahoo))


def market_trend(p: StrategyParams, refresh=False) -> pd.DataFrame:
    return _market(tuple(sorted(p.to_dict().items())), refresh)


def trend_at(mkt: pd.DataFrame, ts) -> dict:
    row = mkt[mkt.index <= ts]
    if not len(row):
        return dict(trend=0, label="UNKNOWN")
    r = row.iloc[-1]
    return dict(trend=int(r.trend), label=LABEL[int(r.trend)], score=int(r.score), index_vote=int(r.index_vote),
                breadth=float(r.breadth) if pd.notna(r.breadth) else 0.0, daily=int(r.daily),
                bar=row.index[-1])


def describe(t: dict) -> str:
    if t["label"] == "UNKNOWN":
        return "Market trend: UNKNOWN (no NIFTY data at this time)"
    idx = {1: "up", -1: "down", 0: "mixed"}[t["index_vote"]]
    day = {1: "above", -1: "below", 0: "n/a"}[t["daily"]]
    return (f"Market trend: {t['label']} (score {t['score']:+d}/3 | NIFTY intraday {idx} | breadth "
            f"{t['breadth'] * 100:+.0f}% bulls-bears | prev close {day} 20-day EMA)")
