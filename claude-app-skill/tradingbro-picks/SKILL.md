---
name: tradingbro-picks
description: Shows the user's personal TradingBro intraday picks (top 2 NIFTY 50 stocks and top 2 CE/PE options, each sized on half the capital) from both data sources, Yahoo and Upstox, with entry, stop-loss, target, quantity and an "Open in Upstox" link, plus the mid-day update, today's result, the track record per segment and the Yahoo-vs-Upstox comparison. Use when the user asks for today's picks, my picks, intraday trades, what to buy today, a mid-day update / how the picks are doing now, today's result / end-of-day result, TradingBro results or performance, or which data source is doing better.
---

# TradingBro personal picks (read-only, for phone use)

Two pipelines run the **same strategies** automatically on GitHub every trading day (Mon–Fri, IST), on different market data: **Yahoo** (original) and **Upstox** (trial, the broker's own feed).

This skill shows **only the personal view**:
- the top **2 stocks** and the top **2 options** for the day;
- each pick is sized on **half the capital**;
- the user puts the capital into **one** segment (stocks or options), so stocks and options are tracked as two separate accounts.

Never fetch or show the standard (top 10) pages (`Picks.md`, `Result.md`, `Compare.md`, `output/`, …), even if the user asks for "all picks". Say this skill shows the personal top 2 per segment only.

An external scheduler triggers the pipelines every 15 minutes, and each step runs once a day when it is due:
- **Scan:** the first run after 09:45, normally about **10:10** (the page shows the actual "scan at" time). A missed scan is retried until 13:30.
- **Mid-day update:** the first run after **13:30**.
- **Day result:** the first run after **15:35**. The comparison is updated once both final reviews exist.

This skill only **reads** the published results. It never computes picks itself.

## Sources (public; use web fetch, not code execution)
Base: `https://raw.githubusercontent.com/swaraj-prabhakar/trading-bro/main/`  (`<date>` = YYYY-MM-DD in IST)

| | Yahoo | Upstox |
|---|---|---|
| Today's picks | `Picks_personal.md` | `Picks_upstox_personal.md` |
| Mid-day update (13:30) | `output_personal/<date>/review_1330.md` | `output_upstox_personal/<date>/review_1330.md` |
| Day result (after 15:35) | `output_personal/<date>/review.md` | `output_upstox_personal/<date>/review.md` |
| Track record | `Result_personal.md` | `Result_upstox_personal.md` |

Yahoo vs Upstox comparison: `Compare_personal.md`.
Pages to open on the phone: `https://github.com/swaraj-prabhakar/trading-bro/blob/main/<file>` (for example `Picks_upstox_personal.md`).

## What the user can ask for
| User says | Show |
|---|---|
| "today's picks", "my picks", "what to buy" | **Today's picks** |
| "mid-day update", "how are the picks doing", "status" | **Mid-day update** |
| "today's result", "how did today go", "end of day", "final" | **Day result** |
| "overall performance", "track record" | **Track record** |
| "which source is better" | **Yahoo vs Upstox** |

If the user is unsure what to ask for, offer these options in one short line: *Picks · Mid-day update · Today's result · Track record · Yahoo vs Upstox*.

Show **Upstox first, then Yahoo**, always labelled with the source. If the user asks for only one source, show only that one. If one source's file fails to load, show the other and say which is missing. If both fail, give the GitHub page links and stop.

### Today's picks
1. Fetch `Picks_upstox_personal.md` and `Picks_personal.md`.
2. **Check the date** in each file against today's date in IST.
   - If a file is for an older day, say so clearly. Do not present old picks as today's.
   - Before about 10:15 IST, explain that today's scan runs at about 10:10 and can take a few minutes to appear.
3. Show the **market trend** line, the "scan at" time and the capital per pick. Then show one small table per segment and source (for example "Stocks · Upstox"), **keeping every "Open in Upstox" / "Option chain" link** as a tappable link. If space is tight, drop the Votes, RVOL and premium stop/target columns first. Never drop the links.
4. **Agreement:** a pick that appears in both sources (same segment and symbol) is marked "both sources" and listed first. These are the strongest picks. Show the Upstox levels, and mention it if the Yahoo levels differ noticeably.
5. Column meanings:
   - Stocks are ORB-30 breakouts. **RVOL** is today's volume compared with normal (higher is stronger).
   - Options: **"Buy at ~ (premium)"** is an *estimated* premium, not a live quote. Manage the trade by the **spot stop / spot target**.
6. If a **Status** column is present, show it (the header says whether it is the mid-day or the final status).
7. After 13:30 IST, warn the user that new entries are no longer valid (entry window 09:45–13:30) and that every position must be squared off by 15:15.

### Mid-day update
1. Use today's IST date. Fetch `review_1330.md` from both sources. If neither exists, say the mid-day check runs after 13:30 and is not published yet. Before 13:30, show the picks instead.
2. Per source, give the stocks and options rows of the **Accuracy summary**: picks, ✅ target, ❌ stop, still open, not filled, and P&L so far. Say clearly that this is **provisional**, with open trades valued at the 13:30 price.
3. List every pick from "Every prediction" in a short table: Pick · Result (✅ target at HH:MM / ❌ stop at HH:MM / ⏳ open +x.xR / ⛔ not filled) · P&L. Put picks that are still **open** first: those are the ones the user still has to watch. Remind the user to square off by 15:15.

### Day result
1. Fetch `review.md` for today from both sources. If it is missing, say the final review runs after 15:35 (before then, offer the mid-day update). Before 09:15 the next day, "today's result" means the latest finished trading day: use that date.
2. Per source, give the day's result for **stocks and options separately** (each is its own account; never add them together): picks, wins, P&L for the day and its % of the capital.
3. Then list each pick: ✅ target / ❌ stop / squared off at 15:15 (exit price, R) / ⛔ not filled, with its P&L.
4. Close with one line per segment from the Result page for context (for example "Upstox options: 8 days, +₹12,300, +12.3%"), if the Result page exists.

### Track record
Fetch `Result_upstox_personal.md` and `Result_personal.md`. Report the overall summary **per segment** (stocks account and options account separately): days traded, total P&L, return % on capital, win %, up/down days, best/worst day and max drawdown. Never add the two segments together. If a Result file doesn't exist yet, say it is created after the first final review.

### Yahoo vs Upstox
Fetch `Compare_personal.md`. Report the per-segment Yahoo vs Upstox rows, the day-by-day better-day count and the "Same picks or different?" table. Fewer than 10 common days is too little to decide; say so. Judge mainly on profit factor and average R, not just total P&L.

## How to place the trade in the Upstox app (tell the user briefly)
- **Stock:** tap the link → **Buy** → Intraday → Limit at the "Buy at" price → Qty. Then place a **stop-loss (SL-M) sell** at the Stop.
- **Option:** tap "Option chain" → choose the **expiry and strike** shown → **Buy** the CE/PE → Intraday → the lots shown. Use the **live premium**, because the shown premium is an estimate. Exit when the **spot** price reaches the spot stop or spot target.
- If the link opens in the browser instead of the app, use the browser's "Open in app", or search for the symbol in the Upstox app.

## Rules
- Never invent, recalculate or "update" prices, strikes or quantities. Only report what the files say.
- Never merge the two sources into one list without labels. Always say which source each pick came from.
- Each pick is already sized at half the capital, for ONE segment: the user trades either the stocks or the options, not both. A pick shown by both sources is one trade, not two.
- Always end with: *Educational analysis, not investment advice. Intraday and F&O trading carry a high risk of loss.*
