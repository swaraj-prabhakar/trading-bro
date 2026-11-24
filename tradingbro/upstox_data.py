"""Market data from the Upstox V3 candle API (used when TRADINGBRO_SOURCE=upstox).

Returns the same {yahoo_ticker: DataFrame} shape as data.fetch(), so the scanners,
backtests and reviews run unchanged. Instruments are still identified by their Yahoo
ticker inside the code; this module translates them to Upstox instrument keys:
stocks -> NSE_EQ|<ISIN>, indices -> NSE_INDEX|<name>.

    past days : /v3/historical-candle/{key}/{unit}/{n}/{to}/{from}   (<= 1 month per call for 1-15 min)
    today     : /v3/historical-candle/intraday/{key}/{unit}/{n}

The candle endpoints currently answer without a token. If UPSTOX_ANALYTICS_TOKEN is set
(the free 1-year read-only token from the Upstox developer console), or a daily login
token from `python -m tradingbro.upstox login` is still valid, it is sent as well, so the
data keeps flowing if Upstox starts requiring authentication.
"""
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import pandas as pd

from .config import DATA_DIR, ROOT

BASE = "https://api.upstox.com/v3/historical-candle"
USER_AGENT = "TradingBro/1.0 (personal Upstox API app)"
IST = timezone(timedelta(hours=5, minutes=30))
INDEX_KEYS = {"^NSEI": "NSE_INDEX|Nifty 50", "^NSEBANK": "NSE_INDEX|Nifty Bank", "^INDIAVIX": "NSE_INDEX|India VIX"}
CHUNK_DAYS = {"minutes": 27, "hours": 88, "days": 3650}   # Upstox max range per request is 1 calendar month for
                                                          # minutes (Feb 27 -> Mar 28 is rejected), 1 quarter for hours
MAX_PER_SEC = 8                                           # well under Upstox's 50/s, 500/min limits


@lru_cache(maxsize=1)
def instrument_keys() -> dict:
    """yahoo ticker -> Upstox instrument key, from data/instruments.json."""
    raw = json.loads((DATA_DIR / "instruments.json").read_text())
    keys = dict(INDEX_KEYS)
    for s in raw["stocks"]:
        if s.get("isin"):
            keys[s.get("yahoo", s["symbol"] + ".NS")] = f"NSE_EQ|{s['isin']}"
    return keys


def parse_interval(interval: str):
    """'5m' -> ('minutes', 5), '1h' -> ('hours', 1), '1d' -> ('days', 1)."""
    n, u = int(interval[:-1]), interval[-1]
    return {"m": "minutes", "h": "hours", "d": "days"}[u], n


def parse_period(period: str) -> int:
    n, u = int(period[:-1]), period[-1]
    return n * {"d": 1, "y": 365}[u]


def _token():
    t = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if t:
        return t
    f = ROOT / ".upstox_token.json"
    if f.exists():
        try:
            d = json.loads(f.read_text())
            if datetime.fromisoformat(d["expires"]) > datetime.now(IST):
                return d["access_token"]
        except (ValueError, KeyError):
            pass
    return None


class _Throttle:
    def __init__(self, per_sec):
        self.gap, self.next, self.lock = 1.0 / per_sec, 0.0, threading.Lock()

    def wait(self):
        with self.lock:
            now = time.monotonic()
            t = max(now, self.next)
            self.next = t + self.gap
        time.sleep(max(0.0, t - now))


_throttle = _Throttle(MAX_PER_SEC)
_auth = {"use": True}   # dropped for the rest of the run if Upstox rejects the token


def _get(url):
    for attempt in range(4):
        _throttle.wait()
        headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
        tok = _token() if _auth["use"] else None
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 401 and tok:
                _auth["use"] = False           # bad/expired token: candles are open, retry without it
                continue
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Upstox request kept failing: {url}")


def candles_to_df(candles) -> pd.DataFrame:
    """Upstox candle rows [ts, o, h, l, c, volume, oi] -> OHLCV frame indexed by IST time."""
    if not candles:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = pd.DataFrame(candles).iloc[:, :6]
    df.columns = ["ts", "open", "high", "low", "close", "volume"]
    df.index = pd.to_datetime(df.pop("ts"), utc=True).dt.tz_convert("Asia/Kolkata")
    df.index.name = None
    return df.astype(float).sort_index()


def fetch_one(key: str, interval: str, period: str, today: date = None) -> pd.DataFrame:
    """Intraday periods mean trading sessions, like Yahoo ('60d' of 5m = the last ~60
    sessions), so the backtests on both sources see the same history. Daily periods
    are calendar time ('1y')."""
    unit, n = parse_interval(interval)
    today = today or datetime.now(IST).date()
    span = parse_period(period)
    sessions = span if unit != "days" else None
    start = today - timedelta(days=int(span * 1.5) + 10 if sessions else span)
    k = urllib.parse.quote(key, safe="")
    parts = []
    to = today - timedelta(days=1)
    while to >= start:                                  # newest chunk first, walking back
        frm = max(start, to - timedelta(days=CHUNK_DAYS[unit] - 1))
        d = _get(f"{BASE}/{k}/{unit}/{n}/{to:%Y-%m-%d}/{frm:%Y-%m-%d}")
        parts.append(candles_to_df(d.get("data", {}).get("candles")))
        to = frm - timedelta(days=1)
    d = _get(f"{BASE}/intraday/{k}/{unit}/{n}")         # today's session so far (empty on holidays)
    parts.append(candles_to_df(d.get("data", {}).get("candles")))
    parts = [p for p in parts if len(p)]
    if not parts:
        return candles_to_df([])
    df = pd.concat(parts).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    if sessions:
        keep = sorted(set(df.index.date))[-sessions:]
        df = df[pd.Index(df.index.date).isin(keep)]
    return df


def fetch_raw(tickers, interval, period) -> dict:
    """{ticker: raw OHLCV frame}. Tickers without a key or whose download fails are omitted."""
    keys = instrument_keys()

    def job(t):
        if t not in keys:
            return t, None
        try:
            return t, fetch_one(keys[t], interval, period)
        except Exception as e:                          # one bad symbol must not stop the scan
            print(f"Upstox: {t} failed ({e})", flush=True)
            return t, None

    with ThreadPoolExecutor(max_workers=6) as ex:
        return {t: df for t, df in ex.map(job, tickers) if df is not None and len(df)}
