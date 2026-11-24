---
name: intraday-futures-upstox
description: Intraday NIFTY 50 stock futures and NIFTY/BANKNIFTY index futures computed on UPSTOX market data (the parallel Upstox pipeline, run alongside the default Yahoo one for comparison). Top 10 trades with entry, stop-loss, target, lots and margin for the user's capital. Use when the user asks for futures picks using Upstox data, real-time/live Upstox data, or the Upstox version of the futures scan.
---

# Intraday futures picks (NIFTY 50 stocks + index futures) (Upstox data)

> **Data source: Upstox.** This is the parallel Upstox-data pipeline. It runs the same strategies as the
> default (Yahoo) skill, but on Upstox's own candle feed (no Yahoo lag; the last completed 5-minute bar).
> Everything it saves is kept apart for comparison: `output_upstox/`, `Result_upstox.md`, `Picks_upstox.md`,
> `reports/upstox/`. Always tell the user these picks come from **Upstox data**. To compare the two sources, see
> the `intraday-review-upstox` skill (`Compare.md`).
>
> No login is needed for the candle data. If `UPSTOX_ANALYTICS_TOKEN` is set (the free 1-year read-only token from
> the Upstox developer console, Analytics tab) or a daily `python -m tradingbro.upstox login` token is valid, it is
> sent as well. If the run prints `Upstox: <symbol> failed`, report which symbols had no data.

Run the engine and report its output. Never make up levels.

## 1. Inputs
- **Capital (₹)**: required. Ask for it if missing. Futures need margin per lot (often ₹1–3 lakh for stocks, about ₹1.5 lakh+ for NIFTY), so small amounts may show no affordable contract. Say that plainly and suggest the `intraday-stocks` or `intraday-options` skill instead.
- Optional: risk % per trade (default 2), symbols, past date to replay.

## 2. Run
```bash
python -m tradingbro.up futures --capital <AMOUNT>
```
Flags: `--risk-pct`, `--symbols NIFTY,BANKNIFTY,SBIN`, `--date YYYY-MM-DD --time HH:MM` (replay), `--min-votes`, `--rr`, `--sl-atr`, `--allow-short` (sell-first trades; the default is buy-first only), `--json`.

When the market is closed the tool replays the last session at 10:00 and shows the actual result. Make it clear these are not forward picks.

## 3. Present
Table: Contract (symbol + expiry), Buy price (futures estimate), Stop, Target, Lot size, Lots, Margin used, Max loss, Risk % of capital, Expected ₹, Backtest win% / trades.

Key caveats to state:
- Futures prices shown are **spot + estimated carry**. The user should take the live futures quote and shift stop and target by the same difference (live futures − spot shown).
- Margin is an estimate (`margin_pct` in `data/instruments.json`). The broker's SPAN margin is what counts.
- One lot can risk more than the chosen risk %. The `Risk%` column shows the real exposure. Flag any row above the user's risk budget.
- Lot sizes in `data/instruments.json` must match NSE's current list. Remind the user to verify, because NSE revises them periodically.


- Add a final **Upstox** column with each row's `upstox` link from the JSON report, as a markdown link, e.g. `[Open](https://upstox.com/...)`. It opens the underlying's Upstox page; the user opens the Futures (F&O) tab there and picks the expiry shown.

## Placing the order on Upstox (optional)
After a live scan, run `python -m tradingbro.up orders`. It opens a local page (http://127.0.0.1:8765/) with one **Review & buy on Upstox** button per pick. Each button opens Upstox's own pre-filled confirmation screen (exact contract, qty, intraday product). The user checks it and presses *Place order* there. Nothing is placed automatically.
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
Backtest on Yahoo data (60 sessions): with the filter, buy-only trades went from losing (profit factor 0.90) to slightly profitable (1.07), and CE/PE trades improved from profit factor 1.08 to 1.24.

## Method
Same 5-strategy ensemble as the stocks skill (VWAP+EMA, ORB, Supertrend, RSI+MACD, CPR) on the underlying's 5-minute chart. Futures track spot closely intraday. A contract qualifies only if its backtested average R-multiple × today's lot-based risk, minus futures charges (STT, exchange, stamp, GST), is positive; qualifiers are ordered by strategy agreement, then max gain. Square off by 15:15.

Validation: `python -m tradingbro.up validate` (add `--allow-short` if short trades are in use).

End with: not investment advice; leveraged futures can lose more than the margin.

**Ordering:** picks are listed by how many of the 5 strategies agree (most first), then by max gain. Every listed pick has already passed the positive-backtest-edge filter.
