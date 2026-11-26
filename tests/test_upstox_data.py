"""Offline tests for the Upstox data source (no network): python -m pytest -q"""
import os
import subprocess
import sys
from datetime import date

import pandas as pd

from tradingbro import upstox_data as ud

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_interval_and_period_parsing():
    assert ud.parse_interval("5m") == ("minutes", 5)
    assert ud.parse_interval("1d") == ("days", 1)
    assert ud.parse_period("60d") == 60 and ud.parse_period("1y") == 365


def test_instrument_keys_cover_universe():
    keys = ud.instrument_keys()
    assert keys["^NSEI"] == "NSE_INDEX|Nifty 50"
    assert keys["^INDIAVIX"] == "NSE_INDEX|India VIX"
    assert keys["RELIANCE.NS"].startswith("NSE_EQ|INE")
    from tradingbro.universe import load_instruments
    s, i = load_instruments()
    assert all(x.yahoo in keys for x in s + i)


def test_candles_to_df_ist_sorted():
    rows = [["2026-11-20T09:20:00+05:30", 101, 103, 100, 102, 500, 0],
            ["2026-11-20T09:15:00+05:30", 100, 102, 99, 101, 900, 0]]
    df = ud.candles_to_df(rows)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert str(df.index.tz) == "Asia/Kolkata" and df.index[0].strftime("%H:%M") == "09:15"
    assert df["close"].tolist() == [101.0, 102.0]
    assert len(ud.candles_to_df([])) == 0


def test_fetch_one_chunks_and_keeps_n_sessions(monkeypatch):
    calls = []

    def fake_get(url):
        calls.append(url)
        if "/intraday/" in url:
            return {"data": {"candles": [["2026-11-25T09:15:00+05:30", 1, 1, 1, 1, 1, 0]]}}
        to, frm = url.rsplit("/", 2)[-2:]
        days = pd.bdate_range(frm, to)
        return {"data": {"candles": [[f"{d:%Y-%m-%d}T09:15:00+05:30", 1, 1, 1, 1, 1, 0] for d in days]}}

    monkeypatch.setattr(ud, "_get", fake_get)
    df = ud.fetch_one("NSE_EQ|X", "5m", "60d", today=date(2026, 11, 25))
    hist = [u for u in calls if "/intraday/" not in u]
    for u in hist:                                       # every minute chunk within Upstox's 1-month cap
        to, frm = u.rsplit("/", 2)[-2:]
        assert (pd.Timestamp(to) - pd.Timestamp(frm)).days < 28   # stays inside 1 calendar month, even in Feb
    assert len(set(df.index.date)) == 60                 # 60 sessions, the backtest history
    assert df.index[-1].date() == date(2026, 11, 25)     # today's intraday bars appended


def _cfg(env, code):
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                          env=dict(os.environ, **env)).stdout.split()


def test_upstox_is_the_only_source_and_profiles_have_own_files():
    code = ("from tradingbro import config as c, daily as d; "
            "print(c.SOURCE, c.OUTPUT_DIR.name, c.RESULT_MD.name, c.PICKS_MD.name, *d.scan_argv(100000))")
    assert _cfg({"TRADINGBRO_PROFILE": ""}, code) ==         ["upstox", "output_upstox", "Result_upstox.md", "Picks_upstox.md", "--capital", "100000"]
    assert _cfg({"TRADINGBRO_PROFILE": "personal"}, code) ==         ["upstox", "output_upstox_personal", "Result_upstox_personal.md", "Picks_upstox_personal.md",
         "--capital", "50000", "--top", "2"]


def test_implied_vol_round_trip_and_price_at():
    from tradingbro.option_quotes import first_fill, implied_vol, price_at
    from tradingbro.options_math import bs_price
    px = bs_price(607.6, 610, 0.09, 0.22, "CE")
    assert abs(implied_vol(px, 607.6, 610, 0.09, "CE") - 0.22) < 1e-4
    assert implied_vol(0.0, 607.6, 610, 0.09, "CE") is None
    idx = pd.date_range("2026-11-26 10:10", periods=4, freq="1min", tz="Asia/Kolkata")
    bars = pd.DataFrame({"open": [20.8, 20.5, 20.1, 19.0], "high": [20.8, 20.55, 20.25, 19.0],
                         "low": [20.5, 20.0, 19.05, 18.6], "close": [20.7, 20.2, 19.1, 18.85]}, index=idx)
    assert price_at(bars, idx[0]) is None                       # the 10:10 candle has not closed yet at 10:10
    assert price_at(bars, idx[1]) == 20.7                        # at 10:11 the 10:10 close is known
    assert first_fill(bars, idx[0], 27.0, "13:30") == (idx[0], 20.8)   # limit above the market fills at the open
    assert first_fill(bars, idx[0], 19.5, "13:30") == (idx[2], 19.5)
    assert first_fill(bars, idx[0], 10.0, "13:30") is None


def test_monthly_pages_and_replay_note():
    from tradingbro.daily import by_month, data_note, month_title
    from tradingbro.config import monthly_md
    days = [dict(date="2026-11-25", replay=False), dict(date="2026-11-03", replay=True),
            dict(date="2026-10-31", replay=True)]
    assert list(by_month(days)) == ["2026-11", "2026-10"]
    assert [d["date"] for d in by_month(days)["2026-11"]] == ["2026-11-25", "2026-11-03"]
    assert month_title("2026-09") == "September 2026"
    assert monthly_md("2026-09").parent.name == "monthly" and monthly_md("2026-09").name == "2026-09.md"
    note = data_note(days)
    assert "2 day(s) 2026-10-31 → 2026-11-03 are a BACKTEST REPLAY" in note and "1 live day(s)" in note


def test_conditions_line_is_advice_only():
    from tradingbro.daily import conditions_line
    c = conditions_line(dict(verdict="CAUTION", reasons=["India VIX up +13.9% in 5 days"]))
    assert "CAUTION" in c and "half size" in c and "unchanged" in c
    ok = conditions_line(dict(verdict="OK", reasons=[], vix_chg5=2.0, breadth_with_trend=0.64))
    assert "OK" in ok and "+2.0%" in ok and "64%" in ok
    assert "not available" in conditions_line(dict(verdict="UNKNOWN", reasons=[]))
