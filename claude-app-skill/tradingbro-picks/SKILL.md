---
name: tradingbro-picks
description: Shows today's TradingBro intraday picks (NIFTY 50 stocks, futures and CE/PE options) with entry, stop-loss, target, quantity, max loss/gain and an "Open in Upstox" link for each, plus their live status and the overall track record. Use when the user asks for today's picks, intraday trades, what to buy today, TradingBro results, or how the picks performed.
---

# TradingBro picks (read-only, for phone use)

The analysis runs automatically on GitHub every trading day (Mon–Fri, IST):
- **10:10** scan
- **13:30** mid-day status
- **15:40** final result

This skill only **reads** the published results. It never computes picks itself.

## Sources (public; use web fetch, not code execution)
- Today's picks and their status: https://raw.githubusercontent.com/swaraj-prabhakar/trading-bro/main/Picks.md
- Track record and daily history: https://raw.githubusercontent.com/swaraj-prabhakar/trading-bro/main/Result.md
- Page to open on the phone: https://github.com/swaraj-prabhakar/trading-bro/blob/main/Picks.md

## Steps
1. Fetch `Picks.md`. If the fetch fails, give the user the GitHub page link above and stop.
2. **Check the date** in the file against today's date in IST.
   - If it's an older day, say so clearly. The scan may not have run yet (before about 10:15 IST), or today may be a holiday or weekend. Do not present old picks as today's.
   - Before about 10:15 IST, explain that today's scan runs at 10:10 and can start a few minutes late.
3. Show the **market trend** line, then the picks per segment, **keeping every "Open in Upstox" / "Option chain" link** as a tappable link. Keep tables narrow for a phone: one segment per table. If space is tight, drop the Votes column first, never the links.
4. If a **Status** column is present (after 13:30 / 15:40), show it and summarise: how many reached target, hit stop, are still open, or were not filled.
5. After 13:30 IST, warn the user that new entries are no longer valid (entry window 09:45–13:30) and that every position must be squared off by 15:15.
6. If the user asks about performance, fetch `Result.md` and report the **Overall summary** section (win %, avg R, P&L, by segment, by votes, by market trend).

## How to place the trade in the Upstox app (tell the user briefly)
- **Stock:** tap the link → **Buy** → Intraday → Limit at the "Buy at" price → Qty. Then place a **stop-loss (SL-M) sell** at the Stop.
- **Futures:** tap the link → **F&O** tab → the expiry shown → Buy → Intraday → the lots shown. Shift the stop and target by (live futures price − the shown price) if they differ.
- **Option:** tap "Option chain" → choose the **expiry and strike** shown → **Buy** the CE/PE → Intraday → the lots shown. Use the **live premium**; the shown premium is an estimate. Exit when the **spot** price reaches the spot stop or spot target.
- If the link opens in the browser instead of the app, use the browser's "Open in app", or search the symbol in the Upstox app.

## Rules
- Never invent, recalculate or "update" prices, strikes or quantities. Only report what the file says.
- Each row is sized on the full capital. If the user takes several picks, they must split the capital.
- Always end with: *Educational analysis, not investment advice. Intraday and F&O trading carry a high risk of loss.*
