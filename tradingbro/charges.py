"""Round-trip transaction cost estimates (brokerage, STT, exchange, SEBI, stamp, GST)."""
from .config import BROKERAGE_PER_ORDER, CHARGES, GST, SEBI_FEE


def round_trip(segment: str, buy_value: float, sell_value: float) -> float:
    c = CHARGES[segment]
    if segment == "options":
        brokerage = 2 * BROKERAGE_PER_ORDER
    else:
        brokerage = min(BROKERAGE_PER_ORDER, 0.0003 * buy_value) + min(BROKERAGE_PER_ORDER, 0.0003 * sell_value)
    turnover = buy_value + sell_value
    txn = c["txn"] * turnover
    sebi = SEBI_FEE * turnover
    stt = c["stt_sell"] * sell_value
    stamp = c["stamp_buy"] * buy_value
    gst = GST * (brokerage + txn + sebi)
    return brokerage + txn + sebi + stt + stamp + gst
