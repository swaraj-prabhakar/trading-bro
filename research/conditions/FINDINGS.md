# Market conditions – first findings (branch `market-conditions`, 26 Nov 2026)

**Question:** which conditions known by the 10:05 decision bar tell whether today suits the strategy?

**Data:** the current rules (options ranked by edge) replayed on 241 trading days, 1 Dec 2025 – 23 Nov 2026
(`python -m tradingbro.replay_days`, one scan a day at 10:05). Features come from `python -m tradingbro.conditions`,
and the dataset is `dataset.csv`. Options were traded on 105 of those days, stocks on 49.

**Labels:**
- `opt_R`: the day's average R of the option picks. It is judged on the spot price, so it is exact.
- `opt_pnl`: rupee P&L. Before late Nov 2026 it uses Black-Scholes premium estimates, so it is approximate.
- `follow`: NIFTY's move 10:05 → 15:15 in the direction of the agent's market trend.

## 1. NIFTY's afternoon direction is not predictable from these features
`follow` averages 0.00% over 206 days. No feature correlates with it by more than |0.14|, and none points the same
way in the four periods (Dec–Feb, Mar–May, Jun–Aug, Sep–Nov). So aim at "is today good for this strategy", not "where
will NIFTY go".

## 2. A rising India VIX marks weak option days, in all four periods
Each cell is the high-tercile minus the low-tercile average `opt_R`, per period.

| Feature | Dec–Feb | Mar–May | Jun–Aug | Sep–Nov |
|---|---|---|---|---|
| VIX change over 5 days | −0.34 | −0.14 | −0.35 | −0.59 |
| VIX change over 1 day | −0.35 | −0.48 | −0.84 | −0.15 |
| Share of NIFTY 50 stocks on the trade's side of VWAP | +0.67 | +0.22 | +0.08 | +0.08 |

Weaker or less consistent (3 of 4 periods):
- Where NIFTY sits in its morning range, in the trade's direction: higher is better.
- A big gap in the trade's direction: worse.
- A wide previous-day range: worse.
- A wide opening range relative to normal: worse.

## 3. Walk-forward rule test (Feb – Nov 2026, 85 option days)
Each threshold uses only the days before the month being tested.

| Rule: skip options when … | Days skipped | Their avg R | Kept avg R | Their P&L ₹ | Best-5 days skipped |
|---|---|---|---|---|---|
| (no rule) | 0 | – | +0.09 | – | – |
| VIX 5-day change in the top 20% | 15 | **−0.39** | +0.20 | −19,913 | 1 |
| VIX 5-day change in the top 33% | 26 | −0.12 | +0.19 | +46,394 | 3 |
| VIX 1-day change in the top 20% | 21 | −0.18 | +0.18 | +28,807 | 1 |
| Breadth against the trade, bottom 20% | 10 | −0.33 | +0.15 | −4,686 | 0 |

In the personal top-2 view, skipping when VIX rose over 5 days (top 20%) or over 1 day: skipped days averaged −0.28R
and kept days +0.25R.

**Caveats:**
- In R, the skipped days are consistently worse. In rupees the picture is mixed, because older option P&L uses
  estimated premiums and a few big winning days fall on rising-VIX days.
- The feature was chosen after looking at all four periods. That is mitigated by its consistency in each period and an
  intuitive reason: rising fear brings reversals that hit breakout entries. It is still a selection risk.
- Five days made most of the profit, so a skip rule must not remove them. "Top 20% of the 5-day VIX change" skipped only
  one of them.

## 4. Proposal (Phase 4, shadow mode)
Add a **Market conditions** line to the Picks pages. It flags **Caution – half size** when the 5-day VIX change is in
the top 20% of the past year (about +10.8%; 26 Nov 2026 was +13.9%) or breadth strongly opposes the trade. It changes
**no picks** for now. After 3–4 weeks of live days, compare flagged and unflagged days, then decide whether it should
cut the personal position size or skip days.

Not yet possible with free data: option-chain features (put/call ratio, OI, ATM IV). Upstox serves these live only,
with a login, so they would need recording daily from now on.
