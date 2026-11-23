"""NIFTY 50 cash-equity intraday scanner (buy first, sell the same day).

    python -m tradingbro.stocks --capital 50000
    python -m tradingbro.stocks --capital 50000 --date 2026-11-20 --time 10:30   # replay a past day
"""
import math

from . import charges
from .common import base_parser, finish, header, params_from_args, resolve_asof, symbols_arg
from .data import fetch_universe
from .market import describe, market_trend, trend_at
from .engine import signal_at, simulate, stats
from .strategies import add_signals
from .universe import filter_symbols, load_instruments


def analyze(a):
    p = params_from_args(a)
    stocks, _ = load_instruments()
    stocks = filter_symbols(stocks, symbols_arg(a))
    intraday, _, dropped = fetch_universe(stocks, a.refresh)
    asof, mode = resolve_asof(intraday, a)
    mkt = None if a.no_trend else market_trend(p, a.refresh)
    mtrend = trend_at(mkt, asof) if mkt is not None else None
    mdir = mtrend["trend"] if mtrend else None
    against = 0
    risk_budget = a.capital * a.risk_pct / 100

    rows, rejected, unaffordable = [], 0, 0
    for inst in stocks:
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
        if a.max_price and sig.price > a.max_price:
            unaffordable += 1
            continue
        risk_unit = abs(sig.price - sig.stop)
        units = min(math.floor(a.capital * a.leverage / sig.price), math.floor(risk_budget / risk_unit))
        if units < 1:
            unaffordable += 1
            continue
        value = units * sig.price
        cost = charges.round_trip("equity", value, value)
        expected = st["avg_r"] * risk_unit * units - cost
        if st["n"] < a.min_trades or st["avg_r"] <= 0 or expected <= 0:
            rejected += 1
            continue
        row = dict(
            symbol=inst.symbol, upstox=inst.upstox, side="BUY" if sig.direction == 1 else "SELL", signal_time=f"{sig.ts:%H:%M}",
            price=sig.price, stop=sig.stop, target=sig.target, units=units, invest=value,
            max_loss=risk_unit * units + cost,
            risk_pct=(risk_unit * units + cost) / a.capital * 100, max_gain=risk_unit * p.rr * units - cost,
            exp_profit=expected, charges=cost, bt_trades=st["n"], win_pct=st["win_rate"] * 100,
            avg_r=st["avg_r"], pf=st["profit_factor"], votes=f"{abs(sig.votes)}/5",
            strategies="+".join(sig.agreeing),
        )
        if sig.outcome:
            o = sig.outcome
            row.update(actual=f"{o['reason']}@{o['exit_time']}",
                       actual_pnl=sig.direction * (o["exit"] - sig.price) * units - cost)
        rows.append(row)

    rows.sort(key=lambda r: (-int(r["votes"].split("/")[0]), -r["max_gain"]))  # most strategies agreeing, then max gain
    rows = rows[: a.top]

    cols = [("Symbol", "symbol", 0), ("Side", "side", 0), ("At", "signal_time", 0), ("Price", "price", 2),
            ("Stop", "stop", 2), ("Target", "target", 2), ("Qty", "units", 0), ("Invest", "invest", 0),
            ("MaxLoss", "max_loss", 0), ("MaxGain", "max_gain", 0), ("ExpRs", "exp_profit", 0),
            ("BT#", "bt_trades", 0), ("Win%", "win_pct", 0), ("AvgR", "avg_r", 2), ("Votes", "votes", 0), ("Upstox", "upstox", 0)]
    if mode == "replay":
        cols += [("Actual", "actual", 0), ("ActualRs", "actual_pnl", 0)]
        if rows:
            tot = sum(r.get("actual_pnl", 0) for r in rows)
            print_note = f"Replay result if every pick above was traded with its own Rs {a.capital:,.0f}: total Rs {tot:,.0f}"
        else:
            print_note = None
    else:
        print_note = None

    notes = [
        "Qty = min(capital x leverage / price, risk budget / stop distance). Each row assumes you put "
        "your whole capital in that one trade; split the capital if you take several.",
        "ExpRs = backtested average R-multiple for that stock x today's risk - charges.",
        f"{rejected} signal(s) rejected for weak backtest edge; {unaffordable} skipped for price/size limits.",
    ]
    if print_note:
        notes.insert(0, print_note)

    if mtrend:
        notes.append(f"{against} signal(s) skipped for going against the market trend "
                     f"({mtrend['label']}; SIDEWAYS = no trades). Use --no-trend to disable.")
    if mtrend and mtrend["trend"] == -1 and not a.allow_short:
        notes.insert(0, "Market is BEARISH: buy-first trades are skipped. Consider the options scanner (PE) "
                        "or --allow-short.")
    header("stocks", a, asof, mode, p, len(stocks), dropped)
    if mtrend and not a.json:
        print(describe(mtrend))
    payload = dict(kind="stocks", mode=mode, market=mtrend, asof=str(asof), capital=a.capital, params=p.to_dict(),
                   picks=rows, rejected=rejected, unaffordable=unaffordable, dropped=dropped)
    finish("stocks", a, payload, rows, cols, notes)
    return payload


def main(argv=None):
    ap = base_parser("NIFTY 50 intraday stock picks with target, stop and quantity")
    ap.add_argument("--max-price", type=float, default=0, help="Skip stocks above this price (default 0 = no limit)")
    ap.add_argument("--leverage", type=float, default=1.0, help="Intraday (MIS) leverage your broker gives (default 1 = own cash)")
    ap.add_argument("--allow-short", action="store_true", help="Also show intraday short-sell setups")
    analyze(ap.parse_args(argv))


if __name__ == "__main__":
    main()
