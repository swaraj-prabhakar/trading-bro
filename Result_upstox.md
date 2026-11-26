# TradingBro – intraday prediction results (Upstox data)

_Updated 2026-11-26 16:41 IST · scans at 10:10 IST, final review after 15:35 IST (Mon–Fri) · capital ₹100,000 per pick._

> **56 day(s) 2026-09-01 → 2026-11-23 are a BACKTEST REPLAY**: the agent's rules replayed on past Upstox data at 10:05 (one scan a day, graded on 5-minute bars), not trades it made live. Options on contracts that have since expired use Black-Scholes premium estimates (marked ~). 2 live day(s) 2026-11-25 → 2026-11-26.

> Educational tool, not investment advice. Backtests on ~60 days of data do not guarantee future results. Intraday F&O trading is high-risk; most retail traders lose money.

## By month

| Month | Days | Picks | Win % | Avg R | Profit factor | Total P&L ₹ | Details |
|---|---|---|---|---|---|---|---|
| November 2026 | 17 | 136 | 54 | 0.25 | 1.51 | 81,732 | [2026-11](monthly/2026-11.md) |
| October 2026 | 20 | 77 | 64 | 0.48 | 3.97 | 89,484 | [2026-10](monthly/2026-10.md) |
| September 2026 | 21 | 48 | 48 | 0.10 | 1.27 | 10,172 | [2026-09](monthly/2026-09.md) |

## Overall summary

**58 trading day(s)** · 2026-09-01 → 2026-11-26 · 261 picks · 261 filled

| Group | Picks | Not filled | ✅ Target | ❌ Stop | ➖ 15:15 close | Win % | Avg R | Profit factor | Total P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|
| All picks | 261 | 0 | 52 | 76 | 133 | 56 | 0.29 | 1.79 | 181,389 |
| Stocks | 68 | 0 | 3 | 4 | 61 | 59 | 0.15 | 1.47 | 10,064 |
| Options | 193 | 0 | 49 | 72 | 72 | 54 | 0.34 | 1.83 | 171,325 |

**By strategy agreement**

| Group | Picks | Not filled | ✅ Target | ❌ Stop | ➖ 15:15 close | Win % | Avg R | Profit factor | Total P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|
| Votes ORB-30 + RVOL | 68 | 0 | 3 | 4 | 61 | 59 | 0.15 | 1.47 | 10,064 |
| Votes 5/5 | 178 | 0 | 43 | 67 | 68 | 54 | 0.31 | 1.81 | 156,298 |
| Votes 4/5 | 10 | 0 | 3 | 4 | 3 | 60 | 0.50 | 1.45 | 5,273 |
| Votes 3/5 | 5 | 0 | 3 | 1 | 1 | 60 | 0.98 | 4.25 | 9,753 |

**By market trend at scan time**

| Group | Picks | Not filled | ✅ Target | ❌ Stop | ➖ 15:15 close | Win % | Avg R | Profit factor | Total P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|
| BEARISH | 81 | 0 | 25 | 24 | 32 | 58 | 0.50 | 2.93 | 99,675 |
| BULLISH | 180 | 0 | 27 | 52 | 101 | 54 | 0.19 | 1.46 | 81,713 |

_Win % = P&L > 0 after charges (filled picks). R = result in multiples of the planned risk. Each pick is sized on the full capital, so totals are a sum of independent trades. Option P&L uses the contract's real Upstox premium (~ = Black-Scholes estimate where no real price exists); target/stop verdicts use exact spot prices. A pick is "not filled" if price never traded back to the entry before 13:30._

## Daily results

### 2026-11-26 · market BULLISH

9 picks · ✅ 1 target · ❌ 4 stop · ➖ 4 closed 15:15 · ⛔ 0 not filled · win 33% · avg -0.11R · P&L ₹-6,653

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| HDFCLIFE BUY | 10:05 | 607.60 | 599.00 | 624.80 | ❌ NO - hit STOP LOSS at 11:46 | -1.00 | -1,493 |
| BEL BUY | 10:05 | 408.75 | 403.05 | 420.15 | ➖ NEITHER - closed 15:15 at -0.57R | -0.57 | -875 |
| CIPLA BUY | 10:05 | 1,450.00 | 1,427.70 | 1,494.60 | ➖ NEITHER - closed 15:15 at -0.20R | -0.20 | -388 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HDFCLIFE 29Dec 610 CE | 10:05 | 5/5 | 26.8~ | 20.8 | 23.9~ | 33.3~ | 17.5 | 607.60 | 601.84 | 619.13 | ❌ NO - hit STOP LOSS at 10:37 | -1.00 | -3,747 |
| SUNPHARMA 29Dec 1920 CE | 10:05 | 5/5 | 55.1~ | 48.1 | 48.7~ | 69.2~ | 42.4 | 1,917.80 | 1,905.61 | 1,942.19 | ❌ NO - hit STOP LOSS at 13:56 | -1.00 | -2,105 |
| HDFCBANK 29Dec 860 CE | 10:05 | 5/5 | 33.3~ | 26.1 | 29.9~ | 40.7~ | 32.7 | 856.75 | 850.14 | 869.98 | ✅ YES - reached TARGET at 10:51 | 2.00 | 4,224 |
| BEL 29Dec 410 CE | 10:05 | 5/5 | 13.7~ | 12.6 | 12.1~ | 17.0~ | 10.8 | 408.75 | 405.77 | 414.71 | ❌ NO - hit STOP LOSS at 11:17 | -1.00 | -2,658 |
| COALINDIA 29Dec 390 CE | 10:05 | 5/5 | 12.8~ | 8.7 | 11.7~ | 15.0~ | 8.9 | 387.70 | 385.64 | 391.82 | ➖ NEITHER - closed 15:15 at +0.63R | 0.63 | 317 |
| SBILIFE 29Dec 1840 CE | 10:10 | 4/5 | 56.5~ | 50.0 | 49.7~ | 71.6~ | 50.4 | 1,831.00 | 1,817.48 | 1,858.05 | ➖ NEITHER - closed 15:15 at +1.15R | 1.15 | 72 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1010.json](output_upstox/2026-11-26/options_1010.json), [stocks_1010.json](output_upstox/2026-11-26/stocks_1010.json) · [full review](output_upstox/2026-11-26/review.md)

### 2026-11-25 · market BULLISH

16 picks · ✅ 4 target · ❌ 4 stop · ➖ 8 closed 15:15 · ⛔ 0 not filled · win 56% · avg 0.35R · P&L ₹17,086

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| TATACONSUM BUY | 10:20 | 1,174.80 | 1,153.40 | 1,217.60 | ➖ NEITHER - closed 15:15 at +0.24R | 0.24 | 360 |
| HDFCLIFE BUY | 10:20 | 605.60 | 582.30 | 652.20 | ➖ NEITHER - closed 15:15 at -0.11R | -0.11 | -276 |
| CIPLA BUY | 10:20 | 1,433.50 | 1,404.60 | 1,491.30 | ➖ NEITHER - closed 15:15 at -0.03R | -0.03 | -144 |
| HINDUNILVR BUY | 10:20 | 2,077.00 | 2,027.00 | 2,177.00 | ➖ NEITHER - closed 15:15 at +1.06R | 1.06 | 2,044 |
| SBILIFE BUY | 10:20 | 1,849.80 | 1,808.80 | 1,931.80 | ➖ NEITHER - closed 15:15 at -0.65R | -0.65 | -1,365 |
| ITC BUY | 10:20 | 308.05 | 300.50 | 323.15 | ➖ NEITHER - closed 15:15 at +0.17R | 0.17 | 254 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ICICIBANK 29Dec 1640 CE | 10:20 | 5/5 | 74.6~ | 74.6~ | 67.1~ | 91.0~ | 67.0~ | 1,642.50 | 1,628.40 | 1,670.71 | ❌ NO - hit STOP LOSS at 13:01 | -1.00 | -5,526 |
| ETERNAL 29Dec 370 CE | 10:20 | 5/5 | 13.7~ | 13.7~ | 12.0~ | 17.6~ | 17.6~ | 369.60 | 366.26 | 376.27 | ✅ YES - reached TARGET at 11:50 | 2.00 | 9,241 |
| HINDUNILVR 29Dec 2080 CE | 10:20 | 5/5 | 73.6~ | 73.6~ | 61.1~ | 102.6~ | 102.5~ | 2,077.00 | 2,052.52 | 2,125.97 | ✅ YES - reached TARGET at 14:10 | 2.00 | 8,567 |
| HDFCLIFE 29Dec 610 CE | 10:20 | 5/5 | 24.2~ | 24.2~ | 20.8~ | 31.9~ | 20.7~ | 605.60 | 598.70 | 619.41 | ❌ NO - hit STOP LOSS at 12:04 | -1.00 | -3,887 |
| TATACONSUM 29Dec 1180 CE | 10:20 | 5/5 | 49.8~ | 49.8~ | 43.7~ | 63.4~ | 52.4~ | 1,174.80 | 1,162.80 | 1,198.79 | ➖ NEITHER - closed 15:15 at +0.43R | 0.43 | 1,328 |
| SBILIFE 29Dec 1840 CE | 10:20 | 5/5 | 68.5~ | 68.5~ | 60.0~ | 87.3~ | 60.0~ | 1,849.80 | 1,834.51 | 1,880.39 | ❌ NO - hit STOP LOSS at 12:26 | -1.00 | -3,309 |
| NESTLEIND 29Dec 1320 CE | 10:20 | 5/5 | 57.8~ | 57.8~ | 51.8~ | 70.8~ | 70.7~ | 1,329.90 | 1,319.20 | 1,351.31 | ✅ YES - reached TARGET at 15:11 | 2.00 | 6,336 |
| ITC 29Dec 310 CE | 10:20 | 5/5 | 8.7~ | 8.7~ | 7.5~ | 11.6~ | 9.3~ | 308.05 | 305.50 | 313.14 | ➖ NEITHER - closed 15:15 at +0.49R | 0.49 | 993 |
| BAJAJFINSV 29Dec 1920 CE | 10:20 | 5/5 | 64.5~ | 64.5~ | 57.0~ | 80.7~ | 80.8~ | 1,917.20 | 1,903.03 | 1,945.55 | ✅ YES - reached TARGET at 11:01 | 2.00 | 4,797 |
| POWERGRID 29Dec 265 CE | 10:20 | 3/5 | 10.5~ | 10.5~ | 9.3~ | 13.0~ | 9.3~ | 265.25 | 263.07 | 269.60 | ❌ NO - hit STOP LOSS at 13:11 | -1.00 | -2,326 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1020.json](output_upstox/2026-11-25/options_1020.json), [stocks_1020.json](output_upstox/2026-11-25/stocks_1020.json) · [full review](output_upstox/2026-11-25/review.md)

### 2026-11-23 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-11-23/options_1005.json), [stocks_1005.json](output_upstox/2026-11-23/stocks_1005.json) · [full review](output_upstox/2026-11-23/review.md)

### 2026-11-20 · market BULLISH · backtest replay

