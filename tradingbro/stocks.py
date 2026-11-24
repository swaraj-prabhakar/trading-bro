"""NIFTY 50 cash-equity intraday scanner (buy first, sell the same day).
Default method: ORB-30 + relative volume (tradingbro/stock_orb.py); --method ensemble = original.

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
from . import stock_orb


def analyze_orb(a):
    """Default stock method: ORB-30 + relative volume (see tradingbro/stock_orb.py)."""
    p = params_from_args(a)
    stocks, _ = load_instruments()
    stocks = filter_symbols(stocks, symbols_arg(a))
    intraday, _, dropped = fetch_universe(stocks, a.refresh)
    asof, mode = resolve_asof(intraday, a)
    mkt = None if a.no_trend else market_trend(p, a.refresh)
    mtrend = trend_at(mkt, asof) if mkt is not None else None
    mdir = mtrend["trend"] if mtrend else None
    risk_budget = a.capital * a.risk_pct / 100
    prepared = {i.symbol: stock_orb.add_orb_columns(intraday[i.yahoo]) for i in stocks if i.yahoo in intraday}
    bt_r, bt_ret = stock_orb.universe_backtest(prepared, f"{asof:%H:%M}", p, mkt, before_date=asof.date())
    bt_n = len(bt_r)
    bt_avg = float(bt_r.mean()) if bt_n else 0.0
    gains, losses = bt_r[bt_r > 0].sum(), -bt_r[bt_r < 0].sum()
    bt_pf = float(gains / losses) if losses > 0 else float("inf")
    bt_win = float((bt_r > 0).mean() * 100) if bt_n else 0.0

    rows, rejected, unaffordable, against = [], 0, 0, 0
    for inst in stocks:
        df = prepared.get(inst.symbol)
        if df is None:
            continue
        sig = stock_orb.signal_at(df, asof, p, market_dir=mdir, with_outcome=(mode == "replay"))
        if sig == "against_trend":
            against += 1
            continue
        if sig is None:
            continue
        if a.max_price and sig.price > a.max_price:
            unaffordable += 1
            continue
        risk_unit = sig.price - sig.stop
        units = min(math.floor(a.capital * a.leverage / sig.price), math.floor(risk_budget / risk_unit))
        if units < 1:
            unaffordable += 1
            continue
        value = units * sig.price
        cost = charges.round_trip("equity", value, value)
        expected = bt_avg * risk_unit * units - cost
        if bt_n < a.min_trades or bt_avg <= 0 or expected <= 0:
            rejected += 1
            continue
        row = dict(
            symbol=inst.symbol, upstox=inst.upstox, side="BUY", signal_time=f"{sig.ts:%H:%M}",
            price=sig.price, stop=sig.stop, target=sig.target, units=units, invest=value,
            max_loss=risk_unit * units + cost, risk_pct=(risk_unit * units + cost) / a.capital * 100,
            max_gain=risk_unit * p.rr * units - cost, exp_profit=expected, charges=cost, bt_trades=bt_n,
            win_pct=bt_win, avg_r=bt_avg, pf=bt_pf,
            votes=stock_orb.METHOD, method=stock_orb.METHOD, rvol=sig.rvol, strategies="orb30+rvol",
        )
        if sig.outcome:
            o = sig.outcome
            row.update(actual=f"{o['reason']}@{o['exit_time']}", actual_pnl=(o["exit"] - sig.price) * units - cost)
        rows.append(row)

    rows.sort(key=lambda r: -r["rvol"])                      # strongest relative volume first
    rows = rows[: a.top]
    cols = [("Symbol", "symbol", 0), ("At", "signal_time", 0), ("Price", "price", 2), ("Stop", "stop", 2),
            ("Target", "target", 2), ("Qty", "units", 0), ("Invest", "invest", 0), ("MaxLoss", "max_loss", 0),
            ("MaxGain", "max_gain", 0), ("ExpRs", "exp_profit", 0), ("RVOL", "rvol", 1), ("Upstox", "upstox", 0)]
    notes = [f"Method {stock_orb.METHOD}: buy when price closes above the 09:15-09:45 high with volume >= "
             f"{stock_orb.RVOL_MIN}x normal for the time of day; stop = opening-range low; target {p.rr}R.",
             f"Method backtest over the downloaded sessions (all stocks, same clock time, trend filter): {bt_n} trades, "
             f"win {bt_win:.0f}%, avg {bt_avg:+.2f}R, profit factor {bt_pf:.2f}.",
             "Qty = min(capital x leverage / price, risk budget / stop distance). Each row assumes the capital "
             "given; split it if you take several.",
             f"{rejected} signal(s) rejected (method backtest edge not positive after charges); "
             f"{unaffordable} skipped for price/size limits."]
    if mode == "replay":
        cols += [("Actual", "actual", 0), ("ActualRs", "actual_pnl", 0)]
        if rows:
            notes.insert(0, "Replay result if every pick above was traded: total Rs "
                            f"{sum(r.get('actual_pnl', 0) for r in rows):,.0f}")
    if mtrend:
        notes.append(f"{against} setup(s) skipped because the market is not BULLISH ({mtrend['label']}). "
                     "Use --no-trend to disable.")
        if mtrend["trend"] != 1:
            notes.insert(0, f"Market is {mtrend['label']}: buy-first stock trades are skipped today. "
                            "Consider the options scanner (PE in a bearish market).")
    header("stocks", a, asof, mode, p, len(stocks), dropped,
           rules=f"Rules: {stock_orb.METHOD} (close > 09:15-09:45 high, volume >= {stock_orb.RVOL_MIN}x) | "
                 f"stop = opening-range low | target {p.rr}R | entries {p.entry_start}-{p.entry_end} | "
                 f"square-off {p.squareoff} | buy only, BULLISH market")
    if mtrend and not a.json:
        print(describe(mtrend))
    payload = dict(kind="stocks", method=stock_orb.METHOD, mode=mode, market=mtrend, asof=str(asof), capital=a.capital,
                   params=p.to_dict(), picks=rows, rejected=rejected, unaffordable=unaffordable, dropped=dropped,
                   method_backtest=dict(n=bt_n, avg_r=bt_avg, pf=bt_pf))
    finish("stocks", a, payload, rows, cols, notes)
    return payload


def analyze(a):
    if a.method == "orb":
        return analyze_orb(a)
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
    ap.add_argument("--allow-short", action="store_true", help="Also show intraday short-sell setups (ensemble method only)")
    ap.add_argument("--method", choices=["orb", "ensemble"], default="orb",
                    help="orb = ORB-30 + relative volume (default); ensemble = the original 5-strategy vote")
    analyze(ap.parse_args(argv))


if __name__ == "__main__":
    main()
