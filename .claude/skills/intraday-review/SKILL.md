---
name: intraday-review
description: End-of-day accuracy check of the intraday predictions saved by the stocks and options scanners (output_upstox/). Compares each saved pick with the actual prices that day (options with the contract's real premium) and produces an accuracy summary (target/stop hits, win rate, direction accuracy, R-multiples, P&L) overall, per segment and by strategy agreement. Use when the user asks whether today's (or a past day's) predictions were correct, for an accuracy report, or for a review of saved picks.
---

# Intraday prediction review

> **Data: Upstox** (the broker's own candle feed; the last completed 5-minute bar). Saved picks and reviews go to
> `output_upstox/`, results to `Result_upstox.md` / `Picks_upstox.md`, reports to `reports/upstox/`.
> No login is needed for the candle data. If `UPSTOX_ANALYTICS_TOKEN` is set (the free 1-year read-only token from
> the Upstox developer console, Analytics tab) or a daily `python -m tradingbro.upstox login` token is valid, it is
> sent as well. If the run prints `Upstox: <symbol> failed`, report which symbols had no data.

Every **live** run of `tradingbro.stocks` or `tradingbro.options` saves its picks to
`output_upstox/<YYYY-MM-DD>/<kind>_<HHMM>.json` (turn this off with `--no-save`). This skill checks those saved
predictions against what the market actually did.

## 1. When to run
- **After 15:30 IST** for the final result. Every trade is closed by the 15:15 square-off rule by then.
- Running earlier is allowed. The report is then marked **PROVISIONAL** and open trades are marked to the latest price. Say this clearly.
- For a past day, pass `--date YYYY-MM-DD`. 1-minute data is only available for about the last 7 days; older days fall back to 5-minute bars (see the `Data` column).

## 2. Run
```bash
python -m tradingbro.review                    # today
python -m tradingbro.review --date 2026-11-23  # a specific day
```
It writes `output_upstox/<date>/review.md` and `review.json` next to the saved predictions.

## How each prediction is checked ("if the order was placed")
1. **Fill check:** the order counts as placed only if, after the signal bar closed, the price actually traded back to the entry level (buy: low <= entry; sell: high >= entry) before 13:30. If it never did, the pick is **NOT FILLED** and excluded from win/loss stats.
2. **From the fill onwards,** each 1-minute bar is checked: did the price touch the **stop-loss** or the **target** first? If both fall inside the same bar, the stop is assumed first (conservative).
3. **Verdict per pick** (column "Reached target or stop?"):
   - `YES - reached TARGET at HH:MM`
   - `NO - hit STOP LOSS at HH:MM`
   - `NEITHER - closed 15:15 at ±xR` (squared off before either level)
   - `PENDING` (review run before the close)
   - `NOT FILLED`
4. **Options** use the contract's real Upstox premium (1-minute candles): the order counts as filled when the premium
   traded at or below the pick's premium (limit buy) before 13:30; target and stop are then judged on the **spot**
   levels; the ₹ P&L is the real premium at exit minus the real fill premium (a Black-Scholes estimate only when
   no candles exist). The `Option buy` / `Option exit`
   columns show those premiums.

Always show the per-pick verdict list (at least for the "first per symbol" picks), then the summary.

## 3. Present
1. **Accuracy summary**: per segment (stocks / options), then overall. Show picks, targets hit, stops hit, square-offs, Win%, RightDir%, AvgR, profit factor and total P&L.
2. **By strategy agreement**: 5/5 vs 4/5 vs 3/5. This tells you whether stronger agreement predicted better.
3. **Notable picks**: biggest winner, biggest loser, and any trade that reached a high BestR but still closed at a loss (the target may be too far away).
4. **Overlap**: if the same symbol was predicted in several scans, the "first per symbol" row is the realistic one (you'd trade it once). "ALL saved predictions" counts every scan.

Definitions:
- **Win%**: P&L > 0 after charges.
- **RightDir%**: price moved the predicted way by exit time.
- **R**: result in multiples of the planned risk.
- **BestR**: the furthest the trade went in the predicted direction before exit.

Caveats to state:
- Option P&L uses real traded premiums (1-minute closes), so actual fills can differ by the bid-ask spread.
- Each pick's P&L uses the quantity from its own scan, sized on the full capital. The total is the sum of all picks, not what one account could hold at the same time.
- One day is a tiny sample. Suggest comparing reviews over many days before trusting the strategy.

End with: educational analysis, not investment advice.