10 picks · ✅ 6 target · ❌ 2 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 80% · avg 1.06R · P&L ₹36,098

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| APOLLOHOSP BUY | 10:05 | 9,147.50 | 8,800.00 | 9,842.50 | ➖ NEITHER - closed 15:15 at +0.12R | 0.12 | 164 |
| AXISBANK BUY | 10:05 | 1,392.60 | 1,368.80 | 1,440.20 | ✅ YES - reached TARGET at 13:00 | 2.00 | 3,298 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BAJFINANCE 23Nov 1100 CE | 10:05 | 5/5 | 14.8~ | 14.8~ | 11.2~ | 23.4~ | 23.3~ | 1,097.60 | 1,089.94 | 1,112.91 | ✅ YES - reached TARGET at 12:00 | 2.00 | 6,281 |
| NIFTY 23Nov 25500 CE | 10:05 | 4/5 | 163.2~ | 163.2~ | 121.4~ | 265.9~ | 264.6~ | 25,503.35 | 25,418.00 | 25,674.04 | ✅ YES - reached TARGET at 12:20 | 2.00 | 6,517 |
| APOLLOHOSP 23Nov 9100 CE | 10:05 | 5/5 | 125.5~ | 125.5~ | 78.5~ | 253.9~ | 148.8~ | 9,147.50 | 9,057.99 | 9,326.51 | ➖ NEITHER - closed 15:15 at +0.47R | 0.47 | 2,824 |
| HINDALCO 23Nov 910 CE | 10:05 | 5/5 | 10.5~ | 10.5~ | 6.3~ | 22.3~ | 22.2~ | 911.65 | 902.89 | 929.16 | ✅ YES - reached TARGET at 13:40 | 2.00 | 8,141 |
| INFY 23Nov 1100 CE | 10:05 | 5/5 | 18.1~ | 18.1~ | 11.4~ | 36.0~ | 11.2~ | 1,108.80 | 1,096.76 | 1,132.89 | ❌ NO - hit STOP LOSS at 13:55 | -1.00 | -2,837 |
| AXISBANK 23Nov 1400 CE | 10:05 | 5/5 | 9.8~ | 9.8~ | 6.3~ | 19.5~ | 19.5~ | 1,392.60 | 1,383.43 | 1,410.95 | ✅ YES - reached TARGET at 11:50 | 2.00 | 5,989 |
| MAXHEALTH 23Nov 1080 CE | 10:05 | 5/5 | 15.9~ | 15.9~ | 8.6~ | 37.8~ | 8.6~ | 1,085.75 | 1,071.02 | 1,115.22 | ❌ NO - hit STOP LOSS at 10:50 | -1.00 | -3,911 |
| BANKNIFTY 23Nov 63200 CE | 10:05 | 5/5 | 463.6~ | 463.6~ | 334.5~ | 789.9~ | 787.4~ | 63,160.10 | 62,883.38 | 63,713.54 | ✅ YES - reached TARGET at 11:55 | 2.00 | 9,632 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-20/options_1005.json), [stocks_1005.json](output_upstox/2026-11-20/stocks_1005.json) · [full review](output_upstox/2026-11-20/review.md)

### 2026-11-19 · market BULLISH · backtest replay

11 picks · ✅ 2 target · ❌ 2 stop · ➖ 7 closed 15:15 · ⛔ 0 not filled · win 73% · avg 0.66R · P&L ₹15,789

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| MARUTI BUY | 10:05 | 13,253.00 | 12,602.00 | 14,555.00 | ➖ NEITHER - closed 15:15 at +0.46R | 0.46 | 861 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JSWSTEEL 23Nov 1320 CE | 10:05 | 5/5 | 23.3~ | 23.3~ | 17.9~ | 36.0~ | 17.8~ | 1,325.00 | 1,314.84 | 1,345.31 | ❌ NO - hit STOP LOSS at 12:15 | -1.00 | -3,765 |
| JIOFIN 23Nov 225 CE | 10:05 | 4/5 | 3.1~ | 3.1~ | 2.4~ | 4.8~ | 4.0~ | 224.95 | 223.45 | 227.95 | ➖ NEITHER - closed 15:15 at +1.17R | 1.17 | 2,041 |
| BAJFINANCE 23Nov 1100 CE | 10:05 | 3/5 | 16.7~ | 16.7~ | 12.8~ | 25.9~ | 15.9~ | 1,096.60 | 1,088.22 | 1,113.35 | ➖ NEITHER - closed 15:15 at -0.08R | -0.08 | -672 |
| TATASTEEL 23Nov 180 CE | 10:05 | 5/5 | 3.0~ | 3.0~ | 2.4~ | 4.5~ | 3.5~ | 180.28 | 179.01 | 182.82 | ➖ NEITHER - closed 15:15 at +0.83R | 0.83 | 1,347 |
| NIFTY 23Nov 25250 CE | 10:05 | 5/5 | 190.4~ | 190.4~ | 146.3~ | 296.3~ | 293.6~ | 25,272.70 | 25,186.71 | 25,444.69 | ✅ YES - reached TARGET at 14:15 | 2.00 | 6,627 |
| TMPV 23Nov 260 CE | 10:05 | 5/5 | 5.4~ | 5.4~ | 4.1~ | 8.5~ | 6.6~ | 259.55 | 256.83 | 265.00 | ➖ NEITHER - closed 15:15 at +0.92R | 0.92 | 1,855 |
| TRENT 23Nov 3200 CE | 10:05 | 5/5 | 52.2~ | 52.2~ | 37.6~ | 89.1~ | 57.4~ | 3,210.20 | 3,181.46 | 3,267.68 | ➖ NEITHER - closed 15:15 at +0.39R | 0.39 | 1,100 |
| M&M 23Nov 3450 CE | 10:05 | 5/5 | 66.2~ | 66.2~ | 49.1~ | 108.1~ | 96.7~ | 3,464.10 | 3,431.18 | 3,529.93 | ➖ NEITHER - closed 15:15 at +1.56R | 1.56 | 6,038 |
| BHARTIARTL 23Nov 2160 CE | 10:05 | 5/5 | 21.5~ | 21.5~ | 16.4~ | 33.9~ | 16.4~ | 2,154.40 | 2,143.11 | 2,176.99 | ❌ NO - hit STOP LOSS at 10:55 | -1.00 | -2,479 |
| HDFCBANK 23Nov 810 CE | 10:05 | 4/5 | 10.0~ | 10.0~ | 8.0~ | 14.5~ | 14.4~ | 810.20 | 806.27 | 818.06 | ✅ YES - reached TARGET at 12:40 | 2.00 | 2,837 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-19/options_1005.json), [stocks_1005.json](output_upstox/2026-11-19/stocks_1005.json) · [full review](output_upstox/2026-11-19/review.md)

### 2026-11-18 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-11-18/options_1005.json), [stocks_1005.json](output_upstox/2026-11-18/stocks_1005.json) · [full review](output_upstox/2026-11-18/review.md)

### 2026-11-17 · market BULLISH · backtest replay

4 picks · ✅ 1 target · ❌ 1 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 50% · avg 0.29R · P&L ₹2,333

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ICICIBANK 23Nov 1600 CE | 10:05 | 5/5 | 25.5~ | 25.5~ | 21.1~ | 35.4~ | 28.6~ | 1,597.90 | 1,588.94 | 1,615.82 | ➖ NEITHER - closed 15:15 at +0.76R | 0.76 | 2,085 |
| SHRIRAMFIN 23Nov 990 CE | 10:05 | 5/5 | 24.7~ | 24.7~ | 21.8~ | 31.0~ | 22.5~ | 988.00 | 982.11 | 999.77 | ➖ NEITHER - closed 15:15 at -0.59R | -0.59 | -1,902 |
| NIFTY 23Nov 25350 CE | 10:05 | 5/5 | 227.0~ | 227.0~ | 194.4~ | 298.8~ | 298.1~ | 25,360.65 | 25,298.20 | 25,485.54 | ✅ YES - reached TARGET at 11:55 | 2.00 | 4,542 |
| SBIN 23Nov 1120 CE | 10:05 | 5/5 | 11.9~ | 11.9~ | 8.9~ | 19.4~ | 8.8~ | 1,112.40 | 1,105.03 | 1,127.13 | ❌ NO - hit STOP LOSS at 13:10 | -1.00 | -2,392 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-17/options_1005.json), [stocks_1005.json](output_upstox/2026-11-17/stocks_1005.json) · [full review](output_upstox/2026-11-17/review.md)

### 2026-11-16 · market BULLISH · backtest replay

11 picks · ✅ 3 target · ❌ 2 stop · ➖ 6 closed 15:15 · ⛔ 0 not filled · win 82% · avg 0.86R · P&L ₹22,844

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| MAXHEALTH BUY | 10:05 | 987.95 | 947.15 | 1,069.55 | ➖ NEITHER - closed 15:15 at +0.49R | 0.49 | 931 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ITC 23Nov 290 CE | 10:05 | 5/5 | 4.4~ | 4.4~ | 3.1~ | 7.9~ | 6.6~ | 291.40 | 288.90 | 296.40 | ➖ NEITHER - closed 15:15 at +1.36R | 1.36 | 3,709 |
| APOLLOHOSP 23Nov 8700 CE | 10:05 | 5/5 | 125.7~ | 125.7~ | 102.7~ | 179.2~ | 178.7~ | 8,654.00 | 8,602.77 | 8,756.45 | ✅ YES - reached TARGET at 12:15 | 2.00 | 6,536 |
| HINDUNILVR 23Nov 2000 CE | 10:05 | 5/5 | 25.3~ | 25.3~ | 20.6~ | 36.2~ | 20.7~ | 1,994.00 | 1,983.95 | 2,014.10 | ❌ NO - hit STOP LOSS at 10:35 | -1.00 | -1,455 |
| ETERNAL 23Nov 370 CE | 10:05 | 5/5 | 7.1~ | 7.1~ | 5.7~ | 10.4~ | 7.3~ | 369.25 | 366.37 | 375.01 | ➖ NEITHER - closed 15:15 at +0.23R | 0.23 | 436 |
| HDFCBANK 23Nov 810 CE | 10:05 | 5/5 | 14.2~ | 14.2~ | 12.0~ | 19.0~ | 12.0~ | 810.50 | 806.28 | 818.94 | ❌ NO - hit STOP LOSS at 10:35 | -1.00 | -1,458 |
| NESTLEIND 23Nov 1280 CE | 10:05 | 5/5 | 24.2~ | 24.2~ | 19.9~ | 34.2~ | 30.4~ | 1,281.50 | 1,273.01 | 1,298.49 | ➖ NEITHER - closed 15:15 at +1.35R | 1.35 | 3,027 |
| TATACONSUM 23Nov 1100 CE | 10:05 | 5/5 | 22.9~ | 22.9~ | 19.0~ | 31.8~ | 29.6~ | 1,100.60 | 1,092.86 | 1,116.09 | ➖ NEITHER - closed 15:15 at +1.59R | 1.59 | 3,580 |
| HDFCLIFE 23Nov 600 CE | 10:05 | 5/5 | 7.9~ | 7.9~ | 6.2~ | 11.9~ | 11.9~ | 595.15 | 591.14 | 603.17 | ✅ YES - reached TARGET at 10:55 | 2.00 | 4,376 |
| ULTRACEMCO 23Nov 12250 CE | 10:05 | 5/5 | 196.0~ | 196.0~ | 160.9~ | 276.9~ | 209.1~ | 12,239.00 | 12,167.51 | 12,381.98 | ➖ NEITHER - closed 15:15 at +0.43R | 0.43 | 585 |
| POWERGRID 23Nov 260 CE | 10:05 | 3/5 | 2.8~ | 2.8~ | 2.3~ | 4.2~ | 4.2~ | 257.50 | 256.02 | 260.46 | ✅ YES - reached TARGET at 12:45 | 2.00 | 2,576 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-16/options_1005.json), [stocks_1005.json](output_upstox/2026-11-16/stocks_1005.json) · [full review](output_upstox/2026-11-16/review.md)

### 2026-11-13 · market BULLISH · backtest replay

1 picks · ✅ 0 target · ❌ 0 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 100% · avg 0.32R · P&L ₹542

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| EICHERMOT BUY | 10:05 | 7,602.00 | 7,451.50 | 7,903.00 | ➖ NEITHER - closed 15:15 at +0.32R | 0.32 | 542 |

Files: [options_1005.json](output_upstox/2026-11-13/options_1005.json), [stocks_1005.json](output_upstox/2026-11-13/stocks_1005.json) · [full review](output_upstox/2026-11-13/review.md)

### 2026-11-12 · market BULLISH · backtest replay

