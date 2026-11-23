---
name: intraday-stocks
description: Intraday (buy first, sell same day) analysis of NIFTY 50 cash stocks. Gives the top 10 picks with entry, stop-loss, target and how many shares to buy for the user's capital, ordered by strategy agreement then max gain. Use when the user asks for intraday stock picks, which NIFTY stock to buy today, target/stop-loss for a stock, or how many shares to buy with an amount.
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
| `--min-votes 4` | stricter: 4 of 5 strategies must agree |
| `--allow-short` | also show sell-first setups (the user's default is buy-first only) |
| `--json` | machine-readable output |

If the market is closed, the tool automatically **replays the last session** at 10:00 and adds `Actual` / `ActualRs` columns showing the real result. Tell the user this clearly: these are not picks for tomorrow. For live picks, run it during market hours after 09:45 IST.

## 3. Present the result
- Show a table with Symbol, Buy price, Stop-loss, Target, Qty, Investment, Max loss, Max gain, Expected ₹, Backtest win% / trades.
- Mention which strategies agreed (the `strategies` field in the JSON report saved under `reports/`).
- Point out that each row assumes the whole capital goes into that one trade. If the user wants several picks, re-run with capital divided by the number of picks.
- If fewer than 10 picks appear, say so. Do not pad the list. Only stocks with a live signal **and** a positive backtested edge qualify.
- Remind the user: place a stop-loss order immediately after buying, and square off by 15:15.

## 4. Validation
To check how the methods performed on past days, run `python -m tradingbro.validate` (per-strategy backtest plus a day-by-day walk-forward of the full agent). Report the numbers honestly, including losing days.


- Add a final **Upstox** column with each row's `upstox` link from the JSON report, as a markdown link, e.g. `[Open](https://upstox.com/...)`. It opens the stock page on Upstox, where the user can buy or sell.

## Placing the order on Upstox (optional)
After a live scan, run `python -m tradingbro.upstox orders`. It opens a local page (http://127.0.0.1:8765/) with one **Review & buy on Upstox** button per pick. Each button opens Upstox's own pre-filled confirmation screen (exact contract, qty, intraday product). The user checks it and presses *Place order* there. Nothing is placed automatically.
- The user must be logged in that day: `python -m tradingbro.upstox login` (the token expires at 03:30 IST the next day).
- First-time setup: `python -m tradingbro.upstox setup`, then put the API key and secret in `upstox_credentials.json`. Never ask the user to paste the secret into chat.
- Stocks use a LIMIT order at the scan price. Futures and options use MARKET, which the user can change to LIMIT on the Upstox screen. The stop-loss is not sent; tell the user to place it after the buy fills.
- Run `python -m tradingbro.upstox sync-lots` now and then to refresh lot sizes from Upstox's official file.

## Market-trend filter (on by default)
Before picking anything, the scanner reads the overall market trend at the scan time from three views:
1. NIFTY's own 5-strategy intraday vote
2. Breadth: bullish vs bearish NIFTY 50 stocks
3. Yesterday's NIFTY close vs its 20-day EMA

The majority lean decides the trend: **BULLISH**, **BEARISH** or **SIDEWAYS** (a tie). Only trades in the market's direction qualify:
- **BULLISH:** buy stocks or futures, buy CE.
- **BEARISH:** buy PE. Buy-first stock and futures trades are skipped; suggest the options scanner (PE) instead.
- **SIDEWAYS:** no trades.

The backtest per symbol also uses this filter. Always report the `Market trend:` line, and how many signals were skipped for going against the trend. Use `--no-trend` to switch the filter off.
Backtest (60 sessions): with the filter, buy-only trades went from losing (profit factor 0.90) to slightly profitable (1.07), and CE/PE trades improved from profit factor 1.08 to 1.24.

## Method (for explaining to the user)
Five popular intraday strategies run on 5-minute bars, and each one votes bullish or bearish:
1. **VWAP + EMA(9/21)** trend
2. **Opening Range Breakout** (first 15 minutes)
3. **Supertrend (10,3)**
4. **RSI(14) + MACD** momentum
5. **CPR** (previous-day Central Pivot Range) breakout

A trade needs at least 3 of the 5 votes (configurable). Stop = 2.5 × ATR(14) and target = 2 × the stop distance (configurable in `tradingbro/config.py`). A stock qualifies only if its own backtested average R-multiple over the last ~60 sessions, converted to ₹ for the user's position size after charges, is positive; qualifiers are ordered by strategy agreement, then max gain.

Always end with: educational analysis, not investment advice; intraday trading carries a high risk of loss.

**Ordering:** picks are listed by how many of the 5 strategies agree (most first), then by max gain. Every listed pick has already passed the positive-backtest-edge filter.
