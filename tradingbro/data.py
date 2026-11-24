"""Market data with a small on-disk cache.

Source is chosen by config.SOURCE: Yahoo Finance (default) or the Upstox candle API
(tradingbro/upstox_data.py). Yahoo limits 5-minute history to the last ~60 calendar
days, which is what the backtests use, and NSE quotes on Yahoo can lag by a few
minutes. Upstox serves the same periods from the broker's own feed.
"""
import time
import warnings
from datetime import datetime

import pandas as pd

from .config import CACHE_DIR, SOURCE, TZ, MARKET_OPEN, MARKET_CLOSE

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


def _cache_path(ticker, interval):
    safe = ticker.replace("^", "IDX_").replace("&", "and")
    return CACHE_DIR / f"{interval}_{safe}.pkl"


def fetch(tickers, interval="5m", period="60d", refresh=False) -> dict:
    """Return {ticker: DataFrame}. Tickers that fail to download are omitted."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ttl = 240 if market_is_open() else 6 * 3600
    out, missing = {}, []
    for t in tickers:
        p = _cache_path(t, interval)
        if not refresh and p.exists() and time.time() - p.stat().st_mtime < ttl:
            out[t] = pd.read_pickle(p)
        else:
            missing.append(t)

    if SOURCE == "upstox":
        from .upstox_data import fetch_raw
        for t, df in fetch_raw(missing, interval, period).items():
            df = _clean(df, intraday=interval.endswith("m"))
            if len(df):
                df.to_pickle(_cache_path(t, interval))
                out[t] = df
        return out

    import yfinance as yf
    for attempt in range(3):                      # cloud runners get throttled: retry the empty ones
        if not missing:
            break
        if attempt:
            time.sleep(10 * attempt)
        raw = yf.download(missing, period=period, interval=interval, group_by="ticker",
                          auto_adjust=False, progress=False, threads=True)
        got = []
        for t in missing:
            try:
                if isinstance(raw.columns, pd.MultiIndex):
                    if t not in raw.columns.get_level_values(0):
                        continue
                    df = raw[t]
                else:
                    df = raw
                df = _clean(df, intraday=interval.endswith("m"))
            except Exception:
                continue
            if len(df) == 0:
                continue
            df.to_pickle(_cache_path(t, interval))
            out[t] = df
            got.append(t)
        missing = [t for t in missing if t not in got]
    return out


def fetch_universe(instruments, refresh=False):
    """5-minute bars (60d) + daily bars (1y) for a list of Instrument objects."""
    tickers = [i.yahoo for i in instruments]
    intraday = fetch(tickers, "5m", "60d", refresh)
    daily = fetch(tickers, "1d", "1y", refresh)
    dropped = [i.symbol for i in instruments if i.yahoo not in intraday]
    return intraday, daily, dropped


def fetch_vix(refresh=False):
    d = fetch(["^INDIAVIX"], "1d", "1y", refresh)
    return d.get("^INDIAVIX")


def parse_date(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()