11 picks · ✅ 0 target · ❌ 9 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 9% · avg -0.83R · P&L ₹-24,636

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| KOTAKBANK BUY | 10:05 | 492.60 | 484.35 | 509.10 | ➖ NEITHER - closed 15:15 at -0.30R | -0.30 | -590 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RELIANCE 23Nov 1340 CE | 10:05 | 5/5 | 46.1~ | 46.1~ | 42.6~ | 53.4~ | 42.6~ | 1,340.00 | 1,333.32 | 1,353.35 | ❌ NO - hit STOP LOSS at 11:40 | -1.00 | -1,888 |
| JSWSTEEL 23Nov 1360 CE | 10:05 | 5/5 | 38.0~ | 38.0~ | 34.0~ | 46.7~ | 34.0~ | 1,364.50 | 1,356.96 | 1,379.59 | ❌ NO - hit STOP LOSS at 10:25 | -1.00 | -2,815 |
| TITAN 23Nov 5000 CE | 10:05 | 5/5 | 108.6~ | 108.6~ | 93.7~ | 141.5~ | 93.7~ | 5,024.20 | 4,997.28 | 5,078.03 | ❌ NO - hit STOP LOSS at 11:10 | -1.00 | -2,696 |
| NIFTY 17Nov 25350 CE | 10:05 | 5/5 | 225.7~ | 225.7~ | 182.8~ | 325.0~ | 182.3~ | 25,352.60 | 25,267.21 | 25,523.39 | ❌ NO - hit STOP LOSS at 11:40 | -1.00 | -2,907 |
| ADANIPORTS 23Nov 1940 CE | 10:05 | 4/5 | 44.4~ | 44.4~ | 38.5~ | 57.3~ | 38.5~ | 1,932.20 | 1,920.16 | 1,956.27 | ❌ NO - hit STOP LOSS at 12:05 | -1.00 | -2,915 |
| JIOFIN 23Nov 232.5 CE | 10:05 | 5/5 | 5.4~ | 5.4~ | 4.6~ | 7.3~ | 4.6~ | 232.92 | 231.31 | 236.13 | ❌ NO - hit STOP LOSS at 12:05 | -1.00 | -2,061 |
| ADANIENT 23Nov 2750 CE | 10:05 | 5/5 | 70.3~ | 70.3~ | 60.0~ | 93.6~ | 60.0~ | 2,753.00 | 2,732.85 | 2,793.30 | ❌ NO - hit STOP LOSS at 11:10 | -1.00 | -3,307 |
| ETERNAL 23Nov 365 CE | 10:05 | 5/5 | 10.5~ | 10.5~ | 8.9~ | 13.9~ | 8.9~ | 366.55 | 363.66 | 372.33 | ❌ NO - hit STOP LOSS at 14:35 | -1.00 | -4,002 |
| SBILIFE 23Nov 1820 CE | 10:05 | 5/5 | 26.4~ | 26.4~ | 19.6~ | 43.6~ | 27.3~ | 1,813.60 | 1,798.59 | 1,843.62 | ➖ NEITHER - closed 15:15 at +0.16R | 0.16 | 265 |
| TATACONSUM 23Nov 1100 CE | 10:05 | 5/5 | 26.4~ | 26.4~ | 23.5~ | 32.9~ | 23.5~ | 1,095.30 | 1,089.20 | 1,107.51 | ❌ NO - hit STOP LOSS at 10:55 | -1.00 | -1,720 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-12/options_1005.json), [stocks_1005.json](output_upstox/2026-11-12/stocks_1005.json) · [full review](output_upstox/2026-11-12/review.md)

### 2026-11-11 · market BULLISH · backtest replay

4 picks · ✅ 0 target · ❌ 1 stop · ➖ 3 closed 15:15 · ⛔ 0 not filled · win 50% · avg -0.08R · P&L ₹-4,190

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRENT 23Nov 3200 CE | 10:05 | 5/5 | 78.4~ | 78.4~ | 65.3~ | 108.6~ | 84.9~ | 3,185.80 | 3,158.30 | 3,240.79 | ➖ NEITHER - closed 15:15 at +0.52R | 0.52 | 1,372 |
| ETERNAL 23Nov 370 CE | 10:05 | 5/5 | 10.8~ | 10.8~ | 9.0~ | 15.1~ | 9.0~ | 371.10 | 367.51 | 378.29 | ❌ NO - hit STOP LOSS at 10:40 | -1.00 | -4,622 |
| TATASTEEL 23Nov 187.5 CE | 10:05 | 4/5 | 4.9~ | 4.9~ | 4.2~ | 6.5~ | 5.4~ | 187.58 | 186.20 | 190.34 | ➖ NEITHER - closed 15:15 at +0.71R | 0.71 | 1,270 |
| SBIN 23Nov 1060 CE | 10:05 | 5/5 | 22.6~ | 22.6~ | 17.8~ | 34.1~ | 19.8~ | 1,065.05 | 1,056.06 | 1,083.02 | ➖ NEITHER - closed 15:15 at -0.53R | -0.53 | -2,209 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-11/options_1005.json), [stocks_1005.json](output_upstox/2026-11-11/stocks_1005.json) · [full review](output_upstox/2026-11-11/review.md)

### 2026-11-09 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-11-09/options_1005.json), [stocks_1005.json](output_upstox/2026-11-09/stocks_1005.json) · [full review](output_upstox/2026-11-09/review.md)

### 2026-11-06 · market BULLISH · backtest replay

15 picks · ✅ 4 target · ❌ 4 stop · ➖ 7 closed 15:15 · ⛔ 0 not filled · win 67% · avg 0.56R · P&L ₹19,159

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| M&M BUY | 10:05 | 3,262.10 | 3,130.10 | 3,526.10 | ➖ NEITHER - closed 15:15 at -0.01R | -0.01 | -68 |
| ICICIBANK BUY | 10:05 | 1,521.90 | 1,504.60 | 1,556.50 | ✅ YES - reached TARGET at 14:30 | 2.00 | 2,167 |
| HDFCBANK BUY | 10:05 | 773.00 | 754.05 | 810.90 | ➖ NEITHER - closed 15:15 at +0.66R | 0.66 | 1,231 |
| SBILIFE BUY | 10:05 | 1,728.20 | 1,705.50 | 1,773.60 | ➖ NEITHER - closed 15:15 at +1.17R | 1.17 | 1,434 |
| MARUTI BUY | 10:05 | 12,661.00 | 12,451.00 | 13,081.00 | ➖ NEITHER - closed 15:15 at +0.42R | 0.42 | 545 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ITC 23Nov 280 CE | 10:05 | 5/5 | 9.1~ | 9.1~ | 7.9~ | 11.6~ | 7.9~ | 281.30 | 279.14 | 285.62 | ❌ NO - hit STOP LOSS at 11:00 | -1.00 | -2,095 |
| ICICIBANK 23Nov 1520 CE | 10:05 | 5/5 | 42.8~ | 42.8~ | 36.6~ | 56.8~ | 56.7~ | 1,521.90 | 1,509.92 | 1,545.86 | ✅ YES - reached TARGET at 13:40 | 2.00 | 9,585 |
| APOLLOHOSP 23Nov 8400 CE | 10:05 | 4/5 | 323.3~ | 323.3~ | 290.5~ | 393.8~ | 290.1~ | 8,449.00 | 8,389.09 | 8,568.81 | ❌ NO - hit STOP LOSS at 12:00 | -1.00 | -4,290 |
| NIFTY 10Nov 24650 CE | 10:05 | 5/5 | 164.5~ | 164.5~ | 119.4~ | 278.8~ | 276.3~ | 24,630.95 | 24,534.09 | 24,824.67 | ✅ YES - reached TARGET at 13:55 | 2.00 | 7,198 |
| TITAN 23Nov 4950 CE | 10:05 | 5/5 | 112.1~ | 112.1~ | 80.1~ | 194.8~ | 133.9~ | 4,954.50 | 4,889.48 | 5,084.53 | ➖ NEITHER - closed 15:15 at +0.61R | 0.61 | 3,727 |
| TATACONSUM 23Nov 1080 CE | 10:05 | 5/5 | 35.2~ | 35.2~ | 31.7~ | 42.8~ | 38.2~ | 1,078.00 | 1,071.11 | 1,091.79 | ➖ NEITHER - closed 15:15 at +0.87R | 0.87 | 1,545 |
| BAJAJ-AUTO 23Nov 10750 CE | 10:05 | 5/5 | 322.8~ | 322.8~ | 267.2~ | 450.3~ | 267.1~ | 10,843.00 | 10,744.23 | 11,040.54 | ❌ NO - hit STOP LOSS at 11:20 | -1.00 | -4,281 |
| MARUTI 23Nov 12750 CE | 10:05 | 5/5 | 318.3~ | 318.3~ | 262.4~ | 448.7~ | 361.3~ | 12,661.00 | 12,541.05 | 12,900.91 | ➖ NEITHER - closed 15:15 at +0.74R | 0.74 | 2,069 |
| M&M 23Nov 3250 CE | 10:05 | 5/5 | 99.2~ | 99.2~ | 74.2~ | 161.3~ | 74.0~ | 3,262.10 | 3,213.23 | 3,359.84 | ❌ NO - hit STOP LOSS at 12:40 | -1.00 | -5,129 |
| TATASTEEL 23Nov 182.5 CE | 10:05 | 3/5 | 4.7~ | 4.7~ | 3.8~ | 6.7~ | 6.7~ | 181.40 | 179.54 | 185.11 | ✅ YES - reached TARGET at 13:40 | 2.00 | 5,522 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-06/options_1005.json), [stocks_1005.json](output_upstox/2026-11-06/stocks_1005.json) · [full review](output_upstox/2026-11-06/review.md)

### 2026-11-05 · market BULLISH · backtest replay

