"""Offline unit tests (synthetic data, no network):  python -m pytest -q"""
import math
from datetime import date

import numpy as np
import pandas as pd
import pytest

from tradingbro import charges, indicators as ind
from tradingbro.config import StrategyParams, TZ
from tradingbro.engine import levels, signal_at, simulate, walk
from tradingbro.options_math import bs_price, next_expiry, pick_strike, years_to_expiry
from tradingbro.strategies import add_signals


def synthetic(days=6, drift=0.0004, seed=1):
    rng = np.random.default_rng(seed)
    idx = []
    for d in pd.bdate_range("2026-10-05", periods=days):
        idx += list(pd.date_range(f"{d.date()} 09:15", f"{d.date()} 15:25", freq="5min", tz=TZ))
    idx = pd.DatetimeIndex(idx)
    c = 1000 * np.exp(np.cumsum(drift + 0.002 * rng.standard_normal(len(idx))))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + 0.001 * rng.random(len(idx)))
    l = np.minimum(o, c) * (1 - 0.001 * rng.random(len(idx)))
    return pd.DataFrame(dict(open=o, high=h, low=l, close=c, volume=rng.integers(1e3, 1e5, len(idx))), index=idx)


def test_ema_matches_pandas():
    s = pd.Series(np.arange(50, dtype=float))
    assert np.allclose(ind.ema(s, 9), s.ewm(span=9, adjust=False).mean())


def test_rsi_bounds_and_direction():
    up = pd.Series(np.linspace(100, 200, 100))
    assert ind.rsi(up).iloc[-1] > 95
    r = ind.rsi(synthetic()["close"]).dropna()
    assert r.between(0, 100).all()


def test_vwap_resets_each_day():
    df = synthetic()
    v = ind.session_vwap(df)
    first_bars = df.groupby(df.index.date).head(1).index
    tp = (df.high + df.low + df.close) / 3
    assert np.allclose(v.loc[first_bars], tp.loc[first_bars])


def test_opening_range_is_nan_while_forming():
    df = synthetic()
    orh, orl = ind.opening_range(df, 15)
    t = df.index.strftime("%H:%M")
    assert orh[t < "09:30"].isna().all() and orh[t >= "09:30"].notna().all()
    assert (orh[t >= "09:30"] >= orl[t >= "09:30"]).all()


def test_supertrend_direction_values():
    _, d = ind.supertrend(synthetic())
    assert set(d.unique()) <= {1, -1}


def test_signals_have_no_lookahead():
    """Changing future bars must not change any earlier signal."""
    p = StrategyParams()
    df = synthetic()
    cut = len(df) - 40
    a = add_signals(df, p)
    df2 = df.copy()
    df2.iloc[cut:, :4] *= 1.2
    b = add_signals(df2, p)
    cols = ["votes"] + [c for c in a.columns if c.startswith("s_")]
    assert (a[cols].iloc[:cut] == b[cols].iloc[:cut]).all().all()


def test_levels_long_and_short():
    p = StrategyParams(sl_atr_mult=2, rr=2)
    assert levels(100, 1, 1, p) == (98, 104)
    assert levels(100, 1, -1, p) == (102, 96)


def test_walk_stop_wins_tie():
    t = np.array(["10:00", "10:05"])
    o = np.array([100.0, 100.0]); h = np.array([105.0, 100]); l = np.array([95.0, 100]); c = o
    j, px, reason = walk(t, o, h, l, c, 0, 1, 100, 98, 104, "15:15")
    assert reason == "stop" and px == 98


def test_walk_squareoff():
    t = np.array(["15:10", "15:15"])
    o = np.array([100.0, 101]); h = o + 0.1; l = o - 0.1
    j, px, reason = walk(t, o, h, l, o, 0, 1, 100, 90, 110, "15:15")
    assert reason == "squareoff" and px == 101


def test_simulate_one_trade_per_day_and_intraday():
    p = StrategyParams(min_votes=1)
    df = add_signals(synthetic(days=8, drift=0.001), p)
    trades = simulate(df, p)
    assert trades
    assert len({t.date for t in trades}) == len(trades)
    for t in trades:
        assert t.entry_time.date() == t.exit_time.date()
        assert t.exit_time.strftime("%H:%M") <= p.squareoff
        assert p.entry_start <= (t.entry_time - pd.Timedelta(minutes=5)).strftime("%H:%M") <= p.entry_end


def test_simulate_before_date_excludes_future():
    p = StrategyParams(min_votes=1)
    df = add_signals(synthetic(days=8, drift=0.001), p)
    cutoff = sorted(set(df.index.date))[5]
    assert all(t.date < cutoff for t in simulate(df, p, before_date=cutoff))


def test_signal_at_outcome():
    p = StrategyParams(min_votes=1)
    df = add_signals(synthetic(days=4, drift=0.001), p)
    d = sorted(set(df.index.date))[-1]
    sig = signal_at(df, pd.Timestamp(f"{d} 10:30").tz_localize(TZ), p, with_outcome=True)
    if sig:
        assert sig.stop < sig.price < sig.target
        assert sig.outcome["reason"] in {"stop", "target", "squareoff"}


def test_put_call_parity():
    S, K, T, v, r = 1000, 1010, 7 / 365, 0.2, 0.065
    ce, pe = bs_price(S, K, T, v, "CE", r), bs_price(S, K, T, v, "PE", r)
    assert math.isclose(ce - pe, S - K * math.exp(-r * T), abs_tol=1e-6)


