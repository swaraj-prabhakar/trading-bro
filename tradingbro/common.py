"""Shared CLI plumbing for the three scanners."""
import argparse
import json
import math
import sys

import pandas as pd

from .config import OUTPUT_DIR, REPORT_DIR, SOURCE, SOURCE_LABEL, StrategyParams, TZ
from .data import market_is_open, now_ist, parse_date

DISCLAIMER = ("Educational tool, not investment advice. Backtests on ~60 days of data do not "
              "guarantee future results. Intraday F&O trading is high-risk; most retail traders lose money.")


def base_parser(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--capital", type=float, required=True, help="Amount you have in hand (Rs)")
    ap.add_argument("--top", type=int, default=10, help="How many picks to show (default 10)")
    ap.add_argument("--risk-pct", type=float, default=2.0, help="Max loss per trade as %% of capital (default 2)")
    ap.add_argument("--date", help="Replay a past session YYYY-MM-DD (validates the agent on that day)")
    ap.add_argument("--time", default=None, help="Decision time HH:MM for replay (default 10:00)")
    ap.add_argument("--symbols", help="Comma-separated subset, e.g. SBIN,ITC,NIFTY")
    ap.add_argument("--min-votes", type=int, default=None, help="Strategies that must agree (1-5, default 3)")
    ap.add_argument("--min-trades", type=int, default=5, help="Min backtest trades for a symbol to qualify")
    ap.add_argument("--rr", type=float, default=None, help="Reward:risk ratio (default 2)")
    ap.add_argument("--sl-atr", type=float, default=None, help="Stop distance in ATRs (default 1.5)")
    ap.add_argument("--refresh", action="store_true", help="Ignore cached data")
    ap.add_argument("--json", action="store_true", help="Print the report as JSON only")
    ap.add_argument("--no-trend", action="store_true",
                    help="Don't filter by overall market trend (default: only trade with the NIFTY trend)")
    ap.add_argument("--no-save", action="store_true", help="Don't save live picks to output/ for the end-of-day review")
    return ap


def params_from_args(a) -> StrategyParams:
    p = StrategyParams()
    if a.min_votes is not None:
        p.min_votes = a.min_votes
    if a.rr is not None:
        p.rr = a.rr
    if a.sl_atr is not None:
        p.sl_atr_mult = a.sl_atr
    return p


def resolve_asof(intraday: dict, a):
    """Returns (asof timestamp, mode) where mode is 'live' or 'replay'."""
    last = max(df.index[-1] for df in intraday.values())
    if a.date:
        t = a.time or "10:00"
        return pd.Timestamp(f"{a.date} {t}").tz_localize(TZ), "replay"
    now = now_ist()
    if market_is_open(now) and last.date() == now.date() and not a.time:
        return last, "live"
    t = a.time or "10:00"
    return pd.Timestamp(f"{last.date()} {t}").tz_localize(TZ), "replay"


def fmt(v, nd=2):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "-"
    if isinstance(v, float):
        return f"{v:,.{nd}f}"
    return str(v)


def print_table(rows, cols):
    """cols: list of (header, key, decimals)."""
    cells = [[h for h, _, _ in cols]] + [[fmt(r.get(k), nd) for _, k, nd in cols] for r in rows]
    w = [max(len(row[i]) for row in cells) for i in range(len(cols))]
    for n, row in enumerate(cells):
        print("  ".join(c.rjust(w[i]) if n and i else c.ljust(w[i]) for i, c in enumerate(row)))
        if n == 0:
            print("  ".join("-" * x for x in w))


def header(kind, a, asof, mode, p, universe_n, dropped, rules=None):
    if getattr(a, "json", False):
        return
    print(f"\n=== TradingBro | {kind.upper()} intraday | {SOURCE_LABEL} data | capital Rs {a.capital:,.0f} ===")
    if mode == "live":
        lag = " (Upstox data, last completed 5-min bar)"
        print(f"LIVE signals as of {asof:%Y-%m-%d %H:%M} IST{lag}")
    else:
        print(f"REPLAY of {asof:%Y-%m-%d} at {asof:%H:%M} IST - market is closed or a past date was "
              f"requested; 'Actual' columns show what really happened after that time.")
    print(rules or f"Rules: >= {p.min_votes}/5 strategies agree | stop {p.sl_atr_mult} x ATR(5m) | target {p.rr}R | "
          f"entries {p.entry_start}-{p.entry_end} | square-off {p.squareoff}")
    print(f"Universe: {universe_n} instruments" + (f" (no data: {', '.join(dropped)})" if dropped else ""))


def save_report(kind, payload, quiet=False):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{kind}_{now_ist():%Y%m%d_%H%M%S}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))
    if not quiet:
        print(f"\nReport saved: {path}")
    return path


def save_prediction(kind, payload, quiet=False):
    """Save picks to output/<date>/<kind>_<HHMM>.json for the end-of-day review
    (python -m tradingbro.review). Re-running in the same minute overwrites."""
    asof = pd.Timestamp(payload["asof"])
    payload = dict(payload, saved_at=str(now_ist()), source=SOURCE)
    d = OUTPUT_DIR / f"{asof:%Y-%m-%d}"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{kind}_{asof:%H%M}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))
    if not quiet:
        print(f"Prediction saved for review: {path}")
    return path


def finish(kind, a, payload, rows, cols, notes):
    if payload.get("mode") == "live" and not getattr(a, "no_save", False):
        save_prediction(kind, payload, quiet=a.json)
    if a.json:
        json.dump(payload, sys.stdout, indent=2, default=str)
        save_report(kind, payload, quiet=True)
        return
    print()
    if rows:
        print_table(rows, cols)
    else:
        print("No instrument currently has a signal that also passed the backtest filter.")
    for n in notes:
        print("* " + n)
    save_report(kind, payload)
    print("\n" + DISCLAIMER)


def symbols_arg(a):
    return a.symbols.split(",") if a.symbols else None