16 picks · ✅ 4 target · ❌ 5 stop · ➖ 7 closed 15:15 · ⛔ 0 not filled · win 62% · avg 0.27R · P&L ₹13,939

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| ICICIBANK BUY | 10:05 | 1,462.80 | 1,445.90 | 1,496.60 | ✅ YES - reached TARGET at 13:45 | 2.00 | 2,216 |
| SUNPHARMA BUY | 10:05 | 1,815.00 | 1,762.40 | 1,920.20 | ➖ NEITHER - closed 15:15 at +0.40R | 0.40 | 726 |
| JIOFIN BUY | 10:05 | 227.91 | 224.72 | 234.29 | ➖ NEITHER - closed 15:15 at +0.50R | 0.50 | 614 |
| SBILIFE BUY | 10:05 | 1,737.00 | 1,713.10 | 1,784.80 | ➖ NEITHER - closed 15:15 at +0.08R | 0.08 | 32 |
| TECHM BUY | 10:05 | 1,840.50 | 1,807.30 | 1,906.90 | ➖ NEITHER - closed 15:15 at -0.46R | -0.46 | -908 |
| ADANIENT BUY | 10:05 | 2,773.00 | 2,727.00 | 2,865.00 | ❌ NO - hit STOP LOSS at 15:10 | -1.00 | -1,738 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JSWSTEEL 23Nov 1360 CE | 10:05 | 5/5 | 55.1~ | 55.1~ | 48.0~ | 70.8~ | 48.0~ | 1,361.90 | 1,348.31 | 1,389.08 | ❌ NO - hit STOP LOSS at 11:15 | -1.00 | -4,932 |
| ICICIBANK 23Nov 1460 CE | 10:05 | 5/5 | 34.1~ | 34.1~ | 28.4~ | 47.0~ | 46.9~ | 1,462.80 | 1,452.08 | 1,484.25 | ✅ YES - reached TARGET at 13:15 | 2.00 | 8,887 |
| ADANIENT 23Nov 2750 CE | 10:05 | 5/5 | 125.9~ | 125.9~ | 109.3~ | 162.5~ | 109.1~ | 2,773.00 | 2,742.76 | 2,833.48 | ❌ NO - hit STOP LOSS at 12:35 | -1.00 | -5,328 |
| JIOFIN 23Nov 227.5 CE | 10:05 | 5/5 | 7.0~ | 7.0~ | 5.5~ | 10.4~ | 7.8~ | 227.91 | 225.06 | 233.61 | ➖ NEITHER - closed 15:15 at +0.56R | 0.56 | 1,915 |
| BAJFINANCE 23Nov 1040 CE | 10:05 | 5/5 | 32.7~ | 32.7~ | 25.8~ | 49.3~ | 49.2~ | 1,044.15 | 1,030.86 | 1,070.72 | ✅ YES - reached TARGET at 13:40 | 2.00 | 12,260 |
| INFY 23Nov 1160 CE | 10:05 | 5/5 | 48.9~ | 48.9~ | 42.9~ | 62.3~ | 42.8~ | 1,167.10 | 1,155.91 | 1,189.48 | ❌ NO - hit STOP LOSS at 12:40 | -1.00 | -2,556 |
| SBILIFE 23Nov 1740 CE | 10:05 | 5/5 | 33.0~ | 33.0~ | 26.9~ | 47.4~ | 33.8~ | 1,737.00 | 1,724.66 | 1,761.69 | ➖ NEITHER - closed 15:15 at +0.16R | 0.16 | 236 |
| ETERNAL 23Nov 355 CE | 10:05 | 5/5 | 10.7~ | 10.7~ | 9.2~ | 14.1~ | 14.0~ | 352.55 | 349.39 | 358.87 | ✅ YES - reached TARGET at 15:10 | 2.00 | 8,016 |
| WIPRO 23Nov 197.5 CE | 10:05 | 5/5 | 7.7~ | 7.7~ | 6.8~ | 9.6~ | 7.8~ | 198.05 | 196.36 | 201.43 | ➖ NEITHER - closed 15:15 at +0.15R | 0.15 | 189 |
| TECHM 23Nov 1840 CE | 10:05 | 5/5 | 78.7~ | 78.7~ | 69.6~ | 98.6~ | 69.5~ | 1,840.50 | 1,822.98 | 1,875.54 | ❌ NO - hit STOP LOSS at 12:05 | -1.00 | -5,690 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-05/options_1005.json), [stocks_1005.json](output_upstox/2026-11-05/stocks_1005.json) · [full review](output_upstox/2026-11-05/review.md)

### 2026-11-04 · market BULLISH · backtest replay

13 picks · ✅ 0 target · ❌ 8 stop · ➖ 5 closed 15:15 · ⛔ 0 not filled · win 23% · avg -0.49R · P&L ₹-20,360

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| ITC BUY | 10:05 | 283.25 | 272.10 | 305.55 | ➖ NEITHER - closed 15:15 at -0.26R | -0.26 | -582 |
| BAJAJFINSV BUY | 10:05 | 1,781.40 | 1,704.30 | 1,935.60 | ➖ NEITHER - closed 15:15 at -0.34R | -0.34 | -707 |
| TITAN BUY | 10:05 | 4,651.10 | 4,471.50 | 5,010.30 | ➖ NEITHER - closed 15:15 at +0.44R | 0.44 | 814 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRENT 23Nov 3050 CE | 10:05 | 5/5 | 160.1~ | 160.1~ | 149.4~ | 182.0~ | 149.5~ | 3,040.70 | 3,020.48 | 3,081.14 | ❌ NO - hit STOP LOSS at 10:25 | -1.00 | -2,499 |
| ADANIPORTS 23Nov 1920 CE | 10:05 | 5/5 | 60.4~ | 60.4~ | 52.1~ | 79.1~ | 52.1~ | 1,912.00 | 1,895.15 | 1,945.71 | ❌ NO - hit STOP LOSS at 11:00 | -1.00 | -4,071 |
| ITC 23Nov 285 CE | 10:05 | 5/5 | 7.9~ | 7.9~ | 6.3~ | 11.8~ | 6.3~ | 283.25 | 279.77 | 290.21 | ❌ NO - hit STOP LOSS at 10:40 | -1.00 | -2,887 |
| TITAN 23Nov 4650 CE | 10:05 | 5/5 | 110.6~ | 110.6~ | 89.1~ | 161.4~ | 89.2~ | 4,651.10 | 4,608.76 | 4,735.77 | ❌ NO - hit STOP LOSS at 10:25 | -1.00 | -3,837 |
| JIOFIN 23Nov 217.5 CE | 10:05 | 5/5 | 6.3~ | 6.3~ | 5.5~ | 8.0~ | 5.5~ | 217.41 | 215.93 | 220.37 | ❌ NO - hit STOP LOSS at 10:25 | -1.00 | -1,866 |
| ONGC 23Nov 232.5 CE | 10:05 | 5/5 | 5.6~ | 5.6~ | 5.0~ | 7.1~ | 6.3~ | 233.02 | 231.75 | 235.56 | ➖ NEITHER - closed 15:15 at +0.94R | 0.94 | 1,394 |
| SHRIRAMFIN 23Nov 910 CE | 10:05 | 5/5 | 40.7~ | 40.7~ | 35.8~ | 51.5~ | 35.8~ | 905.90 | 896.16 | 925.37 | ❌ NO - hit STOP LOSS at 10:20 | -1.00 | -4,153 |
| ADANIENT 23Nov 2700 CE | 10:05 | 5/5 | 92.4~ | 92.4~ | 78.5~ | 124.0~ | 103.9~ | 2,678.00 | 2,648.93 | 2,736.14 | ➖ NEITHER - closed 15:15 at +0.80R | 0.80 | 3,433 |
| BAJFINANCE 23Nov 990 CE | 10:05 | 5/5 | 29.2~ | 29.2~ | 24.6~ | 39.5~ | 24.6~ | 991.05 | 982.27 | 1,008.62 | ❌ NO - hit STOP LOSS at 11:05 | -1.00 | -3,508 |
| LT 23Nov 4000 CE | 10:05 | 5/5 | 89.7~ | 89.7~ | 79.3~ | 112.5~ | 79.4~ | 3,984.00 | 3,962.94 | 4,026.13 | ❌ NO - hit STOP LOSS at 10:20 | -1.00 | -1,891 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-04/options_1005.json), [stocks_1005.json](output_upstox/2026-11-04/stocks_1005.json) · [full review](output_upstox/2026-11-04/review.md)

### 2026-11-03 · market BULLISH · backtest replay

3 picks · ✅ 1 target · ❌ 0 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 100% · avg 1.49R · P&L ₹13,070

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TATACONSUM 23Nov 1040 CE | 10:05 | 5/5 | 41.5~ | 41.5~ | 36.3~ | 52.7~ | 51.7~ | 1,050.00 | 1,040.91 | 1,068.19 | ➖ NEITHER - closed 15:15 at +1.86R | 1.86 | 5,529 |
| BHARTIARTL 23Nov 2020 CE | 10:05 | 5/5 | 50.7~ | 50.7~ | 44.8~ | 63.5~ | 63.4~ | 2,011.80 | 2,000.04 | 2,035.32 | ✅ YES - reached TARGET at 11:55 | 2.00 | 5,944 |
| HINDUNILVR 23Nov 1940 CE | 10:05 | 5/5 | 52.2~ | 52.2~ | 43.3~ | 72.8~ | 57.8~ | 1,942.50 | 1,925.32 | 1,976.87 | ➖ NEITHER - closed 15:15 at +0.61R | 0.61 | 1,597 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-03/options_1005.json), [stocks_1005.json](output_upstox/2026-11-03/stocks_1005.json) · [full review](output_upstox/2026-11-03/review.md)

### 2026-11-02 · market BULLISH · backtest replay

12 picks · ✅ 1 target · ❌ 6 stop · ➖ 5 closed 15:15 · ⛔ 0 not filled · win 33% · avg -0.12R · P&L ₹-3,287

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| COALINDIA BUY | 10:05 | 400.70 | 395.00 | 412.10 | ➖ NEITHER - closed 15:15 at +1.03R | 1.03 | 1,374 |
| TMPV BUY | 10:05 | 272.55 | 267.00 | 283.65 | ➖ NEITHER - closed 15:15 at -0.24R | -0.24 | -568 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NIFTY 03Nov 23300 CE | 10:05 | 5/5 | 86.8~ | 86.8~ | 52.7~ | 180.8~ | 49.8~ | 23,303.60 | 23,230.65 | 23,449.50 | ❌ NO - hit STOP LOSS at 13:05 | -1.00 | -2,465 |
| SHRIRAMFIN 23Nov 840 CE | 10:05 | 5/5 | 37.8~ | 37.8~ | 34.4~ | 45.0~ | 45.0~ | 837.20 | 830.63 | 850.34 | ✅ YES - reached TARGET at 11:10 | 2.00 | 5,821 |
| TATACONSUM 23Nov 1040 CE | 10:05 | 5/5 | 33.0~ | 33.0~ | 29.8~ | 39.7~ | 29.8~ | 1,032.50 | 1,026.10 | 1,045.31 | ❌ NO - hit STOP LOSS at 12:40 | -1.00 | -1,854 |
| TMPV 23Nov 275 CE | 10:05 | 5/5 | 7.3~ | 7.3~ | 6.2~ | 10.1~ | 6.7~ | 272.55 | 270.01 | 277.64 | ➖ NEITHER - closed 15:15 at -0.53R | -0.53 | -1,169 |
| HINDUNILVR 23Nov 1900 CE | 10:05 | 5/5 | 49.1~ | 49.1~ | 42.8~ | 63.1~ | 42.7~ | 1,893.40 | 1,880.78 | 1,918.65 | ❌ NO - hit STOP LOSS at 13:10 | -1.00 | -2,003 |
| JIOFIN 23Nov 212.5 CE | 10:05 | 5/5 | 5.1~ | 5.1~ | 4.2~ | 7.2~ | 5.8~ | 211.44 | 209.54 | 215.25 | ➖ NEITHER - closed 15:15 at +0.71R | 0.71 | 1,531 |
| M&M 23Nov 2900 CE | 10:05 | 5/5 | 74.3~ | 74.3~ | 64.9~ | 95.2~ | 64.6~ | 2,891.00 | 2,872.18 | 2,928.64 | ❌ NO - hit STOP LOSS at 14:40 | -1.00 | -2,025 |
| COALINDIA 23Nov 400 CE | 10:05 | 5/5 | 10.3~ | 10.3~ | 8.3~ | 14.9~ | 13.7~ | 400.70 | 396.95 | 408.21 | ➖ NEITHER - closed 15:15 at +1.56R | 1.56 | 4,581 |
| ETERNAL 23Nov 345 CE | 10:05 | 5/5 | 14.4~ | 14.4~ | 12.9~ | 17.8~ | 12.8~ | 347.25 | 344.40 | 352.95 | ❌ NO - hit STOP LOSS at 13:35 | -1.00 | -4,012 |
| LT 23Nov 3950 CE | 10:05 | 5/5 | 98.7~ | 98.7~ | 85.2~ | 129.0~ | 85.0~ | 3,936.10 | 3,908.87 | 3,990.55 | ❌ NO - hit STOP LOSS at 13:35 | -1.00 | -2,499 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-11-02/options_1005.json), [stocks_1005.json](output_upstox/2026-11-02/stocks_1005.json) · [full review](output_upstox/2026-11-02/review.md)

### 2026-10-30 · market BULLISH · backtest replay

1 picks · ✅ 0 target · ❌ 0 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 100% · avg 0.03R · P&L ₹18

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| INDIGO BUY | 10:05 | 4,832.60 | 4,635.40 | 5,227.00 | ➖ NEITHER - closed 15:15 at +0.03R | 0.03 | 18 |

