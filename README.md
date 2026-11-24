# TradingBro – intraday analysis agent (NIFTY 50 stocks · Options)

Buy-first, sell-same-day analysis. For a given capital it returns the **top 10** trades with
entry, **stop-loss**, **target**, **quantity / lots**, and the backtested expected profit.
Ties go to the cheaper instrument; use `--max-price` (stocks) or `--max-premium` (options) to cap price.

## Claude Code skills
| Skill | Command | Covers |
|---|---|---|
| `intraday-stocks` | `python -m tradingbro.stocks --capital 50000` | NIFTY 50 cash stocks, ORB-30 + relative volume (optional `--max-price`) |
| `intraday-options` | `python -m tradingbro.options --capital 20000` | CE on up-trend / PE on down-trend, index + stock options |

Futures are not part of this agent.

In Claude Code, open this folder and ask, e.g. *"give me intraday stock picks for ₹50,000"*
or *"which CE/PE should I buy with ₹20k today?"*. The matching skill in `.claude/skills/`
runs the scanner and explains the output.

## On your phone
- **[Picks.md](Picks.md)**: today's picks with an *Open in Upstox* link on every row. It's rewritten at 10:10, and gets status updates at 13:30 and 15:40 IST.
- **[Result.md](Result.md)**: the track record (overall summary first, then each day).
- **Claude app skill:** upload `claude-app-skill/tradingbro-picks.zip` once in Claude (Customize → Skills → Upload a skill). Then ask *"today's picks"* in the Claude phone app. It reads Picks.md and shows the table with tappable Upstox links.

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
python -m tradingbro.upstox sync-lots   # refresh option lot sizes from Upstox's official instruments file
```
The app's redirect URL must be `http://127.0.0.1:8765/callback`. Orders are only ever placed by you, on Upstox's confirmation screen.

## Method – stocks: ORB-30 + relative volume
Buy when the scan bar closes above the 09:15–09:45 high, today's volume so far is ≥ 1.5× normal for that time of day,
and the market is BULLISH. Stop = opening-range low, target = 2R, square-off 15:15 (`tradingbro/stock_orb.py`).
In a 1-year Upstox study of 50 stocks it was the only one of 11 well-known methods that beat the original ensemble in
both the older 165 sessions (≈ break-even after costs vs −0.18%/trade) and the latest 60 (+0.32%/trade, PF 1.93).
`--method ensemble` brings back the original vote for stocks.

## Method – options: 5-strategy ensemble + loss filters (5-minute bars)
1. VWAP + EMA 9/21 trend
2. Opening Range Breakout (first 15 min)
3. Supertrend (10, 3)
4. RSI(14) + MACD momentum
5. CPR (previous-day Central Pivot Range)

A signal needs at least 3 of the 5 strategies to agree, inside 09:45–13:30.
Stop = 2.5 × ATR(14), target = 2R, square-off 15:15.
Each instrument is backtested on its own last ~60 sessions. Only instruments with a positive
historical edge after charges are shown, ordered by strategy agreement, then max gain.

**Loss filters** (from the same 1-year study; `--classic` turns them off): an option is only bought when the price is
already beyond the 15-minute opening range in the trade's direction **and** at least 2 of the 3 market-trend views
agree. That was the only change profitable in both periods (avg −0.06R → +0.05R older, +0.21R → +0.38R recent).

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

## Validate on past days
```bash
python -m tradingbro.validate                 # per-strategy backtest + 10-day walk-forward (long only)
python -m tradingbro.validate --allow-short   # include bearish trades (what PE options use)
python -m tradingbro.stocks --capital 50000 --date 2026-11-20 --time 10:30   # replay one day
python -m pytest -q                           # offline unit tests (incl. no-lookahead check)
```
Outside market hours, every scanner automatically replays the last session and shows the
**actual** outcome, so each run is also a test.

## Trial: Upstox data vs Yahoo data (side by side)
A second, separate pipeline runs the **same strategies on Upstox's own candle feed** (no Yahoo lag).
It is a trial: after 1–2 weeks, compare the two and keep the better one.

