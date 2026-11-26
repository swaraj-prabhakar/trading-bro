"""Daily jobs for the scheduled GitHub workflow (all times IST, Mon-Fri).

    python -m tradingbro.daily scan      # 10:10 - stocks + options scans, picks saved to output_upstox/<date>/
    python -m tradingbro.daily midday    # 13:30 - provisional check -> output_upstox/<date>/review_1330.*
    python -m tradingbro.daily final     # 15:40 - final review (review.*) + rebuild Result_upstox.md
    python -m tradingbro.daily results   # rebuild Result_upstox.md only
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
from .config import NSE_HOLIDAYS, OUTPUT_DIR, PERSONAL_SLOTS, PICKS_MD, PROFILE, RESULT_MD, SOURCE_LABEL, monthly_md
from .data import now_ist

TITLE_SFX = f" ({SOURCE_LABEL} data)" + \
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
    try:                                   # shadow-mode market-conditions check: informs, never blocks
        from .conditions import save_assessment
        save_assessment(OUTPUT_DIR / now_ist().date().isoformat())
    except Exception as e:
        print(f"Market conditions check failed ({e})")


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
        _add_premium_levels(folder, picks)
        cf = folder / "conditions.json"
        cond = json.loads(cf.read_text()).get("verdict") if cf.exists() else None
        days.append(dict(date=folder.name, trend=trend, files=rv.get("files", []), picks=picks,
                         replay=_is_replay(folder), conditions=cond))
    return days


def _is_replay(folder):
    """True when the day's picks come from the backtest replay (python -m tradingbro.replay_days),
    not from a live scan."""
    for f in sorted(folder.glob("*_*.json")):
        if not f.name.startswith("review"):
            return str(json.loads(f.read_text()).get("saved_at", "")).startswith("replay")
    return False


def by_month(days):
    """{'2026-11': [days of that month]} (newest month first, days keep their order)."""
    out = {}
    for d in days:
        out.setdefault(d["date"][:7], []).append(d)
    return dict(sorted(out.items(), reverse=True))


def month_title(month):
    return pd.Timestamp(month + "-01").strftime("%B %Y")


def data_note(days):
    """One line saying which days are a backtest replay and which are live."""
    rep = sorted(d["date"] for d in days if d.get("replay"))
    live = sorted(d["date"] for d in days if not d.get("replay"))
    parts = []
    if rep:
        parts.append(f"**{len(rep)} day(s) {rep[0]} → {rep[-1]} are a BACKTEST REPLAY**: the agent's rules replayed "
                     "on past Upstox data at 10:05 (one scan a day, graded on 5-minute bars), not trades it made live. "
                     "Options on contracts that have since expired use Black-Scholes premium estimates (marked ~)")
    if live:
        parts.append(f"{len(live)} live day(s) {live[0]} → {live[-1]}")
    return "> " + ". ".join(parts) + "." if parts else ""


def conditions_line(c):
    """One line for the Picks page (shadow mode: the picks are not changed)."""
    if c.get("verdict") == "CAUTION":
        return ("**Market conditions (trial): ⚠️ CAUTION** – " + "; ".join(c["reasons"]) +
                ". In the 1-year study such days were weak for these picks – consider **half size**. "
                "The picks themselves are unchanged.")
    if c.get("verdict") == "OK":
        bits = []
        if c.get("vix_chg5") is not None:
            bits.append(f"India VIX {c['vix_chg5']:+.1f}% in 5 days")
        if c.get("breadth_with_trend") is not None:
            bits.append(f"{c['breadth_with_trend']:.0%} of NIFTY 50 stocks on the trade's side of VWAP")
        return "**Market conditions (trial): ✅ OK** – " + ", ".join(bits) + "."
    return "**Market conditions (trial):** not available today."


def conditions_table(days, label_kinds=KINDS):
    """Shadow-mode scorecard: how CAUTION vs OK days actually went (days that have a conditions check)."""
    from .review import summarise
    rows = []
    for v in ("OK", "CAUTION"):
        dd = [d for d in days if d.get("conditions") == v]
        for k in label_kinds:
            s = summarise([p for d in dd for p in d["picks"] if p["kind"] == k], f"{v} · {k}")
            rows.append(dict(s, days=len(dd)))
    if not any(r["days"] for r in rows):
        return []
    cols = [("Verdict · segment", "group", 0), ("Days", "days", 0), ("Picks", "picks", 0), ("Win %", "win_pct", 0),
            ("Avg R", "avg_r", 2), ("Total P&L ₹", "total_pnl", 0)]
    return (["## Market conditions check (trial)", "",
             "A shadow-mode flag shown on the Picks page since 27 Nov 2026 (it changes no picks): CAUTION when India "
             "VIX rose sharply over 5 days or breadth opposes the trade. This scorecard decides whether it should "
             "start cutting position size.", ""] + _table(rows, cols) + [""])


def write_monthly(days, render):
    """monthly/<YYYY-MM>[_personal].md for every month that has days; render(days, month) -> md lines."""
    for month, mdays in by_month(days).items():
        p = monthly_md(month)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(render(mdays, month)), encoding="utf-8")


SUMMARY_COLS = [("Group", "group", 0), ("Picks", "picks", 0), ("Not filled", "not_filled", 0),
                ("✅ Target", "targets", 0), ("❌ Stop", "stops", 0), ("➖ 15:15 close", "sqoff", 0),
                ("Win %", "win_pct", 0), ("Avg R", "avg_r", 2), ("Profit factor", "pf", 2),
                ("Total P&L ₹", "total_pnl", 0)]
STOCK_COLS = [("Stock", "label", 0), ("Signal", "at", 0), ("Entry", "entry", 2), ("Stop", "stop", 2),
              ("Target", "target", 2), ("Result", "verdict", 0), ("R", "r", 2), ("P&L ₹", "pnl", 0)]
OPTION_COLS = [("Option", "label", 0), ("Signal", "at", 0), ("Votes", "votes", 0),
               ("Buy at (premium)", "c_buy", 0), ("Filled at", "c_fill", 0), ("Premium stop", "c_stop", 0),
               ("Premium target", "c_tgt", 0), ("Exit premium", "c_exit", 0),
               ("Spot entry", "entry", 2), ("Spot stop", "stop", 2), ("Spot target", "target", 2),
               ("Result", "verdict", 0), ("R", "r", 2), ("P&L ₹", "pnl", 0)]


def _add_premium_levels(folder, picks):
    """Older review.json files lack the premium stop/target: take them from the saved scan file."""
    cache = {}
    for p in picks:
        if p["kind"] != "options" or p.get("prem_target") is not None:
            continue
        src = p.get("source")
        if src not in cache:
            f = folder / src if src else None
            cache[src] = json.loads(f.read_text()).get("picks", []) if f and f.exists() else []
        for r in cache[src]:
            if r.get("option") == p.get("label"):
                p["prem_stop"], p["prem_target"] = r.get("prem_stop"), r.get("prem_target")
                break


def pick_tables(picks):
    """Markdown for one day's picks: a stocks table and an options table (premium + spot levels)."""
    rows = [dict(p, at=str(p["signal_ts"])[11:16], verdict=_icon(p.get("verdict"))) for p in picks]
    for r in rows:
        if r["kind"] == "options":                     # "~" marks a Black-Scholes estimate, no mark = real Upstox price
            est = "" if r.get("premium_source") == "live" else "~"
            r["c_buy"], r["c_stop"], r["c_tgt"] = (_prem(r.get(k), est) for k in ("premium", "prem_stop", "prem_target"))
            r["c_fill"] = _prem(r.get("premium_entry"), "") if r.get("premium_entry") is not None else                 ("-" if r.get("outcome") == "not filled" else r["c_buy"])
            r["c_exit"] = _prem(r["premium_exit"], "") if r.get("premium_exit") is not None else                 _prem(r.get("premium_exit_est"), "~")
    if not rows:
        return ["No picks this day."]
    md = []
    for kind, title, cols in (("stocks", "Stocks", STOCK_COLS), ("options", "Options", OPTION_COLS)):
        part = [r for r in rows if r["kind"] == kind]
        if part:
            md += [f"**{title}**", ""] + _table(part, cols) + [""]
    if any(r["kind"] == "options" for r in rows):
        md += ["_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry "
               "and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. "
               "picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._", ""]
    return md


