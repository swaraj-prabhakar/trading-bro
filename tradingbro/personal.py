"""Personal P&L pages (TRADINGBRO_PROFILE=personal) -> Result_personal.md / Result_upstox_personal.md

Rules being measured:
- the 10:10 scan gives at most PERSONAL_SLOTS (2) picks per segment;
- the whole capital goes into ONE segment only (stocks OR options), split
  equally between that segment's picks (each pick sized on capital / 2 by the scanner);
- so each segment is its own account: its P&L, return on capital, best/worst day and
  drawdown are reported separately and never added together.

Only the first scan file of each segment per day counts (the picks you would have
traded); later re-scans the same day are ignored.
"""
import os

from .common import DISCLAIMER, fmt
from .config import OUTPUT_DIR, PERSONAL_SLOTS, RESULT_MD, monthly_md
from .daily import (KINDS, TITLE_SFX, _table, by_month, conditions_table, data_note, load_days, month_title,
                    pick_tables, write_monthly)
from .data import now_ist


def personal_days():
    """load_days() restricted to each segment's first scan file of the day."""
    days = load_days()
    for d in days:
        first = {}
        for f in sorted(d["files"]):
            k = f.split("_")[0]
            if k in KINDS and k not in first:
                first[k] = f
        d["picks"] = [p for p in d["picks"] if p.get("source") == first.get(p["kind"])]
        d["pnl"] = {k: sum(p.get("pnl") or 0.0 for p in d["picks"] if p["kind"] == k)
                    if any(p["kind"] == k for p in d["picks"]) else None for k in KINDS}
    return sorted(days, key=lambda d: d["date"])


def segment_stats(days, kind, capital):
    picks = [p for d in days for p in d["picks"] if p["kind"] == kind]
    filled = [p for p in picks if p.get("pnl") is not None]
    daily = [d["pnl"][kind] for d in days if d["pnl"][kind] is not None]
    eq, peak, dd = 0.0, 0.0, 0.0
    for v in (d["pnl"][kind] or 0.0 for d in days):         # equity curve over all days (no trade = flat)
        eq += v
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    total = sum(daily)
    oc = [p.get("outcome") for p in filled]
    return dict(group=kind.capitalize(), days=len(days), traded=len(daily), picks=len(picks), filled=len(filled),
                targets=oc.count("target"), stops=oc.count("stop"), sqoff=oc.count("squareoff"),
                win_pct=sum(p["pnl"] > 0 for p in filled) / len(filled) * 100 if filled else None,
                win_days=sum(v > 0 for v in daily), loss_days=sum(v < 0 for v in daily),
                total_pnl=total, ret_pct=total / capital * 100, avg_day=total / len(daily) if daily else None,
                best=max(daily) if daily else None, worst=min(daily) if daily else None, max_dd=dd)


STAT_COLS = [("Segment", "group", 0), ("Days traded", "traded", 0), ("Picks", "picks", 0), ("✅ Target", "targets", 0),
             ("❌ Stop", "stops", 0), ("➖ 15:15", "sqoff", 0), ("Win %", "win_pct", 0), ("Up / down days", "updown", 0),
             ("Total P&L ₹", "total_pnl", 0), ("Return on capital %", "ret_pct", 1), ("Avg / traded day ₹", "avg_day", 0),
             ("Best day ₹", "best", 0), ("Worst day ₹", "worst", 0), ("Max drawdown ₹", "max_dd", 0)]


def build_personal_results():
    days = personal_days()
    RESULT_MD.write_text("\n".join(render_personal(days)), encoding="utf-8")
    write_monthly(days, render_personal)
    print(f"{RESULT_MD.name} updated: {len(days)} day(s); {len(by_month(days))} monthly page(s)")


def render_personal(days, month=None):
    """Personal result page lines for `days` (all of them, or one month: links relative to monthly/)."""
    capital = float(os.environ.get("CAPITAL", "100000"))
    days = sorted(days, key=lambda d: d["date"])
    rel = "../" if month else ""
    md = [f"# TradingBro – personal P&L{TITLE_SFX}" + (f" – {month_title(month)}" if month else ""), "",
          f"_Updated {now_ist():%Y-%m-%d %H:%M} IST · capital ₹{capital:,.0f} put into **one segment only**, "
          f"split between its top {PERSONAL_SLOTS} picks (₹{capital / PERSONAL_SLOTS:,.0f} each) from the 10:10 scan._", ""]
    if month:
        md += [f"[← All results]({rel}{RESULT_MD.name})", ""]
    md += ["Each segment below is a separate account: read the row for the segment you trade. "
           "The segments are **not** added together.", "", data_note(days), "", f"> {DISCLAIMER}", ""]
    if not month and days:
        md += ["## By month (P&L ₹ and return on capital per segment)", "",
               "| Month | Days | Stocks P&L ₹ | Stocks return % | Options P&L ₹ | Options return % | Details |",
               "|---|---|---|---|---|---|---|"]
        for m, mdays in by_month(sorted(days, key=lambda d: d["date"], reverse=True)).items():
            st, op = (segment_stats(sorted(mdays, key=lambda d: d["date"]), k, capital) for k in KINDS)
            md.append(f"| {month_title(m)} | {len(mdays)} | {fmt(st['total_pnl'], 0)} | {fmt(st['ret_pct'], 1)} | "
                      f"{fmt(op['total_pnl'], 0)} | {fmt(op['ret_pct'], 1)} | "
                      f"[{m}]({monthly_md(m).parent.name}/{monthly_md(m).name}) |")
        md += [""]
    md += conditions_table(days)
    md += ["## Per segment" if not month else f"## {month_title(month)} per segment", ""]
    if not days:
        md += ["No final reviews yet.", ""]
    else:
        md += [f"**{len(days)} trading day(s)** · {days[0]['date']} → {days[-1]['date']}", ""]
        rows = []
        for k in KINDS:
            s = segment_stats(days, k, capital)
            s["updown"] = f"{s['win_days']} / {s['loss_days']}"
            rows.append(s)
        md += _table(rows, STAT_COLS)
        md += ["", "_Days traded = days the segment had at least one pick. Return on capital = total P&L ÷ "
                   f"₹{capital:,.0f}. Max drawdown = deepest fall of the running P&L from its high. Win % counts "
                   "filled picks, after charges. Option P&L uses the contract's real Upstox premium (~ = "
                   "Black-Scholes estimate where no real price exists); target/stop verdicts use exact spot prices._", "",
               "## Day by day (P&L ₹, running total in brackets)", "",
               "| Date | Market | Stocks | Options |", "|---|---|---|---|"]
        run = {k: 0.0 for k in KINDS}
        lines = []
        for d in days:
            cells = []
            for k in KINDS:
                v = d["pnl"][k]
                run[k] += v or 0.0
                cells.append("-" if v is None else f"{fmt(v, 0)} ({fmt(run[k], 0)})")
            lines.append(f"| {d['date']}{' (replay)' if d.get('replay') else ''} | {d['trend']} | "
                         + " | ".join(cells) + " |")
        md += lines[::-1] + ["", "## Daily picks", ""]
        for d in reversed(days):
            md += [f"### {d['date']} · market {d['trend']}" + (" · backtest replay" if d.get("replay") else ""), ""]
            md += pick_tables(d["picks"]) + [
                f"[full review]({rel}{OUTPUT_DIR.name}/{d['date']}/review.md)", ""]
    return md
