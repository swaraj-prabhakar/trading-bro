---
name: intraday-options
description: Intraday option-buying analysis - picks CE (call) in an up-trend or PE (put) in a down-trend on NIFTY, BANKNIFTY and NIFTY 50 stock options. Gives the top 10 cheaper contracts with strike, expiry, estimated premium, premium stop/target, underlying stop/target, lots for the user's capital and backtested expected profit. Use when the user asks for intraday options, CE/PE picks, which strike to buy, or option trades for a given amount.
---

# Intraday options (buy CE / PE, exit same day)

Run the engine and report its output. Never make up premiums or strikes.

## 1. Inputs
- **Capital (₹)**: required. Ask if missing.
- Optional: `--otm 1` (one strike out-of-the-money, which is cheaper but has a lower win rate), `--max-premium` (₹ per unit cap, so cheaper options are preferred), risk %, symbols, past date to replay.

## 2. Run
```bash
python -m tradingbro.options --capital <AMOUNT>
```
Flags: `--otm 0|1|2`, `--max-premium 150`, `--risk-pct`, `--symbols NIFTY,BANKNIFTY,SBIN`, `--date YYYY-MM-DD --time HH:MM`, `--min-votes`, `--rr`, `--sl-atr`, `--json`.

Bullish signal → **buy CE**. Bearish signal → **buy PE**. Both are buy-first trades.
When the market is closed, the tool replays the last session and shows the estimated actual P&L.

## 3. Present
Table: Option (symbol expiry strike CE/PE), Spot, Estimated premium, Premium SL, Premium target, **Spot SL / Spot target**, Lot, Lots, Investment, Max loss, Expected ₹, Backtest win% / avg option return %.

Must-say caveats:
- Premiums are **Black-Scholes estimates** (IV from India VIX for NIFTY, 1.1 × 20-day historical volatility otherwise), because free historical option data is not available. Tell the user to open the live option chain, use the real premium, and manage the trade using the **spot** stop and target: exit the option when spot hits either level.
- Check the strike and expiry exist. Expiries assume NSE Tuesday expiries (NIFTY weekly; BANKNIFTY and stocks monthly) with no holiday shift.
- Option backtests ignore IV changes and bid-ask spread, so treat them as indicative only.
- Expiry-day options decay very fast.


- Add a final **Upstox** column with each row's `upstox` link from the JSON report, as a markdown link, e.g. `[Open](https://upstox.com/...)`. It opens the Upstox option chain for that underlying; the user selects the expiry and strike shown (CE or PE).

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

## Loss filters (on by default)
A 1-year Upstox study (165 older + 60 recent sessions, all NIFTY 50 stocks and both indices) showed the original
rules lost money in the older period (avg -0.06R per trade). Two extra conditions were the only change that was
profitable in **both** periods (avg R -0.06 → +0.05 and +0.21 → +0.38; about 3 candidates a day remain):
1. **Opening range agrees**: price is already beyond the 15-minute opening range in the trade's direction
   (above its high for CE, below its low for PE).
2. **Strong market**: at least **2 of the 3** market-trend views agree (market score ≥ 2/3), not just a lean.

The scanner prints how many signals each filter skipped (`Loss filters:` note). Report it. `--classic` switches both
off (the original rules). Things that did **not** help in the study: breakeven stops, scanning later (10:30/11:00),
avoiding stretched prices, time stops, wider/tighter stops, a 1.5R target.
Losses are not eliminated: in the study about half the months still had a negative average. Keep the 2% risk per
trade and the 15:15 square-off.

## Method
Direction comes from the 5-strategy ensemble on the underlying's 5-minute chart (VWAP+EMA, ORB, Supertrend, RSI+MACD, CPR). Each historical underlying trade is re-priced as the corresponding CE/PE to measure the option strategy's average return. Only contracts with a positive expected ₹ profit after option charges qualify; they are then ordered by strategy agreement, then max gain.

Validation: `python -m tradingbro.validate --allow-short`.

End with: not investment advice; most option buyers lose money and premiums can go to zero.

**Ordering:** picks are listed by how many of the 5 strategies agree (most first), then by max gain. Every listed pick has already passed the positive-backtest-edge filter and the loss filters.