Files: [options_1005.json](output_upstox/2026-10-30/options_1005.json), [stocks_1005.json](output_upstox/2026-10-30/stocks_1005.json) · [full review](output_upstox/2026-10-30/review.md)

### 2026-10-29 · market BULLISH · backtest replay

1 picks · ✅ 0 target · ❌ 0 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 100% · avg 1.31R · P&L ₹2,529

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| ADANIENT BUY | 10:05 | 2,537.00 | 2,473.10 | 2,664.80 | ➖ NEITHER - closed 15:15 at +1.31R | 1.31 | 2,529 |

Files: [options_1005.json](output_upstox/2026-10-29/options_1005.json), [stocks_1005.json](output_upstox/2026-10-29/stocks_1005.json) · [full review](output_upstox/2026-10-29/review.md)

### 2026-10-28 · market BEARISH · backtest replay

4 picks · ✅ 0 target · ❌ 1 stop · ➖ 3 closed 15:15 · ⛔ 0 not filled · win 50% · avg 0.13R · P&L ₹2,548

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JIOFIN 23Nov 205 PE | 10:05 | 5/5 | 5.4~ | 5.4~ | 4.5~ | 7.5~ | 4.5~ | 205.12 | 207.16 | 201.04 | ❌ NO - hit STOP LOSS at 11:15 | -1.00 | -2,147 |
| RELIANCE 23Nov 1180 PE | 10:05 | 5/5 | 31.9~ | 31.9~ | 26.0~ | 46.3~ | 41.5~ | 1,179.50 | 1,193.19 | 1,152.12 | ➖ NEITHER - closed 15:15 at +1.40R | 1.40 | 4,725 |
| ONGC 23Nov 225 PE | 10:05 | 5/5 | 4.7~ | 4.7~ | 4.0~ | 6.5~ | 4.5~ | 223.91 | 225.57 | 220.59 | ➖ NEITHER - closed 15:15 at -0.27R | -0.27 | -585 |
| COALINDIA 23Nov 395 PE | 10:05 | 5/5 | 9.3~ | 9.3~ | 8.0~ | 12.3~ | 9.8~ | 394.30 | 397.18 | 388.55 | ➖ NEITHER - closed 15:15 at +0.37R | 0.37 | 556 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-28/options_1005.json), [stocks_1005.json](output_upstox/2026-10-28/stocks_1005.json) · [full review](output_upstox/2026-10-28/review.md)

### 2026-10-27 · market BULLISH · backtest replay

3 picks · ✅ 0 target · ❌ 1 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 33% · avg -0.07R · P&L ₹-1,761

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| TATACONSUM BUY | 10:05 | 995.00 | 957.45 | 1,070.10 | ➖ NEITHER - closed 15:15 at -0.20R | -0.20 | -448 |
| BAJAJFINSV BUY | 10:05 | 1,664.90 | 1,651.60 | 1,691.50 | ➖ NEITHER - closed 15:15 at +0.98R | 0.98 | 704 |
| CIPLA BUY | 10:05 | 1,368.60 | 1,342.10 | 1,421.60 | ❌ NO - hit STOP LOSS at 11:40 | -1.00 | -2,017 |

Files: [options_1005.json](output_upstox/2026-10-27/options_1005.json), [stocks_1005.json](output_upstox/2026-10-27/stocks_1005.json) · [full review](output_upstox/2026-10-27/review.md)

### 2026-10-26 · market BULLISH · backtest replay

4 picks · ✅ 0 target · ❌ 0 stop · ➖ 4 closed 15:15 · ⛔ 0 not filled · win 75% · avg 0.14R · P&L ₹658

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| TRENT BUY | 10:05 | 2,738.00 | 2,690.60 | 2,832.80 | ➖ NEITHER - closed 15:15 at +0.27R | 0.27 | 386 |
| CIPLA BUY | 10:05 | 1,355.20 | 1,330.00 | 1,405.60 | ➖ NEITHER - closed 15:15 at -0.32R | -0.32 | -673 |
| ADANIENT BUY | 10:05 | 2,488.80 | 2,446.90 | 2,572.60 | ➖ NEITHER - closed 15:15 at +0.46R | 0.46 | 686 |
| HINDALCO BUY | 10:05 | 883.50 | 851.10 | 948.30 | ➖ NEITHER - closed 15:15 at +0.16R | 0.16 | 260 |

Files: [options_1005.json](output_upstox/2026-10-26/options_1005.json), [stocks_1005.json](output_upstox/2026-10-26/stocks_1005.json) · [full review](output_upstox/2026-10-26/review.md)

### 2026-10-23 · market BEARISH · backtest replay

10 picks · ✅ 3 target · ❌ 0 stop · ➖ 7 closed 15:15 · ⛔ 0 not filled · win 60% · avg 0.60R · P&L ₹20,758

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JSWSTEEL 27Oct 1200 PE | 10:05 | 5/5 | 15.0~ | 15.0~ | 10.9~ | 25.5~ | 25.2~ | 1,200.70 | 1,209.95 | 1,182.20 | ✅ YES - reached TARGET at 14:50 | 2.00 | 6,839 |
| ITC 27Oct 255 PE | 10:05 | 5/5 | 3.0~ | 3.0~ | 2.4~ | 4.7~ | 3.0~ | 257.20 | 258.96 | 253.68 | ➖ NEITHER - closed 15:15 at +0.03R | 0.03 | -196 |
| TRENT 27Oct 2700 PE | 10:05 | 5/5 | 50.5~ | 50.5~ | 41.1~ | 72.5~ | 71.7~ | 2,723.70 | 2,746.80 | 2,677.50 | ✅ YES - reached TARGET at 13:30 | 2.00 | 4,709 |
| JIOFIN 27Oct 205 PE | 10:05 | 5/5 | 2.2~ | 2.2~ | 1.4~ | 4.4~ | 2.3~ | 205.01 | 206.85 | 201.32 | ➖ NEITHER - closed 15:15 at +0.14R | 0.14 | 113 |
| ADANIPORTS 27Oct 1720 PE | 10:05 | 5/5 | 27.9~ | 27.9~ | 20.7~ | 46.1~ | 29.7~ | 1,711.50 | 1,725.90 | 1,682.69 | ➖ NEITHER - closed 15:15 at +0.29R | 0.29 | 755 |
| NESTLEIND 27Oct 1160 PE | 10:05 | 5/5 | 17.5~ | 17.5~ | 13.6~ | 27.0~ | 18.4~ | 1,168.40 | 1,178.13 | 1,148.94 | ➖ NEITHER - closed 15:15 at +0.36R | 0.36 | 426 |
| SHRIRAMFIN 27Oct 890 PE | 10:05 | 5/5 | 18.1~ | 18.1~ | 13.1~ | 31.0~ | 30.8~ | 885.25 | 895.51 | 864.73 | ✅ YES - reached TARGET at 14:40 | 2.00 | 10,376 |
| HINDUNILVR 27Oct 1800 PE | 10:05 | 5/5 | 18.5~ | 18.5~ | 13.3~ | 32.5~ | 18.5~ | 1,805.00 | 1,817.92 | 1,779.16 | ➖ NEITHER - closed 15:15 at +0.08R | 0.08 | -81 |
| TMPV 27Oct 260 PE | 10:05 | 5/5 | 2.6~ | 2.6~ | 1.8~ | 4.9~ | 2.1~ | 262.00 | 264.34 | 257.32 | ➖ NEITHER - closed 15:15 at -0.51R | -0.51 | -903 |
| TITAN 27Oct 4250 PE | 10:05 | 5/5 | 49.3~ | 49.3~ | 33.6~ | 91.3~ | 42.3~ | 4,238.40 | 4,271.47 | 4,172.25 | ➖ NEITHER - closed 15:15 at -0.35R | -0.35 | -1,280 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-23/options_1005.json), [stocks_1005.json](output_upstox/2026-10-23/stocks_1005.json) · [full review](output_upstox/2026-10-23/review.md)

### 2026-10-22 · market BEARISH · backtest replay

3 picks · ✅ 0 target · ❌ 3 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 0% · avg -1.00R · P&L ₹-5,840

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRENT 27Oct 2750 PE | 10:05 | 5/5 | 64.9~ | 64.9~ | 53.7~ | 90.9~ | 53.9~ | 2,758.50 | 2,783.75 | 2,708.01 | ❌ NO - hit STOP LOSS at 10:20 | -1.00 | -2,563 |
| SBILIFE 27Oct 1620 PE | 10:05 | 5/5 | 13.6~ | 13.6~ | 8.6~ | 28.3~ | 8.6~ | 1,624.70 | 1,637.89 | 1,598.33 | ❌ NO - hit STOP LOSS at 10:35 | -1.00 | -1,921 |
| HDFCBANK 27Oct 690 PE | 10:05 | 5/5 | 6.2~ | 6.2~ | 4.2~ | 11.9~ | 4.2~ | 694.30 | 699.93 | 683.04 | ❌ NO - hit STOP LOSS at 10:35 | -1.00 | -1,356 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-22/options_1005.json), [stocks_1005.json](output_upstox/2026-10-22/stocks_1005.json) · [full review](output_upstox/2026-10-22/review.md)

### 2026-10-21 · market BEARISH · backtest replay

10 picks · ✅ 8 target · ❌ 0 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 90% · avg 1.68R · P&L ₹40,972

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRENT 27Oct 2850 PE | 10:05 | 5/5 | 69.8~ | 69.8~ | 60.2~ | 91.2~ | 91.0~ | 2,864.30 | 2,886.18 | 2,820.55 | ✅ YES - reached TARGET at 12:15 | 2.00 | 4,673 |
| TITAN 27Oct 4400 PE | 10:05 | 3/5 | 54.7~ | 54.7~ | 43.4~ | 81.9~ | 81.7~ | 4,409.10 | 4,435.20 | 4,356.90 | ✅ YES - reached TARGET at 12:15 | 2.00 | 4,654 |
| APOLLOHOSP 27Oct 7700 PE | 10:05 | 5/5 | 153.3~ | 153.3~ | 131.4~ | 202.1~ | 201.9~ | 7,698.00 | 7,744.51 | 7,604.98 | ✅ YES - reached TARGET at 11:35 | 2.00 | 5,987 |
| COALINDIA 27Oct 410 PE | 10:05 | 5/5 | 4.8~ | 4.8~ | 3.9~ | 7.1~ | 7.1~ | 410.65 | 412.81 | 406.33 | ✅ YES - reached TARGET at 12:10 | 2.00 | 2,958 |
| NESTLEIND 27Oct 1240 PE | 10:05 | 5/5 | 29.6~ | 29.6~ | 25.6~ | 38.7~ | 38.5~ | 1,235.00 | 1,243.18 | 1,218.63 | ✅ YES - reached TARGET at 12:50 | 2.00 | 4,357 |
| M&M 27Oct 2850 PE | 10:05 | 5/5 | 33.9~ | 33.9~ | 24.6~ | 58.5~ | 28.4~ | 2,863.10 | 2,886.81 | 2,815.68 | ➖ NEITHER - closed 15:15 at -0.50R | -0.50 | -1,167 |
| TMPV 27Oct 275 PE | 10:05 | 5/5 | 3.6~ | 3.6~ | 2.8~ | 5.5~ | 5.5~ | 276.65 | 278.63 | 272.69 | ✅ YES - reached TARGET at 12:45 | 2.00 | 3,007 |
| ADANIPORTS 27Oct 1760 PE | 10:05 | 5/5 | 29.1~ | 29.1~ | 23.1~ | 43.4~ | 43.3~ | 1,761.60 | 1,774.92 | 1,734.95 | ✅ YES - reached TARGET at 12:20 | 2.00 | 6,681 |
| BAJAJ-AUTO 27Oct 10250 PE | 10:05 | 5/5 | 239.5~ | 239.5~ | 200.4~ | 328.8~ | 327.9~ | 10,187.00 | 10,263.83 | 10,033.34 | ✅ YES - reached TARGET at 12:35 | 2.00 | 6,541 |
| HINDALCO 27Oct 900 PE | 10:05 | 5/5 | 14.1~ | 14.1~ | 11.0~ | 21.9~ | 18.9~ | 898.35 | 905.12 | 884.81 | ➖ NEITHER - closed 15:15 at +1.34R | 1.34 | 3,281 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-21/options_1005.json), [stocks_1005.json](output_upstox/2026-10-21/stocks_1005.json) · [full review](output_upstox/2026-10-21/review.md)

