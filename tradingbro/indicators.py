"""Technical indicators. All are causal: the value at bar i only uses bars <= i."""
import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(100.0).where(dn.notna(), 50.0)


def macd(s: pd.Series, fast=12, slow=26, signal=9):
    line = ema(s, fast) - ema(s, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def session_vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP reset every session. Indices have no volume on Yahoo, so they fall back
    to an equal-weighted running average of the typical price."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    day = df.index.date
    vol = df["volume"].astype(float)
    day_vol = vol.groupby(day).transform("sum")
    vol = vol.where(day_vol > 0, 1.0)
    return (tp * vol).groupby(day).cumsum() / vol.groupby(day).cumsum()


def supertrend(df: pd.DataFrame, n=10, mult=3.0):
    """Returns (line, direction) where direction is +1 (up-trend) / -1 (down-trend)."""
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    a = atr(df, n).values
    hl2 = (h + l) / 2
    ub, lb = hl2 + mult * a, hl2 - mult * a
    fub, flb = ub.copy(), lb.copy()
    d = np.ones(len(c), dtype=int)
    for i in range(1, len(c)):
        fub[i] = ub[i] if (ub[i] < fub[i - 1] or c[i - 1] > fub[i - 1]) else fub[i - 1]
        flb[i] = lb[i] if (lb[i] > flb[i - 1] or c[i - 1] < flb[i - 1]) else flb[i - 1]
        if d[i - 1] == -1:
            d[i] = 1 if c[i] > fub[i] else -1
        else:
            d[i] = -1 if c[i] < flb[i] else 1
    line = np.where(d == 1, flb, fub)
    return pd.Series(line, index=df.index), pd.Series(d, index=df.index)


def opening_range(df: pd.DataFrame, minutes=15, open_time="09:15"):
    """High/low of the first `minutes` of each session; NaN while the range is forming."""
    t = df.index.strftime("%H:%M")
    end = (pd.Timestamp("2000-01-01 " + open_time) + pd.Timedelta(minutes=minutes)).strftime("%H:%M")
    in_or = t < end
    day = df.index.date
    orh = df["high"].where(in_or).groupby(day).transform("max")
    orl = df["low"].where(in_or).groupby(day).transform("min")
    return orh.where(~in_or), orl.where(~in_or)


def cpr(df: pd.DataFrame):
    """Central Pivot Range from the previous session: (pivot, bottom-central, top-central)."""
    day = pd.Series(df.index.date, index=df.index)
    daily = df.groupby(day.values).agg(h=("high", "max"), l=("low", "min"), c=("close", "last")).shift(1)
    piv = (daily.h + daily.l + daily.c) / 3
    bc = (daily.h + daily.l) / 2
    tc = 2 * piv - bc
    lo, hi = np.minimum(bc, tc), np.maximum(bc, tc)
    return (day.map(piv), day.map(lo), day.map(hi))


def hist_vol(daily_close: pd.Series, n=20) -> pd.Series:
    """Annualised close-to-close volatility."""
    r = np.log(daily_close).diff()
    return r.rolling(n).std() * np.sqrt(252)
