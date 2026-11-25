---
name: tradingbro-picks
description: Shows today's TradingBro intraday picks (NIFTY 50 stocks and CE/PE options) from both data sources, Yahoo and Upstox, with entry, stop-loss, target, quantity, max loss/gain and an "Open in Upstox" link for each, plus their live status, the track record, the personal 2-picks-per-segment pages and the Yahoo-vs-Upstox comparison. Use when the user asks for today's picks, intraday trades, what to buy today, "my picks" / personal picks, TradingBro results, how the picks performed, or which data source is doing better.
---

# TradingBro picks (read-only, for phone use)

Two pipelines run the **same strategies** automatically on GitHub every trading day (Mon–Fri, IST), on different market data: **Yahoo** (original) and **Upstox** (trial, the broker's own feed).
An external scheduler triggers them every 15 minutes, and each step runs once a day when it is due:
- **Scan:** the first run after 09:45, normally about **10:10** (the page shows the actual "scan at" time). A missed scan is retried until 13:30.
- **Mid-day status:** the first run after **13:30**.
- **Final result:** the first run after **15:35**. The comparison is updated once both final reviews exist.

Each pipeline publishes two views:
- **Standard:** top 10 stocks and top 10 options, each row sized on the **full capital**.
- **Personal:** top **2** stocks and top 2 options, each row sized on **half the capital**. Stocks and options are tracked as two separate accounts: the user puts the capital into **one** segment.

This skill only **reads** the published results. It never computes picks itself.

## Sources (public; use web fetch, not code execution)
Base: `https://raw.githubusercontent.com/swaraj-prabhakar/trading-bro/main/`

| | Yahoo | Upstox |
|---|---|---|
| Today's picks, standard | `Picks.md` | `Picks_upstox.md` |
| Today's picks, personal | `Picks_personal.md` | `Picks_upstox_personal.md` |
| Track record, standard | `Result.md` | `Result_upstox.md` |
| Track record, personal | `Result_personal.md` | `Result_upstox_personal.md` |

Comparisons (Yahoo vs Upstox): `Compare.md` (standard) and `Compare_personal.md` (personal).
Pages to open on the phone: `https://github.com/swaraj-prabhakar/trading-bro/blob/main/<file>` (for example `Picks.md`).

## Which view to show
- "my picks", "personal", "2 picks", "which 2 should I take", or the user says they trade one segment → **personal** pages.
- Otherwise → **standard** pages. Mention in one line that a personal (2 per segment) view exists.

## Steps
1. Fetch the chosen view from **both** sources (for example `Picks_upstox.md` and `Picks.md`). If one fails, show the other and say which source is missing. If both fail, give the GitHub page links and stop.
2. **Check the date** in each file against today's date in IST.
   - If a file is for an older day, say so clearly. Do not present old picks as today's.
   - Before about 10:15 IST, explain that today's scan runs at about 10:10 and can take a few minutes to appear.
3. Show the **market trend** line and the "scan at" time for each source. Then show the picks per segment, **keeping every "Open in Upstox" / "Option chain" link** as a tappable link. Keep tables narrow for a phone: one segment per table, with the source in the heading (for example "Options · Upstox"). If space is tight, drop the Votes, RVOL and premium stop/target columns first. Never drop the links.
   - Default order: **Upstox first, then Yahoo**. If the user asks for only one source, show only that one.
   - **Agreement:** list the picks that appear in **both** files (same segment and symbol) first, marked "both sources". These are the strongest picks. For a pick in both, show the Upstox levels, and mention it if the Yahoo levels differ noticeably.
4. Column meanings:
   - Stocks are ORB-30 breakouts. **RVOL** is today's volume compared with normal (higher is stronger).
   - Options: **"Buy at ~ (premium)"** is an *estimated* premium, not a live quote. The trade is managed by the **spot stop / spot target**.
5. If a **Status** column is present (after the mid-day or final run), show it and summarise per source: how many ✅ reached target, ❌ hit stop, are PENDING (still open, with R so far) or ⛔ were not filled. The page header says whether the status is "mid-day 13:30" (provisional) or final.
6. After 13:30 IST, warn the user that new entries are no longer valid (entry window 09:45–13:30) and that every position must be squared off by 15:15.
7. If the user asks about performance, fetch the matching Result file(s) and report the **Overall summary**:
   - Standard: win %, avg R, P&L, by segment, by votes, by market trend.
   - Personal: **per segment** (stocks account and options account separately): total P&L, return % on capital, win %, up/down days, best/worst day, max drawdown. Never add the two segments together.
8. If the user asks which source is better, or which to keep or drop, fetch `Compare.md` (or `Compare_personal.md` for the personal view). Report the per-segment Yahoo vs Upstox rows, the day-by-day better-day count and the "Same picks or different?" table. Fewer than 10 common days is too little to decide; say so. Judge mainly on profit factor and average R, not just total P&L.

## How to place the trade in the Upstox app (tell the user briefly)
- **Stock:** tap the link → **Buy** → Intraday → Limit at the "Buy at" price → Qty. Then place a **stop-loss (SL-M) sell** at the Stop.
- **Option:** tap "Option chain" → choose the **expiry and strike** shown → **Buy** the CE/PE → Intraday → the lots shown. Use the **live premium**, because the shown premium is an estimate. Exit when the **spot** price reaches the spot stop or spot target.
- If the link opens in the browser instead of the app, use the browser's "Open in app", or search for the symbol in the Upstox app.

## Rules
- Never invent, recalculate or "update" prices, strikes or quantities. Only report what the files say.
- Never merge the two sources into one list without labels. Always say which source each pick came from.
- Standard rows are each sized on the full capital: if the user takes several picks, they must split the capital. Personal rows are already sized at half the capital each, for ONE segment. A pick shown by both sources is one trade, not two.
- Always end with: *Educational analysis, not investment advice. Intraday and F&O trading carry a high risk of loss.*