### 2026-10-19 · market BULLISH · backtest replay

1 picks · ✅ 0 target · ❌ 1 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 0% · avg -1.00R · P&L ₹-1,735

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| ULTRACEMCO BUY | 10:05 | 11,132.00 | 10,925.00 | 11,546.00 | ❌ NO - hit STOP LOSS at 12:40 | -1.00 | -1,735 |

Files: [options_1005.json](output_upstox/2026-10-19/options_1005.json), [stocks_1005.json](output_upstox/2026-10-19/stocks_1005.json) · [full review](output_upstox/2026-10-19/review.md)

### 2026-10-16 · market BULLISH · backtest replay

12 picks · ✅ 0 target · ❌ 2 stop · ➖ 10 closed 15:15 · ⛔ 0 not filled · win 58% · avg 0.04R · P&L ₹1,246

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| TECHM BUY | 10:05 | 1,762.80 | 1,690.10 | 1,908.20 | ➖ NEITHER - closed 15:15 at +0.26R | 0.26 | 454 |
| WIPRO BUY | 10:05 | 182.71 | 170.00 | 208.13 | ➖ NEITHER - closed 15:15 at +0.16R | 0.16 | 282 |
| BHARTIARTL BUY | 10:05 | 1,887.00 | 1,857.70 | 1,945.60 | ➖ NEITHER - closed 15:15 at +0.38R | 0.38 | 490 |
| JIOFIN BUY | 10:05 | 216.72 | 213.11 | 223.94 | ➖ NEITHER - closed 15:15 at -0.13R | -0.13 | -299 |
| M&M BUY | 10:05 | 2,899.60 | 2,837.00 | 3,024.80 | ➖ NEITHER - closed 15:15 at +0.30R | 0.30 | 498 |

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JSWSTEEL 27Oct 1220 CE | 10:05 | 5/5 | 24.3~ | 24.3~ | 19.7~ | 35.3~ | 24.2~ | 1,216.20 | 1,206.37 | 1,235.86 | ➖ NEITHER - closed 15:15 at +0.02R | 0.02 | -196 |
| M&M 27Oct 2900 CE | 10:05 | 5/5 | 56.3~ | 56.3~ | 43.0~ | 89.2~ | 66.0~ | 2,899.60 | 2,872.31 | 2,954.18 | ➖ NEITHER - closed 15:15 at +0.68R | 0.68 | 1,867 |
| HCLTECH 27Oct 1380 CE | 10:05 | 5/5 | 39.0~ | 39.0~ | 32.5~ | 54.0~ | 37.5~ | 1,373.30 | 1,359.70 | 1,400.50 | ➖ NEITHER - closed 15:15 at -0.17R | -0.17 | -707 |
| BHARTIARTL 27Oct 1880 CE | 10:05 | 5/5 | 45.2~ | 45.2~ | 38.2~ | 61.2~ | 51.1~ | 1,887.00 | 1,873.76 | 1,913.47 | ➖ NEITHER - closed 15:15 at +0.83R | 0.83 | 2,710 |
| HDFCBANK 27Oct 730 CE | 10:05 | 5/5 | 15.9~ | 15.9~ | 13.2~ | 22.2~ | 13.1~ | 732.70 | 727.58 | 742.93 | ❌ NO - hit STOP LOSS at 12:50 | -1.00 | -1,877 |
| HINDALCO 27Oct 900 CE | 10:05 | 5/5 | 21.2~ | 21.2~ | 17.6~ | 29.5~ | 21.6~ | 903.80 | 897.01 | 917.38 | ➖ NEITHER - closed 15:15 at +0.15R | 0.15 | 176 |
| TATASTEEL 27Oct 177.5 CE | 10:05 | 5/5 | 4.0~ | 4.0~ | 3.2~ | 5.8~ | 3.2~ | 178.00 | 176.54 | 180.91 | ❌ NO - hit STOP LOSS at 10:55 | -1.00 | -2,154 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-16/options_1005.json), [stocks_1005.json](output_upstox/2026-10-16/stocks_1005.json) · [full review](output_upstox/2026-10-16/review.md)

### 2026-10-15 · market BULLISH · backtest replay

7 picks · ✅ 0 target · ❌ 0 stop · ➖ 7 closed 15:15 · ⛔ 0 not filled · win 29% · avg -0.10R · P&L ₹-1,461

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| TECHM BUY | 10:05 | 1,631.00 | 1,596.10 | 1,700.80 | ➖ NEITHER - closed 15:15 at +0.54R | 0.54 | 997 |
| CIPLA BUY | 10:05 | 1,329.80 | 1,310.60 | 1,368.20 | ➖ NEITHER - closed 15:15 at -0.48R | -0.48 | -780 |
| BHARTIARTL BUY | 10:05 | 1,851.00 | 1,795.10 | 1,962.80 | ➖ NEITHER - closed 15:15 at +0.01R | 0.01 | -51 |
| HINDALCO BUY | 10:05 | 885.00 | 857.15 | 940.70 | ➖ NEITHER - closed 15:15 at +0.31R | 0.31 | 548 |
| HCLTECH BUY | 10:05 | 1,365.10 | 1,328.30 | 1,438.70 | ➖ NEITHER - closed 15:15 at -0.14R | -0.14 | -349 |
| INFY BUY | 10:05 | 1,120.15 | 1,095.80 | 1,168.85 | ➖ NEITHER - closed 15:15 at -0.58R | -0.58 | -1,232 |
| TCS BUY | 10:05 | 2,367.40 | 2,335.00 | 2,432.20 | ➖ NEITHER - closed 15:15 at -0.38R | -0.38 | -595 |

Files: [options_1005.json](output_upstox/2026-10-15/options_1005.json), [stocks_1005.json](output_upstox/2026-10-15/stocks_1005.json) · [full review](output_upstox/2026-10-15/review.md)

### 2026-10-14 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-10-14/options_1005.json), [stocks_1005.json](output_upstox/2026-10-14/stocks_1005.json) · [full review](output_upstox/2026-10-14/review.md)

### 2026-10-13 · market BULLISH · backtest replay

5 picks · ✅ 0 target · ❌ 0 stop · ➖ 5 closed 15:15 · ⛔ 0 not filled · win 100% · avg 0.34R · P&L ₹2,819

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| HCLTECH BUY | 10:05 | 1,283.10 | 1,238.20 | 1,372.90 | ➖ NEITHER - closed 15:15 at +0.82R | 0.82 | 1,568 |
| TCS BUY | 10:05 | 2,239.90 | 2,155.00 | 2,409.70 | ➖ NEITHER - closed 15:15 at +0.26R | 0.26 | 454 |
| HINDALCO BUY | 10:05 | 895.05 | 882.65 | 919.85 | ➖ NEITHER - closed 15:15 at +0.24R | 0.24 | 245 |
| JIOFIN BUY | 10:05 | 216.91 | 212.73 | 225.27 | ➖ NEITHER - closed 15:15 at +0.08R | 0.08 | 79 |
| ADANIENT BUY | 10:05 | 2,668.90 | 2,610.00 | 2,786.70 | ➖ NEITHER - closed 15:15 at +0.28R | 0.28 | 473 |

Files: [options_1005.json](output_upstox/2026-10-13/options_1005.json), [stocks_1005.json](output_upstox/2026-10-13/stocks_1005.json) · [full review](output_upstox/2026-10-13/review.md)

### 2026-10-12 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-10-12/options_1005.json), [stocks_1005.json](output_upstox/2026-10-12/stocks_1005.json) · [full review](output_upstox/2026-10-12/review.md)

### 2026-10-09 · market BULLISH · backtest replay

3 picks · ✅ 0 target · ❌ 0 stop · ➖ 3 closed 15:15 · ⛔ 0 not filled · win 100% · avg 0.18R · P&L ₹807

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| ADANIPORTS BUY | 10:05 | 1,752.30 | 1,699.10 | 1,858.70 | ➖ NEITHER - closed 15:15 at +0.15R | 0.15 | 235 |
| EICHERMOT BUY | 10:05 | 6,987.00 | 6,801.00 | 7,359.00 | ➖ NEITHER - closed 15:15 at +0.31R | 0.31 | 503 |
| ADANIENT BUY | 10:05 | 2,627.00 | 2,582.30 | 2,716.40 | ➖ NEITHER - closed 15:15 at +0.09R | 0.09 | 70 |

Files: [options_1005.json](output_upstox/2026-10-09/options_1005.json), [stocks_1005.json](output_upstox/2026-10-09/stocks_1005.json) · [full review](output_upstox/2026-10-09/review.md)

### 2026-10-08 · market BEARISH · backtest replay

9 picks · ✅ 8 target · ❌ 0 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 100% · avg 1.79R · P&L ₹32,727

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JIOFIN 27Oct 215 PE | 10:05 | 5/5 | 4.7~ | 4.7~ | 4.1~ | 6.1~ | 6.1~ | 213.94 | 215.24 | 211.34 | ✅ YES - reached TARGET at 12:20 | 2.00 | 3,247 |
| JSWSTEEL 27Oct 1220 PE | 10:05 | 5/5 | 32.7~ | 32.7~ | 28.4~ | 42.5~ | 42.5~ | 1,212.50 | 1,221.37 | 1,194.77 | ✅ YES - reached TARGET at 11:10 | 2.00 | 6,462 |
| RELIANCE 27Oct 1200 PE | 10:05 | 5/5 | 28.0~ | 28.0~ | 25.2~ | 34.1~ | 34.1~ | 1,192.80 | 1,198.47 | 1,181.47 | ✅ YES - reached TARGET at 11:25 | 2.00 | 2,975 |
| BHARTIARTL 27Oct 1820 PE | 10:05 | 5/5 | 40.5~ | 40.5~ | 35.0~ | 53.0~ | 52.9~ | 1,820.40 | 1,832.71 | 1,795.77 | ✅ YES - reached TARGET at 14:55 | 2.00 | 5,769 |
| COALINDIA 27Oct 410 PE | 10:05 | 5/5 | 9.6~ | 9.6~ | 8.6~ | 11.9~ | 11.9~ | 409.20 | 411.40 | 404.80 | ✅ YES - reached TARGET at 11:25 | 2.00 | 2,954 |
| ADANIPORTS 27Oct 1700 PE | 10:05 | 5/5 | 59.4~ | 59.4~ | 51.7~ | 76.7~ | 60.2~ | 1,700.40 | 1,717.48 | 1,666.24 | ➖ NEITHER - closed 15:15 at +0.14R | 0.14 | 270 |
| NIFTY 13Oct 22450 PE | 10:05 | 5/5 | 130.4~ | 130.4~ | 102.9~ | 196.9~ | 196.8~ | 22,467.60 | 22,531.57 | 22,339.66 | ✅ YES - reached TARGET at 11:25 | 2.00 | 4,248 |
| GRASIM 27Oct 2900 PE | 10:05 | 5/5 | 62.2~ | 62.2~ | 55.4~ | 77.3~ | 77.3~ | 2,891.40 | 2,905.87 | 2,862.45 | ✅ YES - reached TARGET at 11:25 | 2.00 | 3,679 |
| TMPV 27Oct 280 PE | 10:05 | 5/5 | 7.3~ | 7.3~ | 6.4~ | 9.3~ | 9.3~ | 280.75 | 282.79 | 276.67 | ✅ YES - reached TARGET at 11:25 | 2.00 | 3,122 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-08/options_1005.json), [stocks_1005.json](output_upstox/2026-10-08/stocks_1005.json) · [full review](output_upstox/2026-10-08/review.md)

