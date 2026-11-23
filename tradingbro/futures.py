"""NIFTY 50 stock futures + NIFTY/BANKNIFTY index futures intraday scanner.

    python -m tradingbro.futures --capital 300000
"""
import math

from . import charges
from .common import base_parser, finish, header, params_from_args, resolve_asof, symbols_arg
from .config import RISK_FREE_RATE
from .data import fetch_universe
from .market import describe, market_trend, trend_at
from .engine import signal_at, simulate, stats
from .options_math import next_expiry
from .strategies import add_signals
from .universe import filter_symbols, load_instruments


def analyze(a):
    p = params_from_args(a)
    stocks, indices = load_instruments()
    universe = filter_symbols(indices + stocks, symbols_arg(a))
    intraday, _, dropped = fetch_universe(universe, a.refresh)
    asof, mode = resolve_asof(intraday, a)
    mkt = None if a.no_trend else market_trend(p, a.refresh)
    mtrend = trend_at(mkt, asof) if mkt is not None else None
    mdir = mtrend["trend"] if mtrend else None
    against = 0
    risk_budget = a.capital * a.risk_pct / 100

    rows, rejected, unaffordable = [], 0, 0
    for inst in universe:
        df = intraday.get(inst.yahoo)
        if df is None:
            continue
        df = add_signals(df, p)
        st = stats(simulate(df, p, allow_short=a.allow_short, before_date=asof.date(), market=mkt))
        sig = signal_at(df, asof, p, allow_short=a.allow_short, with_outcome=(mode == "replay"), market_dir=mdir)
        if sig == "against_trend":
            against += 1
            continue
        if sig is None:
            continue
        expiry = next_expiry(asof.date(), "monthly", skip_today=True)  # trade next month on expiry day
        basis = sig.price * RISK_FREE_RATE * max((expiry - asof.date()).days, 0) / 365
        fut = sig.price + basis                     # fair-value estimate; check the live quote
        margin_lot = fut * inst.lot * inst.margin_pct
        lots_cap = math.floor(a.capital / margin_lot)
        if lots_cap < 1:
            unaffordable += 1
            continue
        risk_unit = abs(sig.price - sig.stop)
        lots = min(lots_cap, max(1, math.floor(risk_budget / (risk_unit * inst.lot))))
        qty = lots * inst.lot
        value = fut * qty
        cost = charges.round_trip("futures", value, value)
        expected = st["avg_r"] * risk_unit * qty - cost
        if st["n"] < a.min_trades or st["avg_r"] <= 0 or expected <= 0:
            rejected += 1
            continue
        max_loss = risk_unit * qty + cost
        row = dict(
            symbol=inst.symbol, upstox=inst.upstox, side="BUY" if sig.direction == 1 else "SELL", signal_time=f"{sig.ts:%H:%M}",
            expiry=str(expiry), spot=sig.price, fut_price=fut, stop=sig.stop + basis, target=sig.target + basis,
            lot=inst.lot, lots=lots, qty=qty, margin=margin_lot * lots, max_loss=max_loss,
            risk_pct=max_loss / a.capital * 100, max_gain=risk_unit * p.rr * qty - cost, exp_profit=expected,
            charges=cost, bt_trades=st["n"], win_pct=st["win_rate"] * 100, avg_r=st["avg_r"],
            pf=st["profit_factor"], votes=f"{abs(sig.votes)}/5", strategies="+".join(sig.agreeing),
        )
        if sig.outcome:
            o = sig.outcome
            row.update(actual=f"{o['reason']}@{o['exit_time']}",
                       actual_pnl=sig.direction * (o["exit"] - sig.price) * qty - cost)
        rows.append(row)

    rows.sort(key=lambda r: (-int(r["votes"].split("/")[0]), -r["max_gain"]))  # most strategies agreeing, then max gain
    rows = rows[: a.top]
    cols = [("Symbol", "symbol", 0), ("Side", "side", 0), ("At", "signal_time", 0), ("Fut~", "fut_price", 1),
            ("Stop", "stop", 1), ("Target", "target", 1), ("Lot", "lot", 0), ("Lots", "lots", 0),
            ("Margin", "margin", 0), ("MaxLoss", "max_loss", 0), ("MaxGain", "max_gain", 0), ("Risk%", "risk_pct", 1),
            ("ExpRs", "exp_profit", 0), ("BT#", "bt_trades", 0), ("Win%", "win_pct", 0), ("AvgR", "avg_r", 2), ("Votes", "votes", 0), ("Upstox", "upstox", 0)]
    if mode == "replay":
        cols += [("Actual", "actual", 0), ("ActualRs", "actual_pnl", 0)]
    notes = [
        "Futures levels = spot levels + estimated cost-of-carry basis; place orders on the actual futures quote, "
        "shifting stop/target by (live futures - spot).",
        "Margin is an estimate (margin_pct in data/instruments.json); your broker's SPAN margin is authoritative.",
        f"Risk% > {a.risk_pct:g} means even 1 lot risks more than your --risk-pct budget.",
        f"{rejected} signal(s) rejected for weak backtest edge; {unaffordable} skipped because 1 lot's margin exceeds capital.",
    ]
    if mtrend:
        notes.append(f"{against} signal(s) skipped for going against the market trend "
                     f"({mtrend['label']}; SIDEWAYS = no trades). Use --no-trend to disable.")
    if mtrend and mtrend["trend"] == -1 and not a.allow_short:
        notes.insert(0, "Market is BEARISH: buy-first trades are skipped. Consider the options scanner (PE) "
                        "or --allow-short.")
    header("futures", a, asof, mode, p, len(universe), dropped)
    if mtrend and not a.json:
        print(describe(mtrend))
    payload = dict(kind="futures", mode=mode, market=mtrend, asof=str(asof), capital=a.capital, params=p.to_dict(),
                   picks=rows, rejected=rejected, unaffordable=unaffordable, dropped=dropped)
    finish("futures", a, payload, rows, cols, notes)
    return payload


def main(argv=None):
    ap = base_parser("NIFTY 50 stock & index futures intraday picks")
    ap.add_argument("--allow-short", action="store_true", help="Also show sell-first (short) futures setups")
    analyze(ap.parse_args(argv))


if __name__ == "__main__":
    main()
