---
name: intraday-review-upstox
description: End-of-day accuracy check of the predictions saved by the UPSTOX-data scanners (output_upstox/), plus the Yahoo-vs-Upstox comparison (Compare.md). Use when the user asks how the Upstox picks performed, whether Upstox-data predictions were correct, or which data source (Yahoo or Upstox) is doing better / should be kept or dropped.
---

# Intraday prediction review (Upstox data)

> **Data source: Upstox.** This is the parallel Upstox-data pipeline. It runs the same strategies as the
> default (Yahoo) skill, but on Upstox's own candle feed (no Yahoo lag; the last completed 5-minute bar).
> Everything it saves is kept apart for comparison: `output_upstox/`, `Result_upstox.md`, `Picks_upstox.md`,
> `reports/upstox/`. Always tell the user these picks come from **Upstox data**. To compare the two sources, see
> the `intraday-review-upstox` skill (`Compare.md`).
>
> No login is needed for the candle data. If `UPSTOX_ANALYTICS_TOKEN` is set (the free 1-year read-only token from
> the Upstox developer console, Analytics tab) or a daily `python -m tradingbro.upstox login` token is valid, it is
> sent as well. If the run prints `Upstox: <symbol> failed`, report which symbols had no data.

Every **live** run of `tradingbro.up stocks`, `tradingbro.up futures` or `tradingbro.up options` saves its picks to
`output_upstox/<YYYY-MM-DD>/<kind>_<HHMM>.json` (turn this off with `--no-save`). This skill checks those saved
predictions against what the market actually did.

## 1. When to run
- **After 15:30 IST** for the final result. Every trade is closed by the 15:15 square-off rule by then.
- Running earlier is allowed. The report is then marked **PROVISIONAL** and open trades are marked to the latest price. Say this clearly.
- For a past day, pass `--date YYYY-MM-DD`. 1-minute data is only available for about the last 7 days; older days fall back to 5-minute bars (see the `Data` column).

## 2. Run
```bash
python -m tradingbro.up review                    # today
python -m tradingbro.up review --date 2026-11-23  # a specific day
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
4. For options, target and stop are judged on the **spot** levels, which is exact. The ₹ P&L is an estimate.

Always show the per-pick verdict list (at least for the "first per symbol" picks), then the summary.

## 3. Present
1. **Accuracy summary**: per segment (stocks / futures / options), then overall. Show picks, targets hit, stops hit, square-offs, Win%, RightDir%, AvgR, profit factor and total P&L.
2. **By strategy agreement**: 5/5 vs 4/5 vs 3/5. This tells you whether stronger agreement predicted better.
3. **Notable picks**: biggest winner, biggest loser, and any trade that reached a high BestR but still closed at a loss (the target may be too far away).
4. **Overlap**: if the same symbol was predicted in several scans, the "first per symbol" row is the realistic one (you'd trade it once). "ALL saved predictions" counts every scan.

Definitions:
- **Win%**: P&L > 0 after charges.
- **RightDir%**: price moved the predicted way by exit time.
- **R**: result in multiples of the planned risk.
- **BestR**: the furthest the trade went in the predicted direction before exit.

Caveats to state:
- Option P&L is a Black-Scholes estimate at the exit spot price; real premiums differ. The spot verdict (target/stop/direction) is exact.
- Each pick's P&L uses the quantity from its own scan, sized on the full capital. The total is the sum of all picks, not what one account could hold at the same time.
- One day is a tiny sample. Suggest comparing reviews over many days before trusting the strategy.

## Yahoo vs Upstox comparison
Both pipelines run on the same schedule (scan 10:10 IST; final review 15:40 Yahoo, 15:55 Upstox). To compare them:
```bash
python -m tradingbro.compare        # rebuilds Compare.md from output/ and output_upstox/
```
`Compare.md` only uses days that have a final review from **both** sources. Present:
1. The **Overall, by segment** table: Yahoo vs Upstox rows side by side (win %, avg R, profit factor, total P&L).
2. **Day by day**: which source did better each day, and the better-day count.
3. **Same picks or different?**: how many picks both sources made, and how the picks only one source made performed.
   This is where the data difference shows up.

Advice on choosing which to keep: wait for at least 10 common trading days. Prefer the source with the higher
profit factor and average R across segments, not just the larger total P&L (a few big option trades can dominate).
If the numbers are close, prefer Upstox: it is the broker's own feed with no delay, and the orders are placed there.

End with: educational analysis, not investment advice.