### 2026-10-07 · market BEARISH · backtest replay

2 picks · ✅ 0 target · ❌ 1 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 0% · avg -0.67R · P&L ₹-2,762

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADANIPORTS 27Oct 1760 PE | 10:05 | 5/5 | 58.6~ | 58.6~ | 54.1~ | 68.1~ | 54.1~ | 1,767.60 | 1,777.74 | 1,747.32 | ❌ NO - hit STOP LOSS at 10:20 | -1.00 | -2,218 |
| ONGC 27Oct 222.5 PE | 10:05 | 5/5 | 4.6~ | 4.6~ | 4.1~ | 5.9~ | 4.4~ | 221.60 | 222.76 | 219.29 | ➖ NEITHER - closed 15:15 at -0.34R | -0.34 | -544 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-10-07/options_1005.json), [stocks_1005.json](output_upstox/2026-10-07/stocks_1005.json) · [full review](output_upstox/2026-10-07/review.md)

### 2026-10-06 · market SIDEWAYS · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-10-06/options_1005.json), [stocks_1005.json](output_upstox/2026-10-06/stocks_1005.json) · [full review](output_upstox/2026-10-06/review.md)

### 2026-10-05 · market BULLISH · backtest replay

2 picks · ✅ 0 target · ❌ 0 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 0% · avg -0.48R · P&L ₹-2,040

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| BAJFINANCE BUY | 10:05 | 989.00 | 962.55 | 1,041.90 | ➖ NEITHER - closed 15:15 at -0.68R | -0.68 | -1,431 |
| TITAN BUY | 10:05 | 4,604.00 | 4,505.80 | 4,800.40 | ➖ NEITHER - closed 15:15 at -0.27R | -0.27 | -610 |

Files: [options_1005.json](output_upstox/2026-10-05/options_1005.json), [stocks_1005.json](output_upstox/2026-10-05/stocks_1005.json) · [full review](output_upstox/2026-10-05/review.md)

### 2026-10-01 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-10-01/options_1005.json), [stocks_1005.json](output_upstox/2026-10-01/stocks_1005.json) · [full review](output_upstox/2026-10-01/review.md)

### 2026-09-30 · market SIDEWAYS · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-30/options_1005.json), [stocks_1005.json](output_upstox/2026-09-30/stocks_1005.json) · [full review](output_upstox/2026-09-30/review.md)

### 2026-09-29 · market BEARISH · backtest replay

10 picks · ✅ 1 target · ❌ 7 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 30% · avg -0.39R · P&L ₹-6,393

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JIOFIN 27Oct 215 PE | 10:05 | 5/5 | 4.6~ | 4.6~ | 4.0~ | 6.2~ | 4.0~ | 215.47 | 217.10 | 212.20 | ❌ NO - hit STOP LOSS at 10:40 | -1.00 | -1,683 |
| ITC 27Oct 265 PE | 10:05 | 5/5 | 8.6~ | 8.6~ | 8.0~ | 9.8~ | 8.0~ | 263.90 | 265.14 | 261.42 | ❌ NO - hit STOP LOSS at 11:30 | -1.00 | -1,097 |
| SBIN 27Oct 960 PE | 10:05 | 5/5 | 24.1~ | 24.1~ | 21.5~ | 29.8~ | 21.5~ | 956.20 | 961.77 | 945.06 | ❌ NO - hit STOP LOSS at 11:30 | -1.00 | -2,038 |
| HCLTECH 27Oct 1240 PE | 10:05 | 5/5 | 42.4~ | 42.4~ | 38.3~ | 51.2~ | 44.8~ | 1,233.60 | 1,242.21 | 1,216.37 | ➖ NEITHER - closed 15:15 at +0.60R | 0.60 | 885 |
| NIFTY 06Oct 22600 PE | 10:05 | 5/5 | 166.0~ | 166.0~ | 137.7~ | 231.9~ | 137.6~ | 22,584.75 | 22,646.14 | 22,461.97 | ❌ NO - hit STOP LOSS at 11:10 | -1.00 | -1,919 |
| JSWSTEEL 27Oct 1240 PE | 10:05 | 5/5 | 29.1~ | 29.1~ | 26.0~ | 36.2~ | 26.0~ | 1,249.20 | 1,256.97 | 1,233.65 | ❌ NO - hit STOP LOSS at 11:10 | -1.00 | -2,219 |
| HINDUNILVR 27Oct 1880 PE | 10:05 | 5/5 | 38.2~ | 38.2~ | 32.4~ | 51.7~ | 41.3~ | 1,875.50 | 1,888.48 | 1,849.54 | ➖ NEITHER - closed 15:15 at +0.52R | 0.52 | 861 |
| BAJFINANCE 27Oct 960 PE | 10:05 | 5/5 | 32.9~ | 32.9~ | 30.0~ | 39.1~ | 30.0~ | 963.40 | 969.97 | 950.25 | ❌ NO - hit STOP LOSS at 11:10 | -1.00 | -2,252 |
| RELIANCE 27Oct 1180 PE | 10:05 | 5/5 | 24.6~ | 24.6~ | 22.2~ | 29.9~ | 22.2~ | 1,185.80 | 1,191.64 | 1,174.12 | ❌ NO - hit STOP LOSS at 10:55 | -1.00 | -1,283 |
| TITAN 27Oct 4750 PE | 10:05 | 5/5 | 87.3~ | 87.3~ | 76.1~ | 112.8~ | 112.6~ | 4,760.00 | 4,786.73 | 4,706.54 | ✅ YES - reached TARGET at 14:00 | 2.00 | 4,353 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-29/options_1005.json), [stocks_1005.json](output_upstox/2026-09-29/stocks_1005.json) · [full review](output_upstox/2026-09-29/review.md)

### 2026-09-28 · market BEARISH · backtest replay

10 picks · ✅ 2 target · ❌ 1 stop · ➖ 7 closed 15:15 · ⛔ 0 not filled · win 70% · avg 0.69R · P&L ₹15,345

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SBILIFE 29Sep 1740 PE | 10:05 | 5/5 | 15.0~ | 15.0~ | 9.3~ | 30.5~ | 20.2~ | 1,734.90 | 1,746.26 | 1,712.19 | ➖ NEITHER - closed 15:15 at +0.87R | 0.87 | 1,867 |
| ITC 29Sep 265 PE | 10:05 | 5/5 | 1.2~ | 1.2~ | 0.8~ | 2.2~ | 1.1~ | 266.35 | 267.46 | 264.13 | ➖ NEITHER - closed 15:15 at +0.18R | 0.18 | -333 |
| JIOFIN 29Sep 225 PE | 10:05 | 4/5 | 1.5~ | 1.5~ | 0.9~ | 3.4~ | 3.4~ | 224.08 | 225.30 | 221.63 | ✅ YES - reached TARGET at 12:55 | 2.00 | 4,380 |
| HDFCBANK 29Sep 720 PE | 10:05 | 5/5 | 2.8~ | 2.8~ | 1.4~ | 7.2~ | 3.9~ | 722.05 | 725.97 | 714.22 | ➖ NEITHER - closed 15:15 at +0.78R | 0.78 | 1,373 |
| TATACONSUM 29Sep 960 PE | 10:05 | 5/5 | 2.0~ | 2.0~ | 0.6~ | 9.2~ | 6.0~ | 964.10 | 970.36 | 951.59 | ➖ NEITHER - closed 15:15 at +1.36R | 1.36 | 4,268 |
| ADANIPORTS 29Sep 1760 PE | 10:05 | 5/5 | 14.6~ | 14.6~ | 10.3~ | 25.1~ | 24.9~ | 1,766.60 | 1,776.93 | 1,745.94 | ✅ YES - reached TARGET at 11:45 | 2.00 | 4,863 |
| ICICIBANK 29Sep 1300 PE | 10:05 | 5/5 | 3.9~ | 3.9~ | 1.3~ | 15.1~ | 3.8~ | 1,302.00 | 1,310.34 | 1,285.32 | ➖ NEITHER - closed 15:15 at +0.08R | 0.08 | -141 |
| SBIN 29Sep 960 PE | 10:05 | 5/5 | 3.0~ | 3.0~ | 1.4~ | 8.7~ | 3.5~ | 964.30 | 969.79 | 953.33 | ➖ NEITHER - closed 15:15 at +0.42R | 0.42 | 298 |
| TRENT 29Sep 2650 PE | 10:05 | 5/5 | 24.3~ | 24.3~ | 11.6~ | 60.9~ | 26.9~ | 2,630.50 | 2,651.35 | 2,588.79 | ➖ NEITHER - closed 15:15 at +0.22R | 0.22 | 518 |
| TCS 29Sep 2060 PE | 10:05 | 5/5 | 15.2~ | 15.2~ | 8.0~ | 37.7~ | 7.7~ | 2,059.40 | 2,076.39 | 2,025.41 | ❌ NO - hit STOP LOSS at 12:25 | -1.00 | -1,746 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-28/options_1005.json), [stocks_1005.json](output_upstox/2026-09-28/stocks_1005.json) · [full review](output_upstox/2026-09-28/review.md)

### 2026-09-25 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-25/options_1005.json), [stocks_1005.json](output_upstox/2026-09-25/stocks_1005.json) · [full review](output_upstox/2026-09-25/review.md)

### 2026-09-24 · market BEARISH · backtest replay

3 picks · ✅ 1 target · ❌ 0 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 67% · avg 0.96R · P&L ₹4,478

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BHARTIARTL 29Sep 1820 PE | 10:05 | 5/5 | 28.7~ | 28.7~ | 25.2~ | 36.3~ | 36.0~ | 1,816.10 | 1,823.09 | 1,802.13 | ✅ YES - reached TARGET at 13:45 | 2.00 | 3,367 |
| HINDUNILVR 29Sep 1940 PE | 10:05 | 5/5 | 19.8~ | 19.8~ | 15.6~ | 29.8~ | 19.7~ | 1,930.70 | 1,938.46 | 1,915.17 | ➖ NEITHER - closed 15:15 at +0.04R | 0.04 | -93 |
| ADANIPORTS 29Sep 1780 PE | 10:05 | 5/5 | 32.9~ | 32.9~ | 28.9~ | 41.4~ | 35.6~ | 1,787.40 | 1,796.22 | 1,769.75 | ➖ NEITHER - closed 15:15 at +0.84R | 0.84 | 1,205 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-24/options_1005.json), [stocks_1005.json](output_upstox/2026-09-24/stocks_1005.json) · [full review](output_upstox/2026-09-24/review.md)

### 2026-09-23 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-23/options_1005.json), [stocks_1005.json](output_upstox/2026-09-23/stocks_1005.json) · [full review](output_upstox/2026-09-23/review.md)

### 2026-09-22 · market SIDEWAYS · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-22/options_1005.json), [stocks_1005.json](output_upstox/2026-09-22/stocks_1005.json) · [full review](output_upstox/2026-09-22/review.md)

### 2026-09-21 · market BEARISH · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-21/options_1005.json), [stocks_1005.json](output_upstox/2026-09-21/stocks_1005.json) · [full review](output_upstox/2026-09-21/review.md)

### 2026-09-18 · market SIDEWAYS · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-18/options_1005.json), [stocks_1005.json](output_upstox/2026-09-18/stocks_1005.json) · [full review](output_upstox/2026-09-18/review.md)

### 2026-09-17 · market BULLISH · backtest replay

