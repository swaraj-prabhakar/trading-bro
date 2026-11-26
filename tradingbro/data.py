"""Market data with a small on-disk cache.

All bars come from the Upstox candle API (tradingbro/upstox_data.py), the broker's own feed.
Instruments are still keyed by their old ticker names (e.g. "SBIN.NS", "^NSEI") internally.
"""
import os
import time
import warnings
from datetime import datetime

import pandas as pd

from .config import CACHE_DIR, TZ, MARKET_OPEN, MARKET_CLOSE

warnings.filterwarnings("ignore", category=FutureWarning)


def now_ist() -> pd.Timestamp:
    return pd.Timestamp.now(tz=TZ)


def market_is_open(ts: pd.Timestamp = None) -> bool:
    ts = ts or now_ist()
    if ts.weekday() >= 5:
        return False
    t = ts.strftime("%H:%M")
    return MARKET_OPEN <= t <= MARKET_CLOSE


def _clean(df: pd.DataFrame, intraday: bool) -> pd.DataFrame:
    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    df = df[df["close"] > 0]
    idx = pd.DatetimeIndex(df.index)
    idx = idx.tz_localize("UTC").tz_convert(TZ) if idx.tz is None else idx.tz_convert(TZ)
    df.index = idx
    if intraday:
        t = df.index.strftime("%H:%M")
        df = df[(t >= MARKET_OPEN) & (t < MARKET_CLOSE)]
    df["volume"] = df["volume"].fillna(0)
    return df[~df.index.duplicated(keep="last")].sort_index()


STANDARD_PERIODS = {"60d", "1y", "7d"}


def _cache_path(ticker, interval, period=None):
    safe = ticker.replace("^", "IDX_").replace("&", "and")
    tag = "" if period in (None, *STANDARD_PERIODS) else f"_{period}"
    return CACHE_DIR / f"{interval}{tag}_{safe}.pkl"


def fetch(tickers, interval="5m", period="60d", refresh=False) -> dict:
    """Return {ticker: DataFrame}. Tickers that fail to download are omitted."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ttl = 240 if market_is_open() else 6 * 3600
    ttl = int(os.environ.get("TRADINGBRO_CACHE_TTL", ttl))   # the personal scan reuses the main scan's bars
    out, missing = {}, []
    for t in tickers:
        p = _cache_path(t, interval, period)
        if not refresh and p.exists() and time.time() - p.stat().st_mtime < ttl:
            out[t] = pd.read_pickle(p)
        else:
            missing.append(t)

    from .upstox_data import fetch_raw
    for t, df in fetch_raw(missing, interval, period).items():
        df = _clean(df, intraday=interval.endswith("m"))
        if len(df):
            df.to_pickle(_cache_path(t, interval, period))
            out[t] = df
    return out


def fetch_universe(instruments, refresh=False):
    """5-minute bars (60d) + daily bars (1y) for a list of Instrument objects."""
    tickers = [i.yahoo for i in instruments]
    # TRADINGBRO_HISTORY_SESSIONS = how many past sessions of 5-minute bars the per-symbol backtests see.
    hist = os.environ.get("TRADINGBRO_HISTORY_SESSIONS", "60")
    intraday = fetch(tickers, "5m", f"{hist}d", refresh)
    daily = fetch(tickers, "1d", "1y", refresh)
    dropped = [i.symbol for i in instruments if i.yahoo not in intraday]
    return intraday, daily, dropped


def fetch_vix(refresh=False):
    d = fetch(["^INDIAVIX"], "1d", "1y", refresh)
    return d.get("^INDIAVIX")


def parse_date(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()
