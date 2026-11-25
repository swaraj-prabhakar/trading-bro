"""Daily jobs for the scheduled GitHub workflow (all times IST, Mon-Fri).

    python -m tradingbro.daily scan      # 10:10 - stocks + options scans, picks saved to output/<date>/
    python -m tradingbro.daily midday    # 13:30 - provisional check, saved to output/<date>/review_1330.*
    python -m tradingbro.daily final     # 15:40 - final review (output/<date>/review.*) + rebuild Result.md
    python -m tradingbro.daily results   # rebuild Result.md only
    python -m tradingbro.daily auto      # whatever is due now (scan / midday / final), each once a day -
                                         # what the frequent schedule and any external trigger call

Capital comes from the CAPITAL environment variable (default 100000).
"""
import json
import os
import sys
from collections import defaultdict

import pandas as pd

from .common import DISCLAIMER, fmt
from .config import NSE_HOLIDAYS, OUTPUT_DIR, PERSONAL_SLOTS, PICKS_MD, PROFILE, RESULT_MD, SOURCE, SOURCE_LABEL
from .data import now_ist

TITLE_SFX = ("" if SOURCE == "yahoo" else f" ({SOURCE_LABEL} data)") + \
    (f" – personal ({PERSONAL_SLOTS} picks per segment)" if PROFILE else "")
KINDS = ("stocks", "options")          # futures are not traded by this agent


def trading_day(d) -> bool:
    return d.weekday() < 5 and d.isoformat() not in NSE_HOLIDAYS


def scan_argv(capital):
    """Scanner arguments for the active profile. Personal: the top PERSONAL_SLOTS picks
    per segment, each sized on capital / PERSONAL_SLOTS (the capital goes into one segment)."""
    if PROFILE == "personal":
        return ["--capital", f"{float(capital) / PERSONAL_SLOTS:g}", "--top", str(PERSONAL_SLOTS)]
    return ["--capital", str(capital)]


def scan():
    cap = os.environ.get("CAPITAL", "100000")
    from . import options, stocks
    for mod in (stocks, options):
        print(f"\n######## {mod.__name__.split('.')[-1]} ########", flush=True)
        mod.main(scan_argv(cap))


def review(name, day=None):
    from . import review as rv
    rv.main(["--date", (day or now_ist().date()).isoformat(), "--name", name])


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


def load_days(output_dir=None):
    days = []
    for folder in sorted((output_dir or OUTPUT_DIR).glob("20??-??-??"), reverse=True):
        f = folder / "review.json"
        if not f.exists():
            continue
        rv = json.loads(f.read_text())
        if rv.get("status") != "final":
            continue
        picks = _first_per_symbol([r for r in rv["predictions"] if r["kind"] in KINDS])
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
    if PROFILE == "personal":
        from .personal import build_personal_results
        return build_personal_results()
    from .review import summarise
    days = load_days()
    allp = [p for d in days for p in d["picks"]]
    md = [f"# TradingBro – intraday prediction results{TITLE_SFX}", "",
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
            "", f"Files: {', '.join(f'[{n}]({OUTPUT_DIR.name}/{d['date']}/{n})' for n in d['files'])} · "
                f"[full review]({OUTPUT_DIR.name}/{d['date']}/review.md)", ""]
    RESULT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"{RESULT_MD.name} updated: {len(days)} day(s), {len(allp)} picks")


# ------------------------------------------------------------------ Picks.md (phone view)


def _latest_scan_files(folder):
    best = {}
    for f in sorted(folder.glob("*_*.json")):
        k = f.stem.split("_")[0]
        if k in KINDS:
            best[k] = f
    return [best[k] for k in KINDS if k in best]


def _status_map(folder):
    """(source file, kind, symbol) -> verdict, from the most recent review of the day."""
    for name, label in (("review.json", "final 15:40"), ("review_1330.json", "mid-day 13:30")):
        f = folder / name
        if f.exists():
            rv = json.loads(f.read_text())
            return label, {(r["source"], r["kind"], r["symbol"]): _icon(r.get("verdict")) for r in rv["predictions"]}
    return None, {}


def _link(url, text="Open in Upstox"):
    return f"[{text}]({url})" if url else "-"


