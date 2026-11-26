---
name: tradingbro-picks
description: Shows the user's personal TradingBro intraday picks (top 2 NIFTY 50 stocks and top 2 CE/PE options, each sized on half the capital, on Upstox market data) with entry, stop-loss, target, quantity, the real option premium and an "Open in Upstox" link, plus the mid-day update, today's result and the track record per segment. Use when the user asks for today's picks, my picks, intraday trades, what to buy today, a mid-day update / how the picks are doing now, today's result / end-of-day result, or TradingBro results or performance.
---

# TradingBro personal picks (read-only, for phone use)

TradingBro runs automatically on GitHub every trading day (Mon–Fri, IST) on **Upstox** market data (the broker's own feed).

This skill shows **only the personal view**:
- the top **2 stocks** and the top **2 options** for the day;
- each pick is sized on **half the capital**;
- the user puts the capital into **one** segment (stocks or options), so stocks and options are tracked as two separate accounts.

Never fetch or show the standard (top 10) pages (`Picks_upstox.md`, `Result_upstox.md`, `output_upstox/`), even if the user asks for "all picks". Say this skill shows the personal top 2 per segment only.

An external scheduler triggers the workflow every 15 minutes, and each step runs once a day when it is due:
- **Scan:** the first run after 09:45, normally about **10:10** (the page shows the actual "scan at" time). A missed scan is retried until 13:30.
- **Mid-day update:** the first run after **13:30**.
- **Day result:** the first run after **15:35**.

This skill only **reads** the published results. It never computes picks itself.

## Sources (public; use web fetch, not code execution)
Base: `https://raw.githubusercontent.com/swaraj-prabhakar/trading-bro/main/`  (`<date>` = YYYY-MM-DD in IST)

| What | File |
|---|---|
| Today's picks | `Picks_upstox_personal.md` |
| Mid-day update (13:30) | `output_upstox_personal/<date>/review_1330.md` |
| Day result (after 15:35) | `output_upstox_personal/<date>/review.md` |
| Track record | `Result_upstox_personal.md` |
| One month's result | `monthly/<YYYY-MM>_personal.md` (e.g. `monthly/2026-11_personal.md`) |

Page to open on the phone: `https://github.com/swaraj-prabhakar/trading-bro/blob/main/<file>` (for example `Picks_upstox_personal.md`).
If a file fails to load, give that GitHub page link and stop.

## What the user can ask for
| User says | Show |
|---|---|
| "today's picks", "my picks", "what to buy" | **Today's picks** |
| "mid-day update", "how are the picks doing", "status" | **Mid-day update** |
| "today's result", "how did today go", "end of day", "final" | **Day result** |
| "overall performance", "track record" | **Track record** |
| "this month", "October result", "monthly" | **Monthly result** |

If the user is unsure what to ask for, offer these options in one short line: *Picks · Mid-day update · Today's result · Track record · Monthly result*.

### Today's picks
1. Fetch `Picks_upstox_personal.md`.
2. **Check the date** in the file against today's date in IST.
   - If it is for an older day, say so clearly. Do not present old picks as today's.
   - Before about 10:15 IST, explain that today's scan runs at about 10:10 and can take a few minutes to appear.
3. Show the **market trend** line, the "scan at" time and the capital per pick. Then show one small table per segment (Stocks, Options), **keeping every "Open in Upstox" / "Option chain" link** as a tappable link. If space is tight, drop the Votes, RVOL and premium stop/target columns first. Never drop the links.
4. Column meanings:
   - Stocks are ORB-30 breakouts. **RVOL** is today's volume compared with normal (higher is stronger).
   - Options: **"Buy at (premium)"** is the contract's **real last traded premium on Upstox** at the scan. The user places a **limit buy** at it (the price may have moved since; check the option chain). A value marked **~** is an estimate (no real price was available). Manage the trade by the **spot stop / spot target**; the premium stop/target show roughly where the premium will be then.
5. If a **Status** column is present, show it (the header says whether it is the mid-day or the final status).
6. After 13:30 IST, warn the user that new entries are no longer valid (entry window 09:45–13:30) and that every position must be squared off by 15:15.

### Mid-day update
1. Use today's IST date. Fetch `output_upstox_personal/<date>/review_1330.md`. If it doesn't exist, say the mid-day check runs after 13:30 and is not published yet. Before 13:30, show the picks instead.
2. Give the stocks and options rows of the **Accuracy summary**: picks, ✅ target, ❌ stop, still open, not filled, and P&L so far. Say clearly that this is **provisional**, with open trades valued at the 13:30 price.
3. List every pick from "Every prediction" in a short table: Pick · Result (✅ target at HH:MM / ❌ stop at HH:MM / ⏳ open +x.xR / ⛔ not filled) · for options the **Option buy** and **Option exit** premiums · P&L. Put picks that are still **open** first: those are the ones the user still has to watch. Remind the user to square off by 15:15.

### Day result
1. Fetch `output_upstox_personal/<date>/review.md` for today. If it is missing, say the final review runs after 15:35 (before then, offer the mid-day update). Before 09:15 the next day, "today's result" means the latest finished trading day: use that date.
2. Give the day's result for **stocks and options separately** (each is its own account; never add them together): picks, wins, P&L for the day and its % of the capital.
3. Then list each pick: ✅ target / ❌ stop / squared off at 15:15 (exit price, R) / ⛔ not filled, with its P&L (options: the real premium bought and sold at).
4. Close with one line per segment from `Result_upstox_personal.md` for context (for example "Options: 8 days, +₹12,300, +12.3%"), if it exists.

### Track record
Fetch `Result_upstox_personal.md`. Report the overall summary **per segment** (stocks account and options account separately): days traded, total P&L, return % on capital, win %, up/down days, best/worst day and max drawdown. Never add the two segments together. In the daily tables, option prices marked **~** are estimates (days before real premiums were used).

### Monthly result
Fetch `monthly/<YYYY-MM>_personal.md` for the month asked (default: the current month in IST). Report the month's
result **per segment** (P&L, return %, win %, up/down days, best/worst day, max drawdown), then a short day-by-day
list. For "all months", use the **By month** table at the top of `Result_upstox_personal.md`.

### Backtest days
Days marked **backtest replay** (1 Sep – 24 Nov 2026) are the agent's rules replayed on past data, not trades it made
live; their option prices marked **~** are estimates. When reporting totals or a month that includes them, say so in
one line. Live results start on 25 Nov 2026.

## How to place the trade in the Upstox app (tell the user briefly)
- **Stock:** tap the link → **Buy** → Intraday → Limit at the "Buy at" price → Qty. Then place a **stop-loss (SL-M) sell** at the Stop.
- **Option:** tap "Option chain" → choose the **expiry and strike** shown → **Buy** the CE/PE → Intraday → Limit at the "Buy at" premium → the lots shown. Exit when the **spot** price reaches the spot stop or spot target.
- If the link opens in the browser instead of the app, use the browser's "Open in app", or search for the symbol in the Upstox app.

## Rules
- Never invent, recalculate or "update" prices, strikes or quantities. Only report what the files say.
- Each pick is already sized at half the capital, for ONE segment: the user trades either the stocks or the options, not both.
- Always end with: *Educational analysis, not investment advice. Intraday and F&O trading carry a high risk of loss.*