2 picks · ✅ 0 target · ❌ 0 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 50% · avg -0.07R · P&L ₹-422

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| ETERNAL BUY | 10:05 | 326.55 | 318.25 | 343.15 | ➖ NEITHER - closed 15:15 at -0.42R | -0.42 | -903 |
| HDFCLIFE BUY | 10:05 | 551.25 | 529.95 | 593.85 | ➖ NEITHER - closed 15:15 at +0.27R | 0.27 | 480 |

Files: [options_1005.json](output_upstox/2026-09-17/options_1005.json), [stocks_1005.json](output_upstox/2026-09-17/stocks_1005.json) · [full review](output_upstox/2026-09-17/review.md)

### 2026-09-16 · market BEARISH · backtest replay

3 picks · ✅ 0 target · ❌ 3 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 0% · avg -1.00R · P&L ₹-7,344

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KOTAKBANK 29Sep 410 PE | 10:05 | 5/5 | 7.1~ | 7.1~ | 5.7~ | 10.2~ | 5.7~ | 409.70 | 412.63 | 403.83 | ❌ NO - hit STOP LOSS at 10:35 | -1.00 | -2,704 |
| BHARTIARTL 29Sep 1820 PE | 10:05 | 4/5 | 33.9~ | 33.9~ | 30.0~ | 42.4~ | 30.0~ | 1,822.80 | 1,831.46 | 1,805.48 | ❌ NO - hit STOP LOSS at 10:30 | -1.00 | -1,911 |
| NIFTY 22Sep 23200 PE | 10:05 | 4/5 | 160.2~ | 160.2~ | 119.3~ | 264.7~ | 119.4~ | 23,178.15 | 23,268.47 | 22,997.51 | ❌ NO - hit STOP LOSS at 10:50 | -1.00 | -2,728 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-16/options_1005.json), [stocks_1005.json](output_upstox/2026-09-16/stocks_1005.json) · [full review](output_upstox/2026-09-16/review.md)

### 2026-09-15 · market BEARISH · backtest replay

4 picks · ✅ 1 target · ❌ 0 stop · ➖ 3 closed 15:15 · ⛔ 0 not filled · win 100% · avg 1.07R · P&L ₹8,937

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADANIPORTS 29Sep 1740 PE | 10:05 | 5/5 | 49.4~ | 49.4~ | 44.1~ | 60.8~ | 59.0~ | 1,741.10 | 1,752.57 | 1,718.15 | ➖ NEITHER - closed 15:15 at +1.75R | 1.75 | 4,494 |
| SBIN 29Sep 980 PE | 10:05 | 5/5 | 10.1~ | 10.1~ | 8.1~ | 15.2~ | 15.2~ | 981.70 | 986.75 | 971.61 | ✅ YES - reached TARGET at 14:45 | 2.00 | 3,715 |
| ICICIBANK 29Sep 1360 PE | 10:05 | 5/5 | 17.3~ | 17.3~ | 13.6~ | 26.2~ | 17.7~ | 1,356.50 | 1,364.41 | 1,340.69 | ➖ NEITHER - closed 15:15 at +0.13R | 0.13 | 201 |
| SBILIFE 29Sep 1660 PE | 10:05 | 5/5 | 23.0~ | 23.0~ | 19.0~ | 32.8~ | 24.6~ | 1,668.50 | 1,678.74 | 1,648.02 | ➖ NEITHER - closed 15:15 at +0.40R | 0.40 | 527 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-15/options_1005.json), [stocks_1005.json](output_upstox/2026-09-15/stocks_1005.json) · [full review](output_upstox/2026-09-15/review.md)

### 2026-09-11 · market BEARISH · backtest replay

1 picks · ✅ 0 target · ❌ 1 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 0% · avg -1.00R · P&L ₹-1,263

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RELIANCE 29Sep 1260 PE | 10:05 | 5/5 | 17.9~ | 17.9~ | 15.6~ | 23.2~ | 15.5~ | 1,259.10 | 1,264.30 | 1,248.71 | ❌ NO - hit STOP LOSS at 14:25 | -1.00 | -1,263 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-11/options_1005.json), [stocks_1005.json](output_upstox/2026-09-11/stocks_1005.json) · [full review](output_upstox/2026-09-11/review.md)

### 2026-09-10 · market BEARISH · backtest replay

2 picks · ✅ 0 target · ❌ 0 stop · ➖ 2 closed 15:15 · ⛔ 0 not filled · win 100% · avg 1.11R · P&L ₹4,538

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HCLTECH 29Sep 1220 PE | 10:05 | 5/5 | 34.0~ | 34.0~ | 29.0~ | 45.6~ | 41.9~ | 1,214.20 | 1,224.86 | 1,192.89 | ➖ NEITHER - closed 15:15 at +1.43R | 1.43 | 3,086 |
| RELIANCE 29Sep 1280 PE | 10:05 | 5/5 | 21.0~ | 21.0~ | 17.4~ | 29.3~ | 24.0~ | 1,274.70 | 1,282.20 | 1,259.70 | ➖ NEITHER - closed 15:15 at +0.80R | 0.80 | 1,452 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-10/options_1005.json), [stocks_1005.json](output_upstox/2026-09-10/stocks_1005.json) · [full review](output_upstox/2026-09-10/review.md)

### 2026-09-09 · market BEARISH · backtest replay

4 picks · ✅ 0 target · ❌ 3 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 25% · avg -0.47R · P&L ₹-3,828

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M&M 29Sep 3100 PE | 10:05 | 5/5 | 34.8~ | 34.8~ | 29.5~ | 47.4~ | 29.5~ | 3,120.50 | 3,134.91 | 3,091.67 | ❌ NO - hit STOP LOSS at 10:20 | -1.00 | -1,128 |
| KOTAKBANK 29Sep 415 PE | 10:05 | 5/5 | 7.6~ | 7.6~ | 6.6~ | 9.7~ | 6.6~ | 414.75 | 416.89 | 410.47 | ❌ NO - hit STOP LOSS at 14:00 | -1.00 | -2,042 |
| HINDUNILVR 29Sep 1960 PE | 10:05 | 5/5 | 30.3~ | 30.3~ | 26.7~ | 38.5~ | 34.6~ | 1,950.30 | 1,957.73 | 1,935.43 | ➖ NEITHER - closed 15:15 at +1.12R | 1.12 | 1,218 |
| ITC 29Sep 260 PE | 10:05 | 5/5 | 5.5~ | 5.5~ | 5.0~ | 6.6~ | 5.0~ | 261.75 | 262.94 | 259.38 | ❌ NO - hit STOP LOSS at 14:55 | -1.00 | -1,876 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-09/options_1005.json), [stocks_1005.json](output_upstox/2026-09-09/stocks_1005.json) · [full review](output_upstox/2026-09-09/review.md)

### 2026-09-08 · market BEARISH · backtest replay

3 picks · ✅ 1 target · ❌ 2 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 33% · avg 0.00R · P&L ₹302

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M&M 29Sep 3100 PE | 10:05 | 5/5 | 41.9~ | 41.9~ | 33.7~ | 61.9~ | 33.7~ | 3,109.10 | 3,129.54 | 3,068.21 | ❌ NO - hit STOP LOSS at 11:05 | -1.00 | -1,700 |
| BHARTIARTL 29Sep 1840 PE | 10:05 | 5/5 | 53.0~ | 53.0~ | 49.2~ | 61.1~ | 49.1~ | 1,832.20 | 1,840.15 | 1,816.30 | ❌ NO - hit STOP LOSS at 11:40 | -1.00 | -1,939 |
| ICICIBANK 29Sep 1420 PE | 10:05 | 5/5 | 23.4~ | 23.4~ | 20.8~ | 29.2~ | 29.1~ | 1,410.80 | 1,415.96 | 1,400.47 | ✅ YES - reached TARGET at 11:40 | 2.00 | 3,941 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-08/options_1005.json), [stocks_1005.json](output_upstox/2026-09-08/stocks_1005.json) · [full review](output_upstox/2026-09-08/review.md)

### 2026-09-07 · market BEARISH · backtest replay

1 picks · ✅ 0 target · ❌ 0 stop · ➖ 1 closed 15:15 · ⛔ 0 not filled · win 100% · avg 0.74R · P&L ₹1,070

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SBIN 29Sep 1000 PE | 10:05 | 5/5 | 12.3~ | 12.3~ | 10.4~ | 16.9~ | 13.8~ | 1,008.80 | 1,014.23 | 997.95 | ➖ NEITHER - closed 15:15 at +0.74R | 0.74 | 1,070 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-07/options_1005.json), [stocks_1005.json](output_upstox/2026-09-07/stocks_1005.json) · [full review](output_upstox/2026-09-07/review.md)

### 2026-09-04 · market BULLISH · backtest replay

3 picks · ✅ 0 target · ❌ 0 stop · ➖ 3 closed 15:15 · ⛔ 0 not filled · win 33% · avg -0.10R · P&L ₹-676

**Stocks**

| Stock | Signal | Entry | Stop | Target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|
| HDFCLIFE BUY | 10:05 | 544.15 | 533.30 | 565.85 | ➖ NEITHER - closed 15:15 at -0.01R | -0.01 | -110 |
| TRENT BUY | 10:05 | 2,875.90 | 2,833.20 | 2,961.30 | ➖ NEITHER - closed 15:15 at -0.39R | -0.39 | -649 |
| RELIANCE BUY | 10:05 | 1,326.80 | 1,304.10 | 1,372.20 | ➖ NEITHER - closed 15:15 at +0.10R | 0.10 | 83 |

Files: [options_1005.json](output_upstox/2026-09-04/options_1005.json), [stocks_1005.json](output_upstox/2026-09-04/stocks_1005.json) · [full review](output_upstox/2026-09-04/review.md)

### 2026-09-03 · market SIDEWAYS · backtest replay

0 picks · ✅ 0 target · ❌ 0 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win -% · avg -R · P&L ₹-

No picks this day.
Files: [options_1005.json](output_upstox/2026-09-03/options_1005.json), [stocks_1005.json](output_upstox/2026-09-03/stocks_1005.json) · [full review](output_upstox/2026-09-03/review.md)

### 2026-09-02 · market BEARISH · backtest replay

1 picks · ✅ 0 target · ❌ 1 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 0% · avg -1.00R · P&L ₹-2,111

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BHARTIARTL 29Sep 1860 PE | 10:05 | 5/5 | 55.8~ | 55.8~ | 51.7~ | 64.7~ | 51.6~ | 1,859.90 | 1,869.08 | 1,841.54 | ❌ NO - hit STOP LOSS at 12:35 | -1.00 | -2,111 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-02/options_1005.json), [stocks_1005.json](output_upstox/2026-09-02/stocks_1005.json) · [full review](output_upstox/2026-09-02/review.md)

### 2026-09-01 · market BEARISH · backtest replay

1 picks · ✅ 0 target · ❌ 1 stop · ➖ 0 closed 15:15 · ⛔ 0 not filled · win 0% · avg -1.00R · P&L ₹-2,460

**Options**

| Option | Signal | Votes | Buy at (premium) | Filled at | Premium stop | Premium target | Exit premium | Spot entry | Spot stop | Spot target | Result | R | P&L ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BAJFINANCE 29Sep 1060 PE | 10:05 | 5/5 | 35.4~ | 35.4~ | 32.3~ | 42.1~ | 32.3~ | 1,051.90 | 1,058.30 | 1,039.11 | ❌ NO - hit STOP LOSS at 12:30 | -1.00 | -2,460 |

_Options: Buy at = the premium in the pick, Filled at / Exit = the contract's real Upstox price at entry and exit (P&L uses these). Values marked ~ are Black-Scholes estimates (no real price available, e.g. picks made before 27 Nov 2026). Target/stop hits are judged on the exact spot price._

Files: [options_1005.json](output_upstox/2026-09-01/options_1005.json), [stocks_1005.json](output_upstox/2026-09-01/stocks_1005.json) · [full review](output_upstox/2026-09-01/review.md)
