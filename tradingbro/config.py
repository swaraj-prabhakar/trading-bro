"""Central configuration. Every number here is a tunable assumption - change it, re-run
`python -m tradingbro.validate`, and see if the backtest improves."""
import os
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# Market data: the Upstox V3 candle API (tradingbro/upstox_data.py), the only source since 26 Nov 2026
# (Yahoo Finance was dropped). File names keep the "_upstox" suffix so the history stays in one place.
SOURCE = "upstox"
SOURCE_LABEL = "Upstox"
_SFX = "_upstox"

CACHE_DIR = ROOT / ".cache" / SOURCE
REPORT_DIR = ROOT / "reports" / SOURCE
# TRADINGBRO_RUN_DIR redirects predictions, reviews and result pages (used by the
# multi-day replay, python -m tradingbro.replay_days, so it never touches the live record)
OUT_BASE = Path(os.environ["TRADINGBRO_RUN_DIR"]).resolve() if os.environ.get("TRADINGBRO_RUN_DIR") else ROOT

# Profile: "" (default: top 10 per segment, each pick sized on the full capital) or
# "personal" (TRADINGBRO_PROFILE=personal): at most PERSONAL_SLOTS picks per segment, the
# capital split equally between them, and P&L tracked per segment because only ONE
# segment (stocks OR options) is traded with the capital. Kept in its own
# files: output*_personal/, Result*_personal.md, Picks*_personal.md.
PROFILE = os.environ.get("TRADINGBRO_PROFILE", "").strip().lower()
if PROFILE not in ("", "personal"):
    raise SystemExit(f"TRADINGBRO_PROFILE must be empty or 'personal', not {PROFILE!r}")
PERSONAL_SLOTS = 2
_PSFX = "_" + PROFILE if PROFILE else ""

OUTPUT_DIR = OUT_BASE / ("output" + _SFX + _PSFX)    # saved predictions (per day) + end-of-day reviews
RESULT_MD = OUT_BASE / f"Result{_SFX}{_PSFX}.md"
PICKS_MD = OUT_BASE / f"Picks{_SFX}{_PSFX}.md"
MONTHLY_DIR = OUT_BASE / "monthly"                   # one result page per month: monthly/2026-11[_personal].md


def monthly_md(month):
    return MONTHLY_DIR / f"{month}{_PSFX}.md"

TZ = "Asia/Kolkata"
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
RISK_FREE_RATE = 0.065  # used for Black-Scholes option pricing

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
BROKERAGE_PER_ORDER = 20.0      # flat, or 0.03% if lower (equity)
GST = 0.18                      # on brokerage + exchange txn + SEBI fee
SEBI_FEE = 10 / 1e7             # Rs 10 per crore

CHARGES = {
    "equity": {"stt_sell": 0.00025, "txn": 0.0000297, "stamp_buy": 0.00003},
    "options": {"stt_sell": 0.0015, "txn": 0.0003503, "stamp_buy": 0.00003},
}
