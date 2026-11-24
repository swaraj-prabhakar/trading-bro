"""Central configuration. Every number here is a tunable assumption - change it, re-run
`python -m tradingbro.validate`, and see if the backtest improves."""
import os
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# Market-data source: "yahoo" (default, the original pipeline) or "upstox".
# Each source keeps its own cache, predictions, reviews and result pages so the two can
# run side by side and be compared (python -m tradingbro.compare). Set it with the
# TRADINGBRO_SOURCE environment variable, or run commands through `python -m tradingbro.up`.
SOURCE = os.environ.get("TRADINGBRO_SOURCE", "yahoo").strip().lower()
if SOURCE not in ("yahoo", "upstox"):
    raise SystemExit(f"TRADINGBRO_SOURCE must be 'yahoo' or 'upstox', not {SOURCE!r}")
SOURCE_LABEL = "Upstox" if SOURCE == "upstox" else "Yahoo"
_SFX = "" if SOURCE == "yahoo" else "_" + SOURCE

CACHE_DIR = ROOT / ".cache" if SOURCE == "yahoo" else ROOT / ".cache" / SOURCE
REPORT_DIR = ROOT / ("reports" + ("" if SOURCE == "yahoo" else "/" + SOURCE))
OUTPUT_DIR = ROOT / ("output" + _SFX)    # saved predictions (per day) + end-of-day reviews
RESULT_MD = ROOT / f"Result{_SFX}.md"
PICKS_MD = ROOT / f"Picks{_SFX}.md"
OUTPUT_DIRS = {"yahoo": ROOT / "output", "upstox": ROOT / "output_upstox"}   # for the comparison report

TZ = "Asia/Kolkata"
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
RISK_FREE_RATE = 0.065  # used for Black-Scholes and futures basis

# NSE F&O trading holidays (YYYY-MM-DD). An expiry that falls on one moves to the
# previous trading day. Add the full year's list from nseindia.com.
NSE_HOLIDAYS = {
    "2026-11-24",  # Guru Nanak Jayanti
    "2026-12-25",  # Christmas
    "2027-01-26",  # Republic Day (Upstox lists the Jan-2027 expiry on Mon 25 Jan)
}


@dataclass
class StrategyParams:
    # How many of the 5 strategies must agree before a trade is taken (1..5)
    min_votes: int = 3
    # Entries are only taken inside this window (after the opening range settles)
    entry_start: str = "09:45"
    entry_end: str = "13:30"
    # Every position is squared off at/after this time (intraday only)
    squareoff: str = "15:15"
    # Stop-loss distance = sl_atr_mult x ATR(atr_period) on 5-minute bars
    sl_atr_mult: float = 2.5
    atr_period: int = 14
    # Target distance = rr x stop distance (reward:risk)
    rr: float = 2.0
    # Indicator settings
    ema_fast: int = 9
    ema_slow: int = 21
    rsi_period: int = 14
    rsi_bull: float = 55.0
    rsi_bear: float = 45.0
    st_period: int = 10
    st_mult: float = 3.0
    or_minutes: int = 15

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# Transaction charges (discount-broker style). Rates change with Union Budgets /
# exchange circulars - verify with your broker's calculator. F&O STT is set to the
# higher post-Budget-2026 rates so the backtest stays conservative.
# ---------------------------------------------------------------------------
BROKERAGE_PER_ORDER = 20.0      # flat, or 0.03% if lower (equity/futures)
GST = 0.18                      # on brokerage + exchange txn + SEBI fee
SEBI_FEE = 10 / 1e7             # Rs 10 per crore

CHARGES = {
    "equity": {"stt_sell": 0.00025, "txn": 0.0000297, "stamp_buy": 0.00003},
    "futures": {"stt_sell": 0.0005, "txn": 0.0000173, "stamp_buy": 0.00002},
    "options": {"stt_sell": 0.0015, "txn": 0.0003503, "stamp_buy": 0.00003},
}