def write_picks(day=None):
    day = day or now_ist().date().isoformat()
    folder = OUTPUT_DIR / day
    files = _latest_scan_files(folder) if folder.exists() else []
    md = [f"# TradingBro – today's picks{TITLE_SFX}", ""]
    if not files:
        md += [f"No scan saved for **{day}** (holiday, weekend, or the 10:10 scan has not run yet).", ""]
        PICKS_MD.write_text(chr(10).join(md + [f"> {DISCLAIMER}"]), encoding="utf-8")
        print(f"{PICKS_MD.name}: no scan for", day)
        return
    status_label, status = _status_map(folder)
    first = json.loads(files[0].read_text())
    m = first.get("market") or {}
    cap = first.get("capital", 0)
    md += [f"**{day}** · scan at {str(first['asof'])[11:16]} IST · market **{m.get('label', '-')}** · " +
           (f"capital ₹{cap * PERSONAL_SLOTS:,.0f} → ₹{cap:,.0f} per pick, trade ONE segment" if PROFILE else
            f"capital ₹{cap:,.0f} per pick") + (f" · status as of **{status_label}**" if status_label else ""), "",
           "How to trade: tap **Open in Upstox** → stocks: Buy · "
           "options: pick the expiry & strike, Buy the CE/PE. Place the stop-loss right after the buy fills; "
           "square off by 15:15. Options: exit on the **spot** stop/target.", ""]
    total = 0
    for f in files:
        pl = json.loads(f.read_text())
        kind, rows = pl["kind"], pl["picks"]
        total += len(rows)
        md += [f"## {kind.capitalize()} ({len(rows)})", ""]
        if not rows:
            md += ["No picks." + (" Market trend blocks buy-first trades today." if m.get("trend") == -1 and kind != "options" else ""), ""]
            continue
        st = lambda r: status.get((f.name, kind, r["symbol"]), "")
        if kind == "stocks":
            cols = ["Stock", "Side", "Buy at", "Stop", "Target", "Qty", "Max loss", "Max gain",
                    "RVOL" if "rvol" in rows[0] else "Votes", "Upstox"]
            body = [[r["symbol"], r["side"], f"{r['price']:,.2f}", f"{r['stop']:,.2f}", f"{r['target']:,.2f}",
                     str(r["units"]), f"₹{r['max_loss']:,.0f}", f"₹{r['max_gain']:,.0f}",
                     f"{r['rvol']:.1f}×" if "rvol" in r else r["votes"], _link(r.get("upstox"))] for r in rows]
        else:
            cols = ["Option", "Side", "Buy at ~ (premium)", "Premium stop ~", "Premium target ~", "Spot stop",
                    "Spot target", "Lots × lot", "Invest", "Max loss", "Max gain", "Votes", "Upstox"]
            body = [[r["option"], "BUY", f"{r['premium']:,.1f}", f"{r['prem_stop']:,.1f}", f"{r['prem_target']:,.1f}",
                     f"{r['spot_stop']:,.1f}", f"{r['spot_target']:,.1f}",
                     f"{r['lots']} × {r['lot']}", f"₹{r['invest']:,.0f}", f"₹{r['max_loss']:,.0f}",
                     f"₹{r['max_gain']:,.0f}", r["votes"], _link(r.get("upstox"), "Option chain")] for r in rows]
        if status_label:
            cols.insert(1, "Status")
            for r, b in zip(rows, body):
                b.insert(1, st(r) or "-")
        md += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(b) + " |" for b in body] + [""]
        if kind == "options":
            md += ["Options: **Buy at ~** is an *estimated* premium (no free live option prices) – check the live "
                   "premium in the option chain before buying. Exit when the **spot** price reaches the spot stop or "
                   "spot target (the premium stop/target are estimates of where the premium will be then).", ""]
        if kind == "stocks" and rows[0].get("valid_until"):
            md += [f"Stocks: place a **LIMIT buy at the 'Buy at' price** (the opening-range high) – it fills only if "
                   f"price pulls back to it. Cancel it if it has not filled by **{rows[0]['valid_until']}**.", ""]
    sizing = (f"Each row uses 1/{PERSONAL_SLOTS} of your capital: choose ONE segment (stocks or options) "
              f"and take its picks; with a single pick the rest stays unused. " if PROFILE else
              "Each row is sized on the full capital – split it if you take several. ")
    md += [f"_{total} pick(s). " + sizing +
           "Option premiums are estimates: use the live Upstox price. "
           f"Full history: [{RESULT_MD.name}]({RESULT_MD.name})._", "", f"> {DISCLAIMER}"]
    PICKS_MD.write_text(chr(10).join(md), encoding="utf-8")
    print(f"{PICKS_MD.name} updated: {total} pick(s) for {day}" + (f" (status: {status_label})" if status_label else ""))


