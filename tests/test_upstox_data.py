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
    assert len(set(df.index.date)) == 60                 # 60 sessions, like Yahoo's "60d"
    assert df.index[-1].date() == date(2026, 11, 25)     # today's intraday bars appended


def test_source_switch_separates_outputs():
    code = "from tradingbro import config as c; print(c.SOURCE, c.OUTPUT_DIR.name, c.RESULT_MD.name, c.PICKS_MD.name)"
    run = lambda src: subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                                     env=dict(os.environ, TRADINGBRO_SOURCE=src)).stdout.split()
    assert run("yahoo") == ["yahoo", "output", "Result.md", "Picks.md"]
    assert run("upstox") == ["upstox", "output_upstox", "Result_upstox.md", "Picks_upstox.md"]


def _cfg(env, code):
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                          env=dict(os.environ, **env)).stdout.split()


def test_personal_profile_has_own_files_and_split_capital():
    code = ("from tradingbro import config as c, daily as d; "
            "print(c.OUTPUT_DIR.name, c.RESULT_MD.name, c.PICKS_MD.name, c.COMPARE_MD.name, *d.scan_argv(100000))")
    assert _cfg({"TRADINGBRO_SOURCE": "yahoo", "TRADINGBRO_PROFILE": ""}, code) == \
        ["output", "Result.md", "Picks.md", "Compare.md", "--capital", "100000"]
    assert _cfg({"TRADINGBRO_SOURCE": "upstox", "TRADINGBRO_PROFILE": "personal"}, code) == \
        ["output_upstox_personal", "Result_upstox_personal.md", "Picks_upstox_personal.md", "Compare_personal.md",
         "--capital", "50000", "--top", "2"]


def test_up_launcher_uses_same_history_as_yahoo():
    code = ("import os; import tradingbro.up as u; "
            "u.importlib.import_module = lambda n: type('M', (), {'main': staticmethod("
            "lambda a: print(os.environ['TRADINGBRO_SOURCE'], os.environ.get('TRADINGBRO_HISTORY_SESSIONS', '60')))}); "
            "u.main(['stocks'])")
    env = {k: v for k, v in os.environ.items() if k not in ("TRADINGBRO_HISTORY_SESSIONS", "TRADINGBRO_SOURCE")}
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, env=env).stdout.split()
    assert out == ["upstox", "60"]