def test_expiries_are_tuesdays():
    assert next_expiry(date(2026, 11, 20), "weekly") == date(2026, 11, 23)  # 24th is a holiday
    assert next_expiry(date(2026, 11, 17), "weekly") == date(2026, 11, 17)
    assert next_expiry(date(2026, 11, 20), "monthly") == date(2026, 11, 23)
    assert next_expiry(date(2026, 11, 25), "monthly") == date(2026, 12, 29)
    assert years_to_expiry(pd.Timestamp("2026-11-24 15:29", tz=TZ), date(2026, 11, 24)) > 0


def test_strikes():
    assert pick_strike(24987, 50, "CE") == 25000
    assert pick_strike(24987, 50, "CE", 1) == 25050
    assert pick_strike(24987, 50, "PE", 1) == 24950


@pytest.mark.parametrize("seg", ["equity", "futures", "options"])
def test_charges_positive_and_scale(seg):
    small, big = charges.round_trip(seg, 1e4, 1e4), charges.round_trip(seg, 1e6, 1e6)
    assert 0 < small < big


def test_holiday_shifts_expiry_and_expiry_day_roll():
    # 24 Nov 2026 is an NSE holiday -> expiry moves to Mon 23 Nov
    assert next_expiry(date(2026, 11, 23), "weekly") == date(2026, 11, 23)
    assert next_expiry(date(2026, 11, 23), "monthly") == date(2026, 11, 23)
    assert next_expiry(date(2026, 11, 23), "weekly", skip_today=True) == date(2026, 12, 1)
    assert next_expiry(date(2026, 11, 23), "monthly", skip_today=True) == date(2026, 12, 29)
    assert next_expiry(date(2026, 11, 25), "weekly") == date(2026, 12, 1)


def test_review_evaluate_target_and_stop():
    from tradingbro.review import evaluate
    idx = pd.date_range("2026-11-23 10:05", periods=4, freq="1min", tz=TZ)
    bars = pd.DataFrame(dict(open=[100, 100.5, 101, 101.5], high=[100.6, 101, 102.5, 102],
                             low=[99.8, 100.2, 100.8, 101], close=[100.5, 101, 102, 101.8]), index=idx)
    base = dict(kind="stocks", symbol="X", signal_ts=pd.Timestamp("2026-11-23 10:00", tz=TZ), votes="4/5",
                qty=10, charges=5.0, direction=1, entry=100.0, stop=99.0, target=102.0)
    r = evaluate(dict(base), bars, "1m", True)
    assert r["outcome"] == "target" and r["exit"] == 102.0 and r["pnl"] == 15.0 and r["r"] == 2.0
    r = evaluate(dict(base, direction=-1, stop=101.0, target=98.0), bars, "1m", True)
    assert r["outcome"] == "stop" and r["exit"] == 101.0 and r["pnl"] == -15.0


def test_every_instrument_has_upstox_links():
    from tradingbro.universe import load_instruments
    s, i = load_instruments()
    for inst in s + i:
        assert inst.upstox.startswith("https://upstox.com/"), inst.symbol
        assert inst.upstox_oc.startswith("https://upstox.com/option-chain/"), inst.symbol


def test_review_not_filled_and_fill_then_walk():
    from tradingbro.review import evaluate
    idx = pd.date_range("2026-11-23 10:05", periods=3, freq="1min", tz=TZ)
    base = dict(kind="stocks", symbol="X", signal_ts=pd.Timestamp("2026-11-23 10:00", tz=TZ), votes="4/5",
                qty=10, charges=0.0, direction=1, entry=100.0, stop=99.0, target=102.0)
    gap_up = pd.DataFrame(dict(open=[101, 101.5, 102], high=[101.6, 102, 103], low=[100.5, 101, 101.5],
                               close=[101.5, 102, 102.5]), index=idx)
    r = evaluate(dict(base), gap_up, "1m", True)
    assert r["outcome"] == "not filled" and r["verdict"].startswith("NOT FILLED")
    dip = pd.DataFrame(dict(open=[100.5, 100.2, 101], high=[100.6, 101, 102.4], low=[100.3, 99.9, 100.8],
                            close=[100.4, 100.9, 102.2]), index=idx)
    r = evaluate(dict(base), dip, "1m", True)
    assert r["fill_time"] == idx[1] and r["outcome"] == "target" and r["verdict"].startswith("YES")


def test_market_trend_filter_blocks_counter_trend_trades():
    from tradingbro.market import trend_series
    p = StrategyParams(min_votes=1)
    up = add_signals(synthetic(days=8, drift=0.001, seed=3), p)
    mkt = trend_series(up, {"A": up, "B": up}, p)
    assert set(np.unique(mkt.trend)) <= {-1, 0, 1}
    forced_bear = mkt.assign(trend=-1)
    assert all(t.direction == -1 for t in simulate(up, p, allow_short=True, market=forced_bear))
    assert simulate(up, p, allow_short=False, market=forced_bear) == []
    d = sorted(set(up.index.date))[-1]
    for hhmm in ("10:00", "10:30", "11:00", "12:00"):
        sig = signal_at(up, pd.Timestamp(f"{d} {hhmm}").tz_localize(TZ), p, market_dir=-1)
        assert sig is None or sig == "against_trend" or sig.direction == -1