# ------------------------------------------------------------------ auto (idempotent scheduler target)
SCAN_FROM, SCAN_UNTIL = "09:45", "13:30"     # live entries are only valid in this window
MIDDAY_FROM = "13:30"
FINAL_FROM = "15:35"                         # after the 15:30 close, so the day is complete
NEXT_DAY_UNTIL = "09:00"                     # a review run after midnight belongs to the previous session


def previous_trading_day(d):
    from datetime import timedelta
    for k in range(1, 10):
        p = d - timedelta(days=k)
        if trading_day(p):
            return p
    return d - timedelta(days=1)


def session_day(now=None):
    """The trading session a review run belongs to: today, or the previous trading day before 09:00."""
    now = now or now_ist()
    return previous_trading_day(now.date()) if now.strftime("%H:%M") < NEXT_DAY_UNTIL else now.date()


def scan_done(day) -> bool:
    folder = OUTPUT_DIR / day.isoformat()
    return folder.exists() and any(f.stem.split("_")[0] in KINDS for f in folder.glob("*_*.json"))


def final_done(day) -> bool:
    f = OUTPUT_DIR / day.isoformat() / "review.json"
    return f.exists() and json.loads(f.read_text()).get("status") == "final"


def auto_job(now=None):
    """(job, day) that is due now, or (None, reason). Safe to call any number of times a day:
    each step runs once - the scan in its entry window, the mid-day check, the final review
    (also after midnight for the previous session, if it was missed)."""
    now = now or now_ist()
    t, today = now.strftime("%H:%M"), now.date()
    if t < NEXT_DAY_UNTIL:
        day = previous_trading_day(today)
        if scan_done(day) and not final_done(day):
            return "final", day
        return None, f"before {NEXT_DAY_UNTIL}; {day} needs no review"
    if not trading_day(today):
        return None, f"{today} is not an NSE trading day"
    if t < SCAN_FROM:
        return None, f"before {SCAN_FROM}"
    if t < SCAN_UNTIL:
        return ("scan", today) if not scan_done(today) else (None, "today's scan is already saved")
    if not scan_done(today):
        return None, f"no scan today and the entry window closed at {SCAN_UNTIL}"
    if t < FINAL_FROM:
        done = (OUTPUT_DIR / today.isoformat() / "review_1330.json").exists()
        return ("midday", today) if not done else (None, "mid-day check already done")
    return ("final", today) if not final_done(today) else (None, "final review already done")


def compare_due(day) -> bool:
    """Upstox side: both final reviews exist for `day` but Compare*.md has no row for it yet."""
    from .config import COMPARE_MD, OUTPUT_DIRS
    if not all((OUTPUT_DIRS[s] / day.isoformat() / "review.json").exists() for s in ("yahoo", "upstox")):
        return False
    return not (COMPARE_MD.exists() and f"| {day.isoformat()} |" in COMPARE_MD.read_text(encoding="utf-8"))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    job = argv[0] if argv else ""
    day = None
    if job == "auto":
        job, day = auto_job()
        if job is None:
            print(f"auto: nothing to do ({day}).")
            if SOURCE == "upstox":
                d = session_day()
                if compare_due(d):
                    from .compare import build_compare
                    build_compare()
            return
        print(f"auto: running '{job}' for {day}", flush=True)
    elif job in ("scan", "midday", "final"):
        day = now_ist().date() if job == "scan" else session_day()
        if not trading_day(day) and os.environ.get("FORCE") != "1":
            print(f"{day} is not an NSE trading day - nothing to do.")
            return
    if job == "scan":
        scan()
        write_picks()
    elif job == "midday":
        review("review_1330", day)
        write_picks(day.isoformat())
    elif job == "final":
        review("review", day)
        build_results()
        write_picks(day.isoformat())
        if SOURCE == "upstox" and compare_due(day):
            from .compare import build_compare
            build_compare()
    elif job == "results":
        build_results()
    elif job == "picks":
        write_picks(argv[1] if len(argv) > 1 else None)
    elif job == "compare":
        from .compare import build_compare
        build_compare()
    else:
        sys.exit("usage: python -m tradingbro.daily auto|scan|midday|final|results|picks|compare [date]")


if __name__ == "__main__":
    main()
