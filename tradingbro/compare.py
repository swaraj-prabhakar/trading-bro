"""Side-by-side comparison of the Yahoo and Upstox data pipelines -> Compare.md

    python -m tradingbro.compare

Reads the final end-of-day reviews in output/ (Yahoo) and output_upstox/ (Upstox).
Only days that have a final review from BOTH sources are compared, so neither side
gets credit for days the other one missed. Uses the first pick per (segment, symbol)
per day, the same rule as Result.md.
"""
from .common import DISCLAIMER, fmt
from .config import COMPARE_MD, OUTPUT_DIRS, PROFILE
from .daily import KINDS, SUMMARY_COLS, _table, load_days
from .data import now_ist
from .review import summarise

PSFX = f"_{PROFILE}" if PROFILE else ""
SOURCES = ("yahoo", "upstox")
LABEL = {"yahoo": "Yahoo", "upstox": "Upstox"}


def build_compare():
    days = {s: {d["date"]: d for d in load_days(OUTPUT_DIRS[s])} for s in SOURCES}
    common = sorted(set(days["yahoo"]) & set(days["upstox"]), reverse=True)
    only = {s: sorted(set(days[s]) - set(common)) for s in SOURCES}

    md = [f"# TradingBro – Yahoo vs Upstox data{' (personal: 2 picks per segment)' if PROFILE else ''}", "",
          f"_Updated {now_ist():%Y-%m-%d %H:%M} IST · same strategies, same schedule, only the market-data "
          f"source differs · full details: [Result{PSFX}.md](Result{PSFX}.md) (Yahoo) and "
          f"[Result_upstox{PSFX}.md](Result_upstox{PSFX}.md) (Upstox)._", "", f"> {DISCLAIMER}", ""]
    if not common:
        md += ["No day has a final review from both sources yet.", ""]
        for s in SOURCES:
            if only[s]:
                md.append(f"- {LABEL[s]} only: {', '.join(only[s])}")
        COMPARE_MD.write_text("\n".join(md), encoding="utf-8")
        print(f"{COMPARE_MD.name}: no common days yet")
        return

    picks = {s: [p for d in common for p in days[s][d]["picks"]] for s in SOURCES}
    md += [f"**{len(common)} common trading day(s)** · {common[-1]} → {common[0]}", ""]
    if any(only.values()):
        md += ["Not compared (one source only): " +
               "; ".join(f"{LABEL[s]}: {', '.join(only[s])}" for s in SOURCES if only[s]), ""]

    md += ["## Overall, by segment", ""]
    rows = []
    for k in (None,) + KINDS:
        for s in SOURCES:
            sel = [p for p in picks[s] if k is None or p["kind"] == k]
            rows.append(summarise(sel, f"{'All' if k is None else k.capitalize()} · {LABEL[s]}"))
    md += _table(rows, SUMMARY_COLS) + [""]

    md += ["## Day by day", "",
           "| Date | Yahoo picks | Yahoo win % | Yahoo P&L ₹ | Upstox picks | Upstox win % | Upstox P&L ₹ | Better |",
           "|---|---|---|---|---|---|---|---|"]
    tally = {"yahoo": 0, "upstox": 0, "tie": 0}
    for d in common:
        sy, su = summarise(days["yahoo"][d]["picks"], d), summarise(days["upstox"][d]["picks"], d)
        py, pu = sy.get("total_pnl") or 0.0, su.get("total_pnl") or 0.0
        better = "yahoo" if py > pu else "upstox" if pu > py else "tie"
        tally[better] += 1
        md.append(f"| {d} | {sy.get('picks', 0)} | {fmt(sy.get('win_pct'), 0)} | {fmt(py, 0)} | "
                  f"{su.get('picks', 0)} | {fmt(su.get('win_pct'), 0)} | {fmt(pu, 0)} | "
                  f"{'=' if better == 'tie' else LABEL[better]} |")
    md += ["", f"Better day count: Yahoo {tally['yahoo']} · Upstox {tally['upstox']} · tie {tally['tie']}", ""]

    md += ["## Same picks or different?", "",
           "How often both sources picked the same instrument on the same day, and how the picks that "
           "only one source made turned out.", "",
           "| Segment | Both | Yahoo only | Upstox only | Yahoo-only P&L ₹ | Upstox-only P&L ₹ |", "|---|---|---|---|---|---|"]
    for k in KINDS:
        key = lambda p: (str(p["signal_ts"])[:10], p["symbol"])
        y = {key(p): p for p in picks["yahoo"] if p["kind"] == k}
        u = {key(p): p for p in picks["upstox"] if p["kind"] == k}
        yo, uo = [y[x] for x in set(y) - set(u)], [u[x] for x in set(u) - set(y)]
        pnl = lambda ps: fmt(sum(p.get("pnl") or 0.0 for p in ps), 0)
        md.append(f"| {k.capitalize()} | {len(set(y) & set(u))} | {len(yo)} | {len(uo)} | {pnl(yo)} | {pnl(uo)} |")
    md += ["", "_Decide after at least 10 common days: prefer the source with the higher profit factor and "
               "average R; a higher total P&L from just a few picks is weaker evidence. "
               "Differences come from data timing (Yahoo lags) and small price differences between feeds._", ""]
    COMPARE_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"{COMPARE_MD.name} updated: {len(common)} common day(s)")


def main(argv=None):
    build_compare()


if __name__ == "__main__":
    main()