def _prem(v, mark):
    return "-" if v is None else f"{v:,.1f}{mark}"


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
    days = load_days()
    RESULT_MD.write_text("\n".join(render_results(days)), encoding="utf-8")
    write_monthly(days, render_results)
    print(f"{RESULT_MD.name} updated: {len(days)} day(s), {sum(len(d['picks']) for d in days)} picks; "
          f"{len(by_month(days))} monthly page(s) in {monthly_md('x').parent.name}/")


def render_results(days, month=None):
    """Result page lines for `days` (all of them, or one month: then links are relative to monthly/)."""
    from .review import summarise
    rel = "../" if month else ""
    allp = [p for d in days for p in d["picks"]]
    md = [f"# TradingBro – intraday prediction results{TITLE_SFX}" + (f" – {month_title(month)}" if month else ""), "",
          f"_Updated {now_ist():%Y-%m-%d %H:%M} IST · scans at 10:10 IST, final review after 15:35 IST "
          f"(Mon–Fri) · capital ₹{float(os.environ.get('CAPITAL', '100000')):,.0f} per pick._", ""]
    if month:
        md += [f"[← All results]({rel}{RESULT_MD.name})", ""]
    md += [data_note(days), "", f"> {DISCLAIMER}", ""]
    if not month and days:
        md += ["## By month", "", "| Month | Days | Picks | Win % | Avg R | Profit factor | Total P&L ₹ | Details |",
               "|---|---|---|---|---|---|---|---|"]
        for m, mdays in by_month(days).items():
            s = summarise([p for d in mdays for p in d["picks"]], m)
            md.append(f"| {month_title(m)} | {len(mdays)} | {s.get('picks', 0)} | {fmt(s.get('win_pct'), 0)} | "
                      f"{fmt(s.get('avg_r'), 2)} | {fmt(s.get('pf'), 2)} | {fmt(s.get('total_pnl'), 0)} | "
                      f"[{m}]({monthly_md(m).parent.name}/{monthly_md(m).name}) |")
        md += [""]
    md += conditions_table(days)
    md += ["## Overall summary" if not month else f"## {month_title(month)} summary", ""]
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
                   "Option P&L uses the contract's real Upstox premium (~ = Black-Scholes estimate where no real "
                   "price exists); target/stop verdicts use exact spot prices. "
                   "A pick is \"not filled\" if price never traded back to the entry before 13:30._", ""]
    md += ["## Daily results", ""]
    for d in days:
        s = summarise(d["picks"], d["date"])
        md += [f"### {d['date']} · market {d['trend']}" + (" · backtest replay" if d.get("replay") else ""), "",
               f"{s.get('picks', 0)} picks · ✅ {s.get('targets', 0)} target · ❌ {s.get('stops', 0)} stop · "
               f"➖ {s.get('sqoff', 0)} closed 15:15 · ⛔ {s.get('not_filled', 0)} not filled · "
               f"win {fmt(s.get('win_pct'), 0)}% · avg {fmt(s.get('avg_r'), 2)}R · "
               f"P&L ₹{fmt(s.get('total_pnl'), 0)}", ""]
        md += pick_tables(d["picks"]) + [
            f"Files: {', '.join(f'[{n}]({rel}{OUTPUT_DIR.name}/{d['date']}/{n})' for n in d['files'])} · "
                f"[full review]({rel}{OUTPUT_DIR.name}/{d['date']}/review.md)", ""]
    return md


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
    cond = json.loads((folder / "conditions.json").read_text()) if (folder / "conditions.json").exists() else None
    first = json.loads(files[0].read_text())
    m = first.get("market") or {}
    cap = first.get("capital", 0)
    md += [f"**{day}** · scan at {str(first['asof'])[11:16]} IST · market **{m.get('label', '-')}** · " +
           (f"capital ₹{cap * PERSONAL_SLOTS:,.0f} → ₹{cap:,.0f} per pick, trade ONE segment" if PROFILE else
            f"capital ₹{cap:,.0f} per pick") + (f" · status as of **{status_label}**" if status_label else ""), "",
           "How to trade: tap **Open in Upstox** → stocks: Buy · "
           "options: pick the expiry & strike, Buy the CE/PE. Place the stop-loss right after the buy fills; "
           "square off by 15:15. Options: exit on the **spot** stop/target.", ""]
    if cond:
        md += [conditions_line(cond), ""]
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
            cols = ["Option", "Side", "Buy at (premium)", "Premium stop", "Premium target", "Spot stop",
                    "Spot target", "Lots × lot", "Invest", "Max loss", "Max gain", "Votes", "Upstox"]
            mk = lambda r: "" if r.get("premium_source") == "live" else "~"
            body = [[r["option"], "BUY", _prem(r["premium"], mk(r)), _prem(r["prem_stop"], mk(r)),
                     _prem(r["prem_target"], mk(r)),
                     f"{r['spot_stop']:,.1f}", f"{r['spot_target']:,.1f}",
                     f"{r['lots']} × {r['lot']}", f"₹{r['invest']:,.0f}", f"₹{r['max_loss']:,.0f}",
                     f"₹{r['max_gain']:,.0f}", r["votes"], _link(r.get("upstox"), "Option chain")] for r in rows]
        if status_label:
            cols.insert(1, "Status")
            for r, b in zip(rows, body):
                b.insert(1, st(r) or "-")
        md += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(b) + " |" for b in body] + [""]
        if kind == "options":
            md += ["Options: **Buy at** is the contract's real last traded premium on Upstox at the scan – place a "
                   "**limit buy** at it (it may have moved since; check the option chain). Exit when the **spot** price "
                   "reaches the spot stop or spot target; the premium stop/target show roughly where the premium will "
                   "be then. A value marked ~ is an estimate (no real price was available).", ""]
        if kind == "stocks" and rows[0].get("valid_until"):
            md += [f"Stocks: place a **LIMIT buy at the 'Buy at' price** (the opening-range high) – it fills only if "
                   f"price pulls back to it. Cancel it if it has not filled by **{rows[0]['valid_until']}**.", ""]
    sizing = (f"Each row uses 1/{PERSONAL_SLOTS} of your capital: choose ONE segment (stocks or options) "
              f"and take its picks; with a single pick the rest stays unused. " if PROFILE else
              "Each row is sized on the full capital – split it if you take several. ")
    md += [f"_{total} pick(s). " + sizing +
           "Option premiums are real Upstox prices at the scan time (~ = estimate). "
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


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    job = argv[0] if argv else ""
    day = None
    if job == "auto":
        job, day = auto_job()
        if job is None:
            print(f"auto: nothing to do ({day}).")
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
    elif job == "results":
        build_results()
    elif job == "picks":
        write_picks(argv[1] if len(argv) > 1 else None)
    else:
        sys.exit("usage: python -m tradingbro.daily auto|scan|midday|final|results|picks [date]")


if __name__ == "__main__":
    main()
