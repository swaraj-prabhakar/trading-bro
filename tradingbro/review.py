"""End-of-day review: check every prediction saved in output/<date>/ against what the
market actually did, and write an accuracy summary.

    python -m tradingbro.review                 # today
    python -m tradingbro.review --date 2026-11-23

Each pick is walked forward from the end of its signal bar on 1-minute bars (5-minute
if 1-minute data is no longer available - Yahoo keeps ~7 days), with the same rules the
scanner uses: stop or target, whichever is touched first (stop wins a tie inside one bar),
otherwise square-off at 15:15. Option P&L is re-priced with Black-Scholes from the saved
strike / expiry / IV, so it is an estimate; the spot-based verdict is exact.
"""
import argparse
import json
from datetime import date as Date

import numpy as np
import pandas as pd

from . import charges as chg
from .common import DISCLAIMER, print_table
from .config import OUTPUT_DIR, TZ, StrategyParams
from .data import fetch, now_ist, parse_date
from .options_math import bs_price, years_to_expiry
from .universe import load_instruments

SQUAREOFF = StrategyParams().squareoff
KINDS = ("stocks", "options")


def load_predictions(day: Date):
    folder = OUTPUT_DIR / day.isoformat()
    files = sorted(p for p in folder.glob("*.json") if not p.name.startswith("review"))
    preds = []
    for f in files:
        pl = json.loads(f.read_text())
        if pl.get("kind") not in KINDS:                # futures are no longer part of the agent
            continue
        for r in pl.get("picks", []):
            preds.append(normalise(pl["kind"], r, day, f.name))
    return folder, files, preds


def normalise(kind, r, day, source):
    ts = pd.Timestamp(f"{day} {r['signal_time']}").tz_localize(TZ)
    p = dict(kind=kind, source=source, symbol=r["symbol"], signal_ts=ts, votes=r.get("votes", "-"),
             qty=r.get("qty", r.get("units")), charges=r.get("charges", 0.0), max_gain=r.get("max_gain"),
             max_loss=r.get("max_loss"))
    if kind == "stocks":
        p.update(direction=1 if r["side"] == "BUY" else -1, entry=r["price"], stop=r["stop"], target=r["target"],
                 label=f"{r['symbol']} {r['side']}")
    else:
        p.update(direction=1 if r["type"] == "CE" else -1, entry=r["spot"], stop=r["spot_stop"],
                 target=r["spot_target"], label=r["option"], opt_type=r["type"], strike=r["strike"],
                 expiry=r["expiry"], iv=r["iv_pct"] / 100, premium=r["premium"])
    return p


def day_bars(tickers, day, bars="auto", refresh=True):
    """{ticker: (bars, interval)} preferring 1-minute data (bars="5m" forces 5-minute)."""
    out = {}
    one = fetch(tickers, "1m", "7d", refresh=refresh) if bars == "auto" else {}
    five = None
    for t in tickers:
        df = one.get(t)
        if df is not None and (df.index.date == day).any():
            out[t] = (df[df.index.date == day], "1m")
            continue
        if five is None:
            five = fetch(tickers, "5m", "60d", refresh=refresh)
        df = five.get(t)
        if df is not None and (df.index.date == day).any():
            out[t] = (df[df.index.date == day], "5m")
    return out


ENTRY_DEADLINE = StrategyParams().entry_end


def find_fill(b, d, e):
    """First bar where a limit order at `e` would have filled (buy: price traded at or
    below e; sell: at or above e) before the entry deadline. Returns index or None."""
    for i, (ts, row) in enumerate(b.iterrows()):
        if ts.strftime("%H:%M") > ENTRY_DEADLINE:
            return None
        if (d == 1 and row.low <= e) or (d == -1 and row.high >= e):
            return i
    return None


def verdict(r):
    t = r["exit_time"].strftime("%H:%M") if r.get("exit_time") is not None else ""
    o = r["outcome"]
    if o == "target":
        return f"YES - reached TARGET at {t}"
    if o == "stop":
        return f"NO - hit STOP LOSS at {t}"
    if o == "squareoff":
        return f"NEITHER - closed {t} at {r['r']:+.2f}R"
    if o == "open":
        return f"PENDING - open, now {r['r']:+.2f}R"
    if o == "not filled":
        return "NOT FILLED - price never came back to entry"
    return "NO DATA"


