"""Strategy validation: backtest every strategy (and the ensemble) over the last ~60
sessions of 5-minute data for the whole NIFTY 50, and report which methods actually work.

    python -m tradingbro.validate
    python -m tradingbro.validate --allow-short --min-votes 4
    python -m tradingbro.validate --walk-forward 5     # replay the full agent on each of the last 5 days
"""
import argparse
import json

import numpy as np
import pandas as pd

from .common import DISCLAIMER, params_from_args, print_table, save_report
from .config import TZ
from .data import fetch_universe
from .engine import signal_at, simulate, stats
from .market import trend_series
from .strategies import STRATEGIES, add_signals
from .universe import filter_symbols, load_instruments


def strategy_table(prepared, p, allow_short, mkt=None):
    rows = []
    runs = [(n, n, None) for n in list(STRATEGIES) + ["ensemble"]]
    if mkt is not None:
        runs.append(("ensemble+trend", "ensemble", mkt))
    for label, name, m in runs:
        trades = [t for df in prepared.values() for t in simulate(df, p, allow_short, strategy=name, market=m)]
        s = stats(trades)
        r = np.array([t.r_multiple for t in trades]) if trades else np.array([0.0])
        reasons = pd.Series([t.reason for t in trades]).value_counts(normalize=True) if trades else {}
        rows.append(dict(strategy=label, trades=s["n"], win_pct=s["win_rate"] * 100, avg_r=s["avg_r"],
                         avg_ret_pct=s["avg_ret_pct"], pf=s["profit_factor"], total_r=s["total_r"],
                         target_pct=float(reasons.get("target", 0) * 100),
                         stop_pct=float(reasons.get("stop", 0) * 100),
                         sqoff_pct=float(reasons.get("squareoff", 0) * 100),
                         worst_r=float(r.min())))
    return rows


def walk_forward(prepared, p, allow_short, days, time, min_trades, mkt=None):
    """For each of the last `days` sessions: rank symbols exactly like the live agent
    (using only earlier data), take the top 10 and record what really happened."""
    any_df = next(iter(prepared.values()))
    sessions = sorted(set(any_df.index.date))[-days:]
    out = []
    for d in sessions:
        asof = pd.Timestamp(f"{d} {time}").tz_localize(TZ)
        picks = []
        for sym, df in prepared.items():
            mdir = None
            if mkt is not None:
                row = mkt[mkt.index <= asof]
                mdir = int(row.trend.iloc[-1]) if len(row) else 0
            sig = signal_at(df, asof, p, allow_short, with_outcome=True, market_dir=mdir)
            if sig is None or sig == "against_trend" or not sig.outcome:
                continue
            st = stats(simulate(df, p, allow_short, before_date=d, market=mkt))
            if st["n"] < min_trades or st["avg_r"] <= 0:
                continue
            r = sig.direction * (sig.outcome["exit"] - sig.price) / abs(sig.price - sig.stop)
            picks.append((st["avg_r"], sym, r, sig.outcome["reason"]))
        picks.sort(reverse=True)
        top = picks[:10]
        rs = [x[2] for x in top]
        out.append(dict(date=str(d), picks=len(top), wins=sum(r > 0 for r in rs),
                        total_r=float(sum(rs)), avg_r=float(np.mean(rs)) if rs else 0.0,
                        symbols=",".join(x[1] for x in top)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Backtest the intraday strategies on past sessions")
    ap.add_argument("--symbols", help="Comma-separated subset (default: all NIFTY 50 + indices)")
    ap.add_argument("--allow-short", action="store_true", help="Include bearish (sell / PE) trades")
    ap.add_argument("--min-votes", type=int, default=None)
    ap.add_argument("--rr", type=float, default=None)
    ap.add_argument("--sl-atr", type=float, default=None)
    ap.add_argument("--walk-forward", type=int, default=10, help="Sessions to replay with the full agent")
    ap.add_argument("--time", default="10:00", help="Decision time for walk-forward replays")
    ap.add_argument("--min-trades", type=int, default=5)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--no-trend", action="store_true", help="Walk-forward without the market-trend filter")
    a = ap.parse_args(argv)
    p = params_from_args(a)

    stocks, indices = load_instruments()
    universe = filter_symbols(indices + stocks, a.symbols.split(",") if a.symbols else None)
    intraday, daily, dropped = fetch_universe(universe, a.refresh)
    prepared = {i.symbol: add_signals(intraday[i.yahoo], p) for i in universe if i.yahoo in intraday}
    mkt = None
    if "NIFTY" in prepared:
        stocks_only = {k: v for k, v in prepared.items() if k not in ("NIFTY", "BANKNIFTY")}
        mkt = trend_series(prepared["NIFTY"], stocks_only, p, daily.get("^NSEI"))
    n_days = len(set(next(iter(prepared.values())).index.date))

    print(f"\n=== Strategy backtest: {len(prepared)} instruments x {n_days} sessions (5-min bars) ===")
    print(f"Mode: {'long + short' if a.allow_short else 'long only (buy first)'} | stop {p.sl_atr_mult} ATR | "
          f"target {p.rr}R | ensemble needs {p.min_votes}/5 | entries {p.entry_start}-{p.entry_end}")
    if dropped:
        print("No data:", ", ".join(dropped))
    rows = strategy_table(prepared, p, a.allow_short, mkt)
    print()
    print_table(rows, [("Strategy", "strategy", 0), ("Trades", "trades", 0), ("Win%", "win_pct", 1),
                       ("AvgR", "avg_r", 3), ("Avg%", "avg_ret_pct", 3), ("PF", "pf", 2),
                       ("TotalR", "total_r", 1), ("Tgt%", "target_pct", 0), ("Stop%", "stop_pct", 0),
                       ("SqOff%", "sqoff_pct", 0)])
    print("\nAvgR = average profit per trade in units of risk (gross of charges). >0 means an edge; "
          "PF = gross wins / gross losses.")

    wf = walk_forward(prepared, p, a.allow_short, a.walk_forward, a.time, a.min_trades,
                      None if a.no_trend else mkt)
    print(f"\n=== Walk-forward: full agent replayed at {a.time} on each of the last {len(wf)} sessions ===")
    print_table(wf, [("Date", "date", 0), ("Picks", "picks", 0), ("Wins", "wins", 0), ("TotalR", "total_r", 2),
                     ("AvgR", "avg_r", 2), ("Symbols", "symbols", 0)])
    tot = sum(x["total_r"] for x in wf)
    n = sum(x["picks"] for x in wf)
    w = sum(x["wins"] for x in wf)
    print(f"\nWalk-forward total: {n} trades, {w} wins ({(w / n * 100) if n else 0:.0f}%), {tot:+.2f}R overall")
    print("(1R = the amount risked per trade, e.g. 2% of capital -> +5R = +10% of capital before charges.)")
    save_report("validate", dict(params=p.to_dict(), allow_short=a.allow_short, strategies=rows, walk_forward=wf))
    print("\n" + DISCLAIMER)


if __name__ == "__main__":
    main()
