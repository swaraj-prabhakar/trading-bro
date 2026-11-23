"""Daily jobs for the scheduled GitHub workflow (all times IST, Mon-Fri).

    python -m tradingbro.daily scan      # 10:10 - stocks + futures + options scans, picks saved to output/<date>/
    python -m tradingbro.daily midday    # 13:30 - provisional check, saved to output/<date>/review_1330.*
    python -m tradingbro.daily final     # 15:40 - final review (output/<date>/review.*) + rebuild Result.md
    python -m tradingbro.daily results   # rebuild Result.md only

Capital comes from the CAPITAL environment variable (default 100000).
"""
import json
import os
import sys
from collections import defaultdict

import pandas as pd

from .common import DISCLAIMER, fmt
from .config import NSE_HOLIDAYS, OUTPUT_DIR, ROOT
from .data import now_ist

RESULT_MD = ROOT / "Result.md"
KINDS = ("stocks", "futures", "options")


def trading_day(d) -> bool:
    return d.weekday() < 5 and d.isoformat() not in NSE_HOLIDAYS


def scan():
    cap = os.environ.get("CAPITAL", "100000")
    from . import futures, options, stocks
    for mod in (stocks, futures, options):
        print(f"\n######## {mod.__name__.split('.')[-1]} ########", flush=True)
        mod.main(["--capital", cap])


def review(name):
    from . import review as rv
    rv.main(["--date", now_ist().date().isoformat(), "--name", name])


# ------------------------------------------------------------------ Result.md
def _first_per_symbol(preds):
    seen, out = set(), []
    for r in sorted(preds, key=lambda r: str(r["signal_ts"])):
        k = (r["kind"], r["symbol"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def _market_label(folder):
    for f in sorted(folder.glob("*.json")):
        if f.name.startswith("review"):
            continue
        m = json.loads(f.read_text()).get("market")
        if m:
            return m.get("label", "-")
    return "-"


def load_days():
    days = []
    for folder in sorted(OUTPUT_DIR.glob("20??-??-??"), reverse=True):
        f = folder / "review.json"
        if not f.exists():
            continue
        rv = json.loads(f.read_text())
        if rv.get("status") != "final":
            continue
        picks = _first_per_symbol(rv["predictions"])
        trend = _market_label(folder)
        for p in picks:
            p["market"] = trend
        days.append(dict(date=folder.name, trend=trend, files=rv.get("files", []), picks=picks))
    return days


SUMMARY_COLS = [("Group", "group", 0), ("Picks", "picks", 0), ("Not filled", "not_filled", 0),
                ("✅ Target", "targets", 0), ("❌ Stop", "stops", 0), ("➖ 15:15 close", "sqoff", 0),
                ("Win %", "win_pct", 0), ("Avg R", "avg_r", 2), ("Profit factor", "pf", 2),
                ("Total P&L ₹", "total_pnl", 0)]
PICK_COLS = [("Segment", "kind", 0), ("Pick", "label", 0), ("Signal", "at", 0), ("Votes", "votes", 0),
             ("Entry", "entry", 2), ("Stop", "stop", 2), ("Target", "target", 2),
             ("Result", "verdict", 0), ("R", "r", 2), ("P&L ₹", "pnl", 0)]


def _table(rows, cols):
    out = ["| " + " | ".join(h for h, _, _ in cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(fmt(r.get(k), nd) for _, k, nd in cols) + " |")
    return out


def _icon(v):
    v = v or ""
    return ("✅ " if v.startswith("YES") else "❌ " if v.startswith("NO -") else
            "➖ " if v.startswith("NEITHER") else "⛔ " if v.startswith("NOT FILLED") else "") + v


def build_results():
    from .review import summarise
    days = load_days()
    allp = [p for d in days for p in d["picks"]]
    md = ["# TradingBro – intraday prediction results", "",
          f"_Updated {now_ist():%Y-%m-%d %H:%M} IST · scans at 10:10 IST, final review at 15:40 IST "
          f"(Mon–Fri) · capital ₹{float(os.environ.get('CAPITAL', '100000')):,.0f} per pick._", "",
          f"> {DISCLAIMER}", "", "## Overall summary", ""]
    if not days:
        md += ["No final reviews yet.", ""]
    else:
        filled = [p for p in allp if p.get("pnl") is not None]
        md += [f"**{len(days)} trading day(s)** · {days[-1]['date']} → {days[0]['date']} · "
               f"{len(allp)} picks · {len(filled)} filled", ""]
        groups = [summarise(allp, "All picks")]
        groups += [summarise([p for p in allp if p["kind"] == k], k.capitalize()) for k in KINDS
                   if any(p["kind"] == k for p in allp)]
        md += _table(groups, SUMMARY_COLS) + ["", "**By strategy agreement**", ""]
        md += _table([summarise([p for p in allp if p["votes"] == v], f"Votes {v}")
                      for v in sorted({p["votes"] for p in allp}, reverse=True)], SUMMARY_COLS)
        md += ["", "**By market trend at scan time**", ""]
        md += _table([summarise([p for p in allp if p["market"] == m], m)
                      for m in sorted({p["market"] for p in allp})], SUMMARY_COLS)
        md += ["", "_Win % = P&L > 0 after charges (filled picks). R = result in multiples of the planned risk. "
                   "Each pick is sized on the full capital, so totals are a sum of independent trades. "
                   "Option P&L is a Black-Scholes estimate; target/stop verdicts use exact spot prices. "
                   "A pick is \"not filled\" if price never traded back to the entry before 13:30._", ""]
    md += ["## Daily results", ""]
    for d in days:
        s = summarise(d["picks"], d["date"])
        md += [f"### {d['date']} · market {d['trend']}", "",
               f"{s.get('picks', 0)} picks · ✅ {s.get('targets', 0)} target · ❌ {s.get('stops', 0)} stop · "
               f"➖ {s.get('sqoff', 0)} closed 15:15 · ⛔ {s.get('not_filled', 0)} not filled · "
               f"win {fmt(s.get('win_pct'), 0)}% · avg {fmt(s.get('avg_r'), 2)}R · "
               f"P&L ₹{fmt(s.get('total_pnl'), 0)}", ""]
        rows = []
        for p in d["picks"]:
            rows.append(dict(p, at=str(p["signal_ts"])[11:16], verdict=_icon(p.get("verdict"))))
        md += (_table(rows, PICK_COLS) if rows else ["No picks this day."]) + [
            "", f"Files: {', '.join(f'[{n}](output/{d['date']}/{n})' for n in d['files'])} · "
                f"[full review](output/{d['date']}/review.md)", ""]
    RESULT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Result.md updated: {len(days)} day(s), {len(allp)} picks")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    job = argv[0] if argv else ""
    today = now_ist().date()
    if job in ("scan", "midday", "final") and not trading_day(today) and os.environ.get("FORCE") != "1":
        print(f"{today} is not an NSE trading day - nothing to do.")
        return
    if job == "scan":
        scan()
    elif job == "midday":
        review("review_1330")
    elif job == "final":
        review("review")
        build_results()
    elif job == "results":
        build_results()
    else:
        sys.exit("usage: python -m tradingbro.daily scan|midday|final|results")


if __name__ == "__main__":
    main()