def evaluate(p, bars, interval, day_complete):
    start = p["signal_ts"] + pd.Timedelta(minutes=5)          # signal bar closes 5 minutes after its label
    b = bars[bars.index >= start]
    d, e, s, tg = p["direction"], p["entry"], p["stop"], p["target"]
    risk = abs(e - s)
    res = dict(outcome="no data", exit_time=None, exit=None)
    if len(b):
        fi = find_fill(b, d, e)
        if fi is None:
            out = dict(p, outcome="not filled", exit_time=None, exit=None, interval=interval, fill_time=None)
            out["verdict"] = verdict(out)
            return out
        fill_time = b.index[fi]
        b = b.iloc[fi:]                                        # trade only exists from the fill onwards
    else:
        fill_time = None
    best = worst = 0.0
    for ts, row in b.iterrows():
        if ts.strftime("%H:%M") >= SQUAREOFF:
            res = dict(outcome="squareoff", exit_time=ts, exit=float(row.open))
            break
        best = max(best, d * ((row.high if d == 1 else row.low) - e) / risk)
        worst = min(worst, d * ((row.low if d == 1 else row.high) - e) / risk)
        hit_stop = row.low <= s if d == 1 else row.high >= s
        hit_tgt = row.high >= tg if d == 1 else row.low <= tg
        if hit_stop:
            px = min(s, row.open) if d == 1 else max(s, row.open)
            res = dict(outcome="stop", exit_time=ts, exit=float(px))
            break
        if hit_tgt:
            px = max(tg, row.open) if d == 1 else min(tg, row.open)
            res = dict(outcome="target", exit_time=ts, exit=float(px))
            break
    else:
        if len(b):
            res = dict(outcome="squareoff" if day_complete else "open", exit_time=b.index[-1], exit=float(b.close.iloc[-1]))
    if res["exit"] is None:
        out = dict(p, **res, interval=interval, fill_time=fill_time)
        out["verdict"] = verdict(out)
        return out

    move = d * (res["exit"] - e)
    r_mult = move / risk if risk else 0.0
    if p["kind"] == "options":
        exp = parse_date(p["expiry"])
        prem_exit = bs_price(res["exit"], p["strike"], years_to_expiry(res["exit_time"], exp), p["iv"], p["opt_type"])
        pnl = (prem_exit - p["premium"]) * p["qty"] - p["charges"]
        extra = dict(premium_exit_est=prem_exit)
    else:
        pnl = move * p["qty"] - p["charges"]
        extra = {}
    out = dict(p, **res, **extra, interval=interval, move_pct=move / e * 100, r=r_mult, pnl=pnl,
               direction_right=move > 0, win=pnl > 0, best_r=best, worst_r=worst, fill_time=fill_time)
    out["verdict"] = verdict(out)
    return out