| | Yahoo (original) | Upstox (trial) |
|---|---|---|
| Run a scanner | `python -m tradingbro.stocks …` | `python -m tradingbro.up stocks …` (also `options`, `review`, `validate`, `orders`) |
| Claude Code skills | `intraday-stocks/-options/-review` | `intraday-stocks-upstox`, `-options-upstox`, `-review-upstox` |
| GitHub workflow | `TradingBro daily` ([daily.yml](.github/workflows/daily.yml)) | `TradingBro daily (Upstox data)` ([daily_upstox.yml](.github/workflows/daily_upstox.yml)) |
| Saved picks & reviews | `output/` | `output_upstox/` |
| Results / phone page | [Result.md](Result.md), [Picks.md](Picks.md) | [Result_upstox.md](Result_upstox.md), [Picks_upstox.md](Picks_upstox.md) |

**Comparison:** [Compare.md](Compare.md) is rebuilt by the Upstox workflow after each final review
(15:55 IST), or by hand with `python -m tradingbro.compare`. It only counts days where both pipelines have a
final review, and shows per-segment win %, avg R, profit factor and P&L, a day-by-day winner, and how the picks
that only one source made turned out.

Notes:
- Both scans run at 10:10 IST and both use the last 60 sessions of 5-minute history, so the comparison is fair.
- The Upstox candle API currently answers without a login. Optionally create the free 1-year read-only
  **Analytics Token** (Upstox developer console → Analytics tab) and add it as the repository secret
  `UPSTOX_ANALYTICS_TOKEN` (locally: environment variable). Then the pipeline keeps working if Upstox starts requiring auth.
- Under the hood it is one switch, `TRADINGBRO_SOURCE=upstox` (`tradingbro/config.py`); `tradingbro.up` just sets it.
  Dropping either pipeline later means deleting its workflow, skills and output folder.

## Personal P&L: 2 picks per segment, capital in one segment
The standard pages size **every** pick on the full capital and add all picks up. The personal pages answer
"what if I put my capital into ONE segment and take its best 2 picks":

- the 10:10 scan keeps the top **2** stocks and top 2 options;
- each pick is sized on **half the capital** (₹1,00,000 → ₹50,000 per pick; with one pick the other half stays unused);
- stocks and options are tracked as **two separate accounts**: P&L, return on capital, up/down days, best/worst
  day and drawdown per segment, never added together.

| | Yahoo | Upstox |
|---|---|---|
| Today's picks | [Picks_personal.md](Picks_personal.md) | [Picks_upstox_personal.md](Picks_upstox_personal.md) |
| Track record | [Result_personal.md](Result_personal.md) | [Result_upstox_personal.md](Result_upstox_personal.md) |
| Saved picks & reviews | `output_personal/` | `output_upstox_personal/` |

Comparison: [Compare_personal.md](Compare_personal.md). Both workflows run it as an extra step right after the standard
scan, on the same bars (it can never block the standard results). By hand: set `TRADINGBRO_PROFILE=personal` before any
`python -m tradingbro.daily …` / `python -m tradingbro.up daily …` command.

Replay past days in either mode (writes to its own folder, never the live pages):
```bash
python -m tradingbro.replay_days --from 2026-11-03 --to 2026-11-23                       # standard -> backtest/
python -m tradingbro.replay_days --from 2026-11-03 --to 2026-11-23 --profile personal \
       --out backtest_personal                                                          # personal
```

## Setup
```bash
pip install -r requirements.txt
```
Data comes from Yahoo Finance: 5-minute bars, last 60 days, which can lag live by a few minutes
(or from Upstox in the trial pipeline above).
Edit `data/instruments.json` when NSE changes the NIFTY 50 constituents or F&O lot sizes.
Tunables (stop/target, vote threshold, entry window, charges) are in `tradingbro/config.py`.

## Limitations – read before trading
- Option premiums are **Black-Scholes estimates**, not live quotes. Use the live option chain
  and manage trades by the spot stop and target.
- 60 days is a short sample, so edges are small and can disappear. Re-run `validate` regularly.
- Educational tool, **not investment advice**. Intraday and F&O trading carry a high risk of loss.

**Ordering:** picks are listed by how many of the 5 strategies agree (most first), then by max gain. Every listed pick has already passed the positive-backtest-edge filter.
