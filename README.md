# TradingBro – intraday analysis agent (NIFTY 50 stocks · Options)

Buy-first, sell-same-day analysis on **Upstox market data** (the broker's own feed). For a given capital it
returns the **top 10** trades with
entry, **stop-loss**, **target**, **quantity / lots**, and the backtested expected profit.
Ties go to the cheaper instrument; use `--max-price` (stocks) or `--max-premium` (options) to cap price.

## Claude Code skills
| Skill | Command | Covers |
|---|---|---|
| `intraday-stocks` | `python -m tradingbro.stocks --capital 50000` | NIFTY 50 cash stocks, ORB-30 + relative volume (optional `--max-price`) |
| `intraday-options` | `python -m tradingbro.options --capital 20000` | CE on up-trend / PE on down-trend, index + stock options, real Upstox premiums |
| `intraday-review` | `python -m tradingbro.review` | end-of-day check of the saved picks |

Futures are not part of this agent.

In Claude Code, open this folder and ask, e.g. *"give me intraday stock picks for ₹50,000"*
or *"which CE/PE should I buy with ₹20k today?"*. The matching skill in `.claude/skills/`
runs the scanner and explains the output.

## On your phone
- **[Picks_upstox.md](Picks_upstox.md)**: today's picks with an *Open in Upstox* link on every row. It's rewritten at about 10:10, and gets status updates at 13:30 and after 15:35 IST.
- **[Result_upstox.md](Result_upstox.md)**: the track record (by month, overall summary, then each day).
- **[monthly/](monthly/)**: one result page per month, `monthly/2026-11.md` (standard) and `monthly/2026-11_personal.md`
  (personal), rebuilt with the result pages after every final review.
- Days from **1 Sep 2026 to 24 Nov 2026** are a **backtest replay** (`python -m tradingbro.replay_days`): the same
  rules replayed on Upstox data at 10:05, each day seeing only the 60 sessions before it. They are marked
  "backtest replay" on every page. Options on contracts that have expired since use Black-Scholes premium
  estimates (marked ~), because Upstox no longer serves their candles. Live results start on 25 Nov 2026.
- **Claude app skill:** upload `claude-app-skill/tradingbro-picks.zip` once in Claude (Customize → Skills → Upload a skill). Then ask *"today's picks"*, *"mid-day update"* or *"today's result"* in the Claude phone app. It reads the **personal** pages (2 picks per segment, see below) and shows them with tappable Upstox links.

## Save picks and review them at the end of the day
Every live scan saves its picks to `output_upstox/<date>/<kind>_<HHMM>.json` (turn off with `--no-save`).
After 15:30, run the `intraday-review` skill or:
```bash
python -m tradingbro.review                    # today; add --date YYYY-MM-DD for another day
```
It checks every saved pick against the actual 1-minute prices and writes `output_upstox/<date>/review.md` with
target and stop hits, win rate, direction accuracy, R-multiples, P&L, and a breakdown by strategy agreement.
Options are checked on the contract's **real premium**: filled when it traded at or below the pick's premium
(limit buy), exit when the spot price hits the stop or target, P&L from the real premium at entry and exit.

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
Optional refinements, off by default (they protected the weak part of the study but lowered profit in a 30-day
replay): `--entry pullback` (limit buy at the opening-range high till 11:30) and `--daily-trend` (stock above its
20-day EMA).
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
Stop = 2.5 × ATR(14), target = 2R, square-off 15:15 (on the underlying's spot price).

**Premium:** the contract's **real last traded price on Upstox** at the scan, from its 1-minute candles
(`tradingbro/option_quotes.py`). Lots are sized on it, and the premium stop/target are priced from it at the spot
stop/target using its implied volatility. Only if no real price is found does it fall back to a Black-Scholes
estimate, marked `~` on the pages. (Until 26 Nov 2026 every premium was an estimate, and those were 7–55% too high.)
Each instrument is backtested on its own last ~60 sessions. Only instruments with a positive
historical edge after charges are shown, ordered by strategy agreement, then max gain.

**Loss filters** (from the same 1-year study; `--classic` turns them off): an option is only bought when the price is
already beyond the 15-minute opening range in the trade's direction **and** at least 2 of the 3 market-trend views
agree. That was the only change profitable in both periods (avg −0.06R → +0.05R older, +0.21R → +0.38R recent).
Optional, off by default (tested but not reliably better): `--rr 3` (3R target: slightly better in the study, mixed in
a 30-day replay) and `--cooldown` (skip a symbol for 5 sessions after its setup hit the stop).

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

## Personal P&L: 2 picks per segment, capital in one segment
The standard pages size **every** pick on the full capital and add all picks up. The personal pages answer
"what if I put my capital into ONE segment and take its best 2 picks":

- the 10:10 scan keeps the top **2** stocks and top 2 options;
- each pick is sized on **half the capital** (₹1,00,000 → ₹50,000 per pick; with one pick the other half stays unused);
- stocks and options are tracked as **two separate accounts**: P&L, return on capital, up/down days, best/worst
  day and drawdown per segment, never added together.

| | |
|---|---|
| Today's picks | [Picks_upstox_personal.md](Picks_upstox_personal.md) |
| Track record | [Result_upstox_personal.md](Result_upstox_personal.md) |
| Saved picks & reviews | `output_upstox_personal/` |

The workflow runs it as an extra step right after the standard scan, on the same bars (it can never block the
standard results). By hand: set `TRADINGBRO_PROFILE=personal` before any `python -m tradingbro.daily …` command.

Replay past days in either mode (writes to its own folder, never the live pages):
```bash
python -m tradingbro.replay_days --from 2026-11-03 --to 2026-11-23                       # standard -> backtest/
python -m tradingbro.replay_days --from 2026-11-03 --to 2026-11-23 --profile personal \
       --out backtest_personal                                                          # personal
```

## Schedule and on-time runs
The workflow is `TradingBro daily` ([daily_upstox.yml](.github/workflows/daily_upstox.yml)).
GitHub starts scheduled workflows whenever it has capacity – on 24 Nov 2026 they started 5–10 hours late. So the
workflow has **18 triggers a day** and each one runs `python -m tradingbro.daily auto`, which looks at the IST time
and what is already saved and does only what is due, once a day:

| Time (IST) | `auto` does |
|---|---|
| 09:45–13:30 | the **scan**, if today's scan is not saved yet (a late scan after 13:30 is skipped: entries are closed) |
| 13:30–15:35 | the **mid-day check** |
| after 15:35 | the **final review** + result pages |
| 00:00–09:00 | the **previous session's** final review, if it was missed |

Every other run prints `auto: nothing to do` and commits nothing. Manual runs: **Actions → workflow → Run workflow**
(job `auto`, or a specific job).

**For truly on-time runs (recommended):** GitHub starts *manually dispatched* runs within seconds, so let a free
external scheduler dispatch `auto` every 15 minutes:
1. GitHub → Settings → Developer settings → **Fine-grained token**: repository `trading-bro` only, permission
   **Actions: Read and write**. Copy the token.
2. [cron-job.org](https://cron-job.org) (free) → create a job:
   - URL `https://api.github.com/repos/swaraj-prabhakar/trading-bro/actions/workflows/daily_upstox.yml/dispatches`
   - Method **POST**, body `{"ref":"main","inputs":{"job":"auto"}}`
   - Headers `Authorization: Bearer <token>`, `Accept: application/vnd.github+json`
   - Schedule: every 15 minutes, 09:50–16:30, Monday–Friday, time zone **Asia/Kolkata**.
3. Keep the token only in cron-job.org (never in the repo). Extra triggers are harmless: `auto` runs each step once.

## Setup
```bash
pip install -r requirements.txt
```
Data comes from the Upstox V3 candle API: 5-minute bars of the last 60 sessions for the backtests, 1-minute bars
for the reviews and the real option premiums. It currently answers without a login. Optionally create the free
1-year read-only **Analytics Token** (Upstox developer console → Analytics tab) and add it as the repository secret
`UPSTOX_ANALYTICS_TOKEN` (locally: environment variable), so the pipeline keeps working if Upstox starts requiring auth.
(Yahoo Finance was used until 26 Nov 2026 and has been removed. Internally, instruments are still keyed by their
old ticker names, the `yahoo` field in `data/instruments.json`.)
Edit `data/instruments.json` when NSE changes the NIFTY 50 constituents or F&O lot sizes.
Tunables (stop/target, vote threshold, entry window, charges) are in `tradingbro/config.py`.

## Limitations – read before trading
- Option premiums are the **last traded price at the scan**; the live price moves and the bid-ask spread costs a
  little. Place a limit order, and manage trades by the spot stop and target. The option *backtest* filter still
  re-prices past underlying trades with Black-Scholes, so treat it as indicative.
- 60 days is a short sample, so edges are small and can disappear. Re-run `validate` regularly.
- Educational tool, **not investment advice**. Intraday and F&O trading carry a high risk of loss.

**Ordering:** picks are listed by how many of the 5 strategies agree (most first), then by max gain. Every listed pick has already passed the positive-backtest-edge filter.