def summarise(rows, label):
    done = [r for r in rows if r.get("pnl") is not None]
    nf = sum(r["outcome"] == "not filled" for r in rows)
    if not done:
        return dict(group=label, picks=len(rows), not_filled=nf)
    pnl = np.array([r["pnl"] for r in done])
    oc = pd.Series([r["outcome"] for r in done]).value_counts()
    gains, losses = pnl[pnl > 0].sum(), -pnl[pnl < 0].sum()
    return dict(group=label, picks=len(rows), not_filled=nf, filled=len(done), targets=int(oc.get("target", 0)), stops=int(oc.get("stop", 0)),
                sqoff=int(oc.get("squareoff", 0)), open=int(oc.get("open", 0)),
                win_pct=float((pnl > 0).mean() * 100),
                dir_pct=float(np.mean([r["direction_right"] for r in done]) * 100),
                avg_r=float(np.mean([r["r"] for r in done])), total_pnl=float(pnl.sum()),
                pf=float(gains / losses) if losses > 0 else float("inf"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check saved intraday predictions against actual prices")
    ap.add_argument("--date", help="YYYY-MM-DD (default today)")
    ap.add_argument("--name", default="review", help="Output file name (review -> review.md/json)")
    ap.add_argument("--bars", choices=["auto", "5m"], default="auto",
                    help="auto = 1-minute bars when available (default), 5m = always 5-minute bars")
    ap.add_argument("--cached", action="store_true", help="Use cached bars instead of re-downloading")
    a = ap.parse_args(argv)
    now = now_ist()
    day = parse_date(a.date) if a.date else now.date()
    folder, files, preds = load_predictions(day)
    if not files:
        print(f"No saved predictions in {folder}. Run a scanner during market hours first.")
        return
    # Scans ran but found no picks: still write the review, so the day counts (as a no-trade day) in the results.
    day_complete = day < now.date() or now.strftime("%H:%M") >= "15:30"

    stocks, indices = load_instruments()
    ymap = {i.symbol: i.yahoo for i in stocks + indices}
    bars = day_bars(sorted({ymap[p["symbol"]] for p in preds if p["symbol"] in ymap}), day, a.bars, not a.cached)

    rows = []
    for p in preds:
        t = ymap.get(p["symbol"])
        if t not in bars:
            rows.append(dict(p, outcome="no data", verdict="NO DATA"))
            continue
        rows.append(evaluate(p, *bars[t], day_complete))

    # first prediction per (kind, symbol) = what you would actually have traded
    seen, unique = set(), []
    for r in sorted(rows, key=lambda r: r["signal_ts"]):
        k = (r["kind"], r["symbol"])
        if k not in seen:
            seen.add(k)
            unique.append(r)

    summary = [summarise([r for r in unique if r["kind"] == k], k) for k in KINDS]
    summary.append(summarise(unique, "ALL (first per symbol)"))
    summary.append(summarise(rows, "ALL saved predictions"))
    by_votes = [summarise([r for r in unique if r["votes"] == v], f"votes {v}")
                for v in sorted({r["votes"] for r in unique}, reverse=True)]

    status = "final" if day_complete else f"PROVISIONAL at {now:%H:%M} - open trades marked to market"
    print(f"\n=== Prediction review {day} ({status}) ===")
    print(f"Files: {', '.join(f.name for f in files)}")
    detail_cols = [("Kind", "kind", 0), ("Pick", "label", 0), ("At", "at", 0), ("Votes", "votes", 0),
                   ("Entry", "entry", 2), ("Stop", "stop", 2), ("Target", "target", 2), ("Filled@", "fill_at", 0),
                   ("Reached target or stop?", "verdict", 0), ("Exit", "exit", 2), ("R", "r", 2),
                   ("BestR", "best_r", 2), ("P&L Rs", "pnl", 0), ("Data", "interval", 0)]
    for r in rows:
        r["at"] = f"{r['signal_ts']:%H:%M}"
        r["exit_at"] = f"{r['exit_time']:%H:%M}" if r.get("exit_time") is not None else "-"
        r["fill_at"] = f"{r['fill_time']:%H:%M}" if r.get("fill_time") is not None else "-"
    print()
    print_table(rows, detail_cols)
    print("\nAccuracy summary")
    scols = [("Group", "group", 0), ("Picks", "picks", 0), ("NotFilled", "not_filled", 0), ("Target", "targets", 0),
             ("Stop", "stops", 0),
             ("SqOff", "sqoff", 0), ("Open", "open", 0), ("Win%", "win_pct", 0), ("RightDir%", "dir_pct", 0),
             ("AvgR", "avg_r", 2), ("PF", "pf", 2), ("Total P&L Rs", "total_pnl", 0)]
    print_table(summary, scols)
    print("\nBy strategy agreement (first per symbol)")
    print_table(by_votes, scols)
    print("\n* Win% = P&L > 0 after charges. RightDir% = price moved the predicted way by exit. "
          "R = result in multiples of the planned risk. BestR = furthest it went in your favour.")
    print("* An order counts as placed only if price traded back to the entry level after the signal (before "
          f"{ENTRY_DEADLINE}); target/stop are then checked from that fill onwards. Win%, RightDir% and AvgR count filled picks only.")
    print("* Each P&L uses the quantity/lots from the scan (each pick sized on the full capital).")
    print("* Option P&L is a Black-Scholes estimate at the exit spot price; spot results are exact.")

    out = dict(date=str(day), status=status, files=[f.name for f in files], summary=summary, by_votes=by_votes,
               predictions=rows)
    (folder / f"{a.name}.json").write_text(json.dumps(out, indent=2, default=str))
    md = [f"# Prediction review {day}", f"_Status: {status}_", "", "## Accuracy summary", "",
          "| " + " | ".join(h for h, _, _ in scols) + " |", "|" + "---|" * len(scols)]
    from .common import fmt
    for s in summary + by_votes:
        md.append("| " + " | ".join(fmt(s.get(k), nd) for _, k, nd in scols) + " |")
    md += ["", "## Every prediction", "", "| " + " | ".join(h for h, _, _ in detail_cols) + " |",
           "|" + "---|" * len(detail_cols)]
    for r in rows:
        md.append("| " + " | ".join(fmt(r.get(k), nd) for _, k, nd in detail_cols) + " |")
    md += ["", DISCLAIMER]
    (folder / f"{a.name}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nSaved: {folder / 'review.md'} and review.json")


if __name__ == "__main__":
    main()
