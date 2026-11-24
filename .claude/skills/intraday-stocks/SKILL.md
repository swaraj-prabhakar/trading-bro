---
name: intraday-stocks
description: Intraday (buy first, sell same day) analysis of NIFTY 50 cash stocks using the 30-minute Opening Range Breakout with relative volume (ORB-30 + RVOL). Gives the top 10 picks with entry, stop-loss, target and how many shares to buy for the user's capital, strongest relative volume first. Use when the user asks for intraday stock picks, which NIFTY stock to buy today, target/stop-loss for a stock, or how many shares to buy with an amount.
---

# Intraday NIFTY 50 stock picks

The analysis is done by the Python engine in this repo. Do not invent prices or levels yourself. Always run the scanner and report what it prints.

## 1. Collect inputs
- **Capital (₹)**: required. If the user did not give an amount, ask for it.
- Optional: max share price (default: no limit; e.g. `--max-price 800` to prefer cheaper stocks), risk % per trade (default 2), broker intraday leverage (default 1 = own cash only), specific symbols, a past date to replay.

## 2. Run
```bash
python -m tradingbro.stocks --capital <AMOUNT>
```
Useful flags:
| Flag | Meaning |
|---|---|
| `--max-price 800` | only stocks priced ≤ ₹800 (default 0 = no limit) |
| `--risk-pct 1` | max loss per trade = 1% of capital |
| `--leverage 5` | use broker MIS leverage (more shares, more risk) |
| `--date 2026-11-20 --time 10:30` | replay a past session and show what actually happened |
| `--symbols SBIN,ITC,TMPV` | analyse only these |
| `--method ensemble` | use the original 5-strategy vote instead of ORB-30 + RVOL |
| `--entry pullback` | optional: limit buy at the opening-range high till 11:30 instead of buying at the scan price |
| `--daily-trend` | optional: also require the stock above its 20-day EMA |
| `--min-votes 4` / `--allow-short` | ensemble method only |
| `--json` | machine-readable output |

If the market is closed, the tool automatically **replays the last session** at 10:00 and adds `Actual` / `ActualRs` columns showing the real result. Tell the user this clearly: these are not picks for tomorrow. For live picks, run it during market hours after 09:45 IST.

## 3. Present the result
- Show a table with Symbol, Buy price, Stop-loss, Target, Qty, Investment, Max loss, Max gain, Expected ₹, Backtest win% / trades.
- Show each pick's **RVOL** (volume vs normal for that time of day) and the `Method backtest` note line (trades, win %, avg R, profit factor).
- Point out that each row assumes the whole capital goes into that one trade. If the user wants several picks, re-run with capital divided by the number of picks.
- If fewer than 10 picks appear, say so. Do not pad the list. ORB-30 + RVOL setups are rare (about one a day across all 50 stocks), and none appear when the market is not BULLISH.
- **Order type:** a LIMIT buy at the 'Buy at' price. With `--entry pullback` that price is the opening-range high, valid till **11:30**; it fills only if price pulls back to it, otherwise cancel it (no trade). Say this clearly.
- Remind the user: place a stop-loss order immediately after the buy fills, and square off by 15:15.

## 4. Validation
To check past days, replay them: `python -m tradingbro.stocks --capital <AMOUNT> --date YYYY-MM-DD --time 10:05`, or many days at once with `python -m tradingbro.replay_days`. (`python -m tradingbro.validate` checks the original ensemble strategies.) Report the numbers honestly, including losing days.


- Add a final **Upstox** column with each row's `upstox` link from the JSON report, as a markdown link, e.g. `[Open](https://upstox.com/...)`. It opens the stock page on Upstox, where the user can buy or sell.

## Placing the order on Upstox (optional)
After a live scan, run `python -m tradingbro.upstox orders`. It opens a local page (http://127.0.0.1:8765/) with one **Review & buy on Upstox** button per pick. Each button opens Upstox's own pre-filled confirmation screen (exact contract, qty, intraday product). The user checks it and presses *Place order* there. Nothing is placed automatically.
- The user must be logged in that day: `python -m tradingbro.upstox login` (the token expires at 03:30 IST the next day).
- First-time setup: `python -m tradingbro.upstox setup`, then put the API key and secret in `upstox_credentials.json`. Never ask the user to paste the secret into chat.
- Stocks use a LIMIT order at the scan price. Options use MARKET, which the user can change to LIMIT on the Upstox screen. The stop-loss is not sent; tell the user to place it after the buy fills.
- Run `python -m tradingbro.upstox sync-lots` now and then to refresh lot sizes from Upstox's official file.

## Market-trend filter (on by default)
Before picking anything, the scanner reads the overall market trend at the scan time from three views:
1. NIFTY's own 5-strategy intraday vote
2. Breadth: bullish vs bearish NIFTY 50 stocks
3. Yesterday's NIFTY close vs its 20-day EMA

The majority lean decides the trend: **BULLISH**, **BEARISH** or **SIDEWAYS** (a tie). Only trades in the market's direction qualify:
- **BULLISH:** buy stocks, buy CE.
- **BEARISH:** buy PE. Buy-first stock trades are skipped; suggest the options scanner (PE) instead.
- **SIDEWAYS:** no trades.

The backtest per symbol also uses this filter. Always report the `Market trend:` line, and how many signals were skipped for going against the trend. Use `--no-trend` to switch the filter off.
Backtest (60 sessions): with the filter, buy-only trades went from losing (profit factor 0.90) to slightly profitable (1.07), and CE/PE trades improved from profit factor 1.08 to 1.24.

## Method (for explaining to the user)
**ORB-30 + relative volume**, a classic intraday stock method (Toby Crabel's opening range breakout, with a
relative-volume filter as used by day-trading desks):
1. The **opening range** is the high and low between 09:15 and 09:45.
2. **Setup** when the scan bar closes above the opening-range high **and** today's volume so far is at least **1.5×**
   the stock's normal volume by that time of day (average of the previous 10 sessions), **and** the market is BULLISH.
3. **Entry**: buy at the scan price.
4. **Stop-loss** = the opening-range low. **Target** = 2 × the risk. Square off by 15:15.
5. The `ExpRs` column uses the method's own backtest over all 50 stocks at the same clock time; if that average is
   not positive after charges, no picks are shown.

Why this method: a 1-year Upstox study of 50 stocks (decision at the 10:05 bar, ~0.11% costs per trade) compared
11 well-known methods. Over the older 165 sessions every long method lost after costs, including the original
5-strategy vote (-0.18% per trade, profit factor 0.60). ORB-30 + RVOL with the stop at the opening-range low was
the only one that beat it in both periods: roughly break-even in the older period (-0.01%, PF 0.98) and
+0.32% per trade (PF 1.93) in the latest 60 sessions. Two optional refinements, `--entry pullback` (wait for a
pullback to the broken level) and `--daily-trend` (stock above its 20-day EMA), lifted the study to +0.15% (PF 1.44)
older and +0.44% (PF 2.12) recent, but cut trades to one every three sessions and lowered profit in a 30-day replay of
a strong market, so they are off by default. Others tested: ORB-15 + VWAP, previous-day-high breakout,
VWAP pullback, gap-and-go, Camarilla H4, NR7 + ORB. Be honest with the user: this is a modest edge, not a sure thing.

Always end with: educational analysis, not investment advice; intraday trading carries a high risk of loss.

**Ordering:** picks are listed by relative volume (strongest first). Every listed pick has passed the
method-backtest filter.
