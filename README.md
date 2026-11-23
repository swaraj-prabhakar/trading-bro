# TradingBro – intraday analysis agent (NIFTY 50 · Futures · Options)

Buy-first, sell-same-day analysis. For a given capital it returns the **top 10** trades with
entry, **stop-loss**, **target**, **quantity / lots**, and the backtested expected profit.
Ties go to the cheaper instrument; use `--max-price` (stocks) or `--max-premium` (options) to cap price.

## Three separate Claude Code skills
| Skill | Command | Covers |
|---|---|---|
| `intraday-stocks` | `python -m tradingbro.stocks --capital 50000` | NIFTY 50 cash stocks (optional `--max-price`) |
| `intraday-futures` | `python -m tradingbro.futures --capital 300000` | NIFTY 50 stock futures + NIFTY/BANKNIFTY futures |
| `intraday-options` | `python -m tradingbro.options --capital 20000` | CE on up-trend / PE on down-trend, index + stock options |

In Claude Code, open this folder and ask, e.g. *"give me intraday stock picks for ₹50,000"*
or *"which CE/PE should I buy with ₹20k today?"*. The matching skill in `.claude/skills/`
runs the scanner and explains the output.

## Save picks and review them at the end of the day
Every live scan saves its picks to `output/<date>/<kind>_<HHMM>.json` (turn off with `--no-save`).
After 15:30, run the `intraday-review` skill or:
```bash
python -m tradingbro.review                    # today; add --date YYYY-MM-DD for another day
```
It checks every saved pick against the actual 1-minute prices and writes `output/<date>/review.md` with
target and stop hits, win rate, direction accuracy, R-multiples, P&L, and a breakdown by strategy agreement.

## Upstox: one-click review and place
```bash
python -m tradingbro.upstox setup       # once: creates upstox_credentials.json (put the API key and secret in it)
python -m tradingbro.upstox login       # once a day
python -m tradingbro.upstox orders      # Review & place page for the latest saved picks
python -m tradingbro.upstox sync-lots   # refresh F&O lot sizes from Upstox's official instruments file
```
The app's redirect URL must be `http://127.0.0.1:8765/callback`. Orders are only ever placed by you, on Upstox's confirmation screen.

## Method (popular intraday strategies, 5-minute bars)
1. VWAP + EMA 9/21 trend
2. Opening Range Breakout (first 15 min)
3. Supertrend (10, 3)
4. RSI(14) + MACD momentum
5. CPR (previous-day Central Pivot Range)

A signal needs at least 3 of the 5 strategies to agree, inside 09:45–13:30.
Stop = 2.5 × ATR(14), target = 2R, square-off 15:15.
Each instrument is backtested on its own last ~60 sessions. Only instruments with a positive
historical edge after charges are shown, ordered by strategy agreement, then max gain.

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

## Validate on past days
```bash
python -m tradingbro.validate                 # per-strategy backtest + 10-day walk-forward (long only)
python -m tradingbro.validate --allow-short   # include bearish trades (what PE options use)
python -m tradingbro.stocks --capital 50000 --date 2026-11-20 --time 10:30   # replay one day
python -m pytest -q                           # offline unit tests (incl. no-lookahead check)
```
Outside market hours, every scanner automatically replays the last session and shows the
**actual** outcome, so each run is also a test.

## Setup
```bash
pip install -r requirements.txt
```
Data comes from Yahoo Finance: 5-minute bars, last 60 days, which can lag live by a few minutes.
Edit `data/instruments.json` when NSE changes the NIFTY 50 constituents or F&O lot sizes.
Tunables (stop/target, vote threshold, entry window, charges) are in `tradingbro/config.py`.

## Limitations – read before trading
- Option premiums are **Black-Scholes estimates**, not live quotes. Use the live option chain
  and manage trades by the spot stop and target.
- Futures prices are spot + estimated carry, and margins are estimates.
- 60 days is a short sample, so edges are small and can disappear. Re-run `validate` regularly.
- Educational tool, **not investment advice**. Intraday and F&O trading carry a high risk of loss.

**Ordering:** picks are listed by how many of the 5 strategies agree (most first), then by max gain. Every listed pick has already passed the positive-backtest-edge filter.
