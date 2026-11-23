"""The five popular intraday strategies. Each produces +1 (bullish), -1 (bearish) or 0
per 5-minute bar. The ensemble adds them up ("votes")."""
import numpy as np
import pandas as pd

from . import indicators as ind
from .config import StrategyParams


def add_indicators(df: pd.DataFrame, p: StrategyParams) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]
    df["ema_f"] = ind.ema(c, p.ema_fast)
    df["ema_s"] = ind.ema(c, p.ema_slow)
    df["vwap"] = ind.session_vwap(df)
    df["rsi"] = ind.rsi(c, p.rsi_period)
    _, _, df["macd_h"] = ind.macd(c)
    df["atr"] = ind.atr(df, p.atr_period)
    df["st_line"], df["st_dir"] = ind.supertrend(df, p.st_period, p.st_mult)
    df["orh"], df["orl"] = ind.opening_range(df, p.or_minutes)
    df["pivot"], df["cpr_bc"], df["cpr_tc"] = ind.cpr(df)
    return df


def _sig(bull, bear):
    return pd.Series(np.where(bull, 1, np.where(bear, -1, 0)), index=bull.index)


def vwap_ema(df, p):
    """Trend-following: price above session VWAP and fast EMA above slow EMA."""
    c = df["close"]
    return _sig((c > df.vwap) & (df.ema_f > df.ema_s), (c < df.vwap) & (df.ema_f < df.ema_s))


def orb(df, p):
    """Opening Range Breakout: close beyond the first-15-minute high/low."""
    c = df["close"]
    return _sig(c > df.orh, c < df.orl)


def supertrend(df, p):
    """Supertrend(10,3) direction."""
    return _sig(df.st_dir == 1, df.st_dir == -1)


def rsi_macd(df, p):
    """Momentum: RSI above/below its band and MACD histogram on the same side."""
    return _sig((df.rsi > p.rsi_bull) & (df.macd_h > 0), (df.rsi < p.rsi_bear) & (df.macd_h < 0))


def cpr_breakout(df, p):
    """Previous-day Central Pivot Range: trading above TC is bullish, below BC bearish."""
    c = df["close"]
    return _sig(c > df.cpr_tc, c < df.cpr_bc)


STRATEGIES = {
    "vwap_ema": vwap_ema,
    "orb": orb,
    "supertrend": supertrend,
    "rsi_macd": rsi_macd,
    "cpr": cpr_breakout,
}


def add_signals(df: pd.DataFrame, p: StrategyParams) -> pd.DataFrame:
    df = add_indicators(df, p)
    for name, fn in STRATEGIES.items():
        df["s_" + name] = fn(df, p).astype(int)
    df["votes"] = df[["s_" + n for n in STRATEGIES]].sum(axis=1)
    return df
