---
name: tradingbro-picks
description: Shows today's TradingBro intraday picks (NIFTY 50 stocks, futures and CE/PE options) from both data sources, Yahoo and Upstox, with entry, stop-loss, target, quantity, max loss/gain and an "Open in Upstox" link for each, plus their live status, the track record and the Yahoo-vs-Upstox comparison. Use when the user asks for today's picks, intraday trades, what to buy today, TradingBro results, how the picks performed, or which data source is doing better.
---

# TradingBro picks (read-only, for phone use)

Two pipelines run the **same strategies** automatically on GitHub every trading day (Mon–Fri, IST), on different market data:
- **Yahoo** (original): scan 10:10 · mid-day status 13:30 · final result 15:40
- **Upstox** (trial, broker's own feed): scan 10:10 · mid-day status 13:30 · final result 15:55, then the comparison is updated

This skill only **reads** the published results. It never computes picks itself.

## Sources (public; use web fetch, not code execution)
Base: `https://raw.githubusercontent.com/swaraj-prabhakar/trading-bro/main/`
- Today's picks, Yahoo: `Picks.md` · Upstox: `Picks_upstox.md`
- Track record, Yahoo: `Result.md` · Upstox: `Result_upstox.md`
- Yahoo vs Upstox comparison: `Compare.md`
- Pages to open on the phone: https://github.com/swaraj-prabhakar/trading-bro/blob/main/Picks.md and https://github.com/swaraj-prabhakar/trading-bro/blob/main/Picks_upstox.md

## Steps
1. Fetch **both** `Picks.md` and `Picks_upstox.md`. If one fails, show the other and say which source is missing. If both fail, give the GitHub page links above and stop.
2. **Check the date** in each file against today's date in IST.
   - If a file is for an older day, say so clearly. The scan may not have run yet (before about 10:15 IST), or today may be a holiday or weekend. Do not present old picks as today's.
   - Before about 10:15 IST, explain that today's scans run at 10:10 and can start a few minutes late.
3. Show the **market trend** line for each source, then the picks per segment, **keeping every "Open in Upstox" / "Option chain" link** as a tappable link. Keep tables narrow for a phone: one segment per table, with the source in the heading (e.g. "Options · Upstox"). If space is tight, drop the Votes column first, never the links.
   - Default order: **Upstox first, then Yahoo**. If the user asks for only one source, show only that one.
   - **Agreement:** list the picks that appear in **both** files (same segment and symbol) first, marked "both sources". These are the strongest picks. For a pick in both, show the Upstox levels; mention it if the Yahoo levels differ noticeably.
4. If a **Status** column is present (after 13:30 / 15:40 / 15:55), show it and summarise per source: how many reached target, hit stop, are still open, or were not filled.
5. After 13:30 IST, warn the user that new entries are no longer valid (entry window 09:45–13:30) and that every position must be squared off by 15:15.
6. If the user asks about performance, fetch `Result.md` and `Result_upstox.md` and report each **Overall summary** (win %, avg R, P&L, by segment, by votes, by market trend).
7. If the user asks which source is better, or which to keep or drop, fetch `Compare.md` and report the per-segment Yahoo vs Upstox rows, the day-by-day better-day count and the "Same picks or different?" table. Fewer than 10 common days is too little to decide; say so. Judge mainly on profit factor and average R, not just total P&L.

## How to place the trade in the Upstox app (tell the user briefly)
- **Stock:** tap the link → **Buy** → Intraday → Limit at the "Buy at" price → Qty. Then place a **stop-loss (SL-M) sell** at the Stop.
- **Futures:** tap the link → **F&O** tab → the expiry shown → Buy → Intraday → the lots shown. Shift the stop and target by (live futures price − the shown price) if they differ.
- **Option:** tap "Option chain" → choose the **expiry and strike** shown → **Buy** the CE/PE → Intraday → the lots shown. Use the **live premium**; the shown premium is an estimate. Exit when the **spot** price reaches the spot stop or spot target.
- If the link opens in the browser instead of the app, use the browser's "Open in app", or search the symbol in the Upstox app.

## Rules
- Never invent, recalculate or "update" prices, strikes or quantities. Only report what the files say.
- Never merge the two sources into one list without labels: always say which source each pick came from.
- Each row is sized on the full capital. If the user takes several picks (from either source), they must split the capital. A pick shown by both sources is one trade, not two.
- Always end with: *Educational analysis, not investment advice. Intraday and F&O trading carry a high risk of loss.*
