"""Intraday option-buying scanner: buy CE in an up-trend, PE in a down-trend, exit same day.
Covers NIFTY, BANKNIFTY and NIFTY 50 stock options.

    python -m tradingbro.options --capital 20000
    python -m tradingbro.options --capital 20000 --otm 1     # one strike out-of-the-money (cheaper)
"""
import math

import numpy as np
import pandas as pd

from . import charges
from .common import base_parser, finish, header, params_from_args, resolve_asof, symbols_arg
from .data import fetch_universe, fetch_vix
from .market import describe, market_trend, trend_at
from .engine import signal_at, simulate
from .indicators import hist_vol
from .options_math import bs_delta, bs_price, next_expiry, pick_strike, years_to_expiry
from .strategies import add_signals
from .universe import estimate_strike_step, filter_symbols, load_instruments


def implied_vol(inst, daily, vix, day):
    """IV proxy known *before* `day`: India VIX for NIFTY, else 1.1 x 20-day historical vol."""
    if inst.symbol == "NIFTY" and vix is not None:
        v = vix["close"][vix.index.date < day]
        if len(v):
            return max(float(v.iloc[-1]) / 100, 0.08)
    if daily is not None:
        hv = hist_vol(daily["close"][daily.index.date < day]).dropna()
        if len(hv):
            return max(float(hv.iloc[-1]) * 1.1, 0.12)
    return 0.25


def option_trade_returns(trades, inst, daily, vix, otm, expiry_day=False, dte_days=None):
    """Re-price each historical underlying trade as a bought CE/PE using Black-Scholes.

    With `dte_days`, every past trade is priced on an option with that many days to
    expiry, so the backtest matches the contract being recommended today (a 36-day
    option behaves very differently from a 1-day one)."""
    out = []
    for t in trades:
        kind = "CE" if t.direction == 1 else "PE"
        step = inst.strike_step or estimate_strike_step(t.entry)
        K = pick_strike(t.entry, step, kind, otm)
        if dte_days is not None:
            exp = t.date + pd.Timedelta(days=dte_days)
        else:
            exp = next_expiry(t.date, inst.expiry, skip_today=not expiry_day)
        iv = implied_vol(inst, daily, vix, t.date)
        p_in = bs_price(t.entry, K, years_to_expiry(t.entry_time, exp), iv, kind)
        p_out = bs_price(t.exit, K, years_to_expiry(t.exit_time, exp), iv, kind)
        if p_in > 0.05:
            out.append(p_out / p_in - 1)
    return np.array(out)


def analyze(a):
    p = params_from_args(a)
    stocks, indices = load_instruments()
    universe = filter_symbols(indices + stocks, symbols_arg(a))
    intraday, daily_all, dropped = fetch_universe(universe, a.refresh)
    vix = fetch_vix(a.refresh)
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
        daily = daily_all.get(inst.yahoo)
        df = add_signals(df, p)
        sig = signal_at(df, asof, p, allow_short=True, with_outcome=(mode == "replay"), market_dir=mdir)
        if sig == "against_trend":
            against += 1
            continue
        if sig is None:
            continue
        kind = "CE" if sig.direction == 1 else "PE"
        step = inst.strike_step or estimate_strike_step(sig.price)
        K = pick_strike(sig.price, step, kind, a.otm)
        exp = next_expiry(asof.date(), inst.expiry, skip_today=not a.expiry_day)
        hist = simulate(df, p, allow_short=True, before_date=asof.date(), market=mkt)
        rets = option_trade_returns(hist, inst, daily, vix, a.otm, a.expiry_day,
                                    dte_days=(exp - asof.date()).days)
        iv = implied_vol(inst, daily, vix, asof.date())
        T = years_to_expiry(sig.ts, exp)
        T_exit = years_to_expiry(sig.ts + pd.Timedelta(hours=1), exp)
        prem = bs_price(sig.price, K, T, iv, kind)
        if prem < 0.5 or (a.max_premium and prem > a.max_premium):
            unaffordable += 1
            continue
        prem_stop = bs_price(sig.stop, K, T_exit, iv, kind)
        prem_tgt = bs_price(sig.target, K, T_exit, iv, kind)
        lot_cost = prem * inst.lot
        lots_cap = math.floor(a.capital / lot_cost)
        if lots_cap < 1:
            unaffordable += 1
            continue
        risk_lot = max(prem - prem_stop, 0.01) * inst.lot
        lots = min(lots_cap, max(1, math.floor(risk_budget / risk_lot)))
        qty = lots * inst.lot
        cost = charges.round_trip("options", prem * qty, prem * qty)
        n = len(rets)
        avg = float(rets.mean()) if n else 0.0
        expected = avg * prem * qty - cost
        if n < a.min_trades or avg <= 0 or expected <= 0:
            rejected += 1
            continue
        wins, losses = rets[rets > 0].sum(), -rets[rets < 0].sum()
        max_loss = risk_lot * lots + cost
        row = dict(
            symbol=inst.symbol, upstox=inst.upstox_oc, option=f"{inst.symbol} {exp:%d%b} {K:g} {kind}", type=kind, strike=K,
            expiry=str(exp), signal_time=f"{sig.ts:%H:%M}", spot=sig.price, iv_pct=iv * 100,
            delta=bs_delta(sig.price, K, T, iv, kind), premium=prem, prem_stop=prem_stop, prem_target=prem_tgt,
            spot_stop=sig.stop, spot_target=sig.target, lot=inst.lot, lots=lots, qty=qty, invest=prem * qty,
            max_loss=max_loss, risk_pct=max_loss / a.capital * 100,
            max_gain=(prem_tgt - prem) * qty - cost, exp_profit=expected, charges=cost, bt_trades=n,
            win_pct=float((rets > 0).mean() * 100), avg_opt_ret_pct=avg * 100,
            pf=float(wins / losses) if losses > 0 else float("inf"), votes=f"{abs(sig.votes)}/5",
            strategies="+".join(sig.agreeing),
        )
        if sig.outcome:
            o = sig.outcome
            exit_ts = pd.Timestamp(f"{asof.date()} {o['exit_time']}").tz_localize(asof.tz)
            p_out = bs_price(o["exit"], K, years_to_expiry(exit_ts, exp), iv, kind)
            row.update(actual=f"{o['reason']}@{o['exit_time']}", actual_pnl=(p_out - prem) * qty - cost)
        rows.append(row)

    rows.sort(key=lambda r: (-int(r["votes"].split("/")[0]), -r["max_gain"]))  # most strategies agreeing, then max gain
    rows = rows[: a.top]
    cols = [("Option", "option", 0), ("At", "signal_time", 0), ("Spot", "spot", 1), ("Prem~", "premium", 1),
            ("SL prem", "prem_stop", 1), ("Tgt prem", "prem_target", 1), ("Spot SL", "spot_stop", 1),
            ("Spot Tgt", "spot_target", 1), ("Lot", "lot", 0), ("Lots", "lots", 0), ("Invest", "invest", 0),
            ("MaxLoss", "max_loss", 0), ("MaxGain", "max_gain", 0), ("ExpRs", "exp_profit", 0), ("BT#", "bt_trades", 0),
            ("Win%", "win_pct", 0), ("AvgRet%", "avg_opt_ret_pct", 1), ("Votes", "votes", 0), ("Upstox", "upstox", 0)]
    if mode == "replay":
        cols += [("Actual", "actual", 0), ("ActualRs~", "actual_pnl", 0)]
    notes = [
        "Premiums are Black-Scholes ESTIMATES (IV = India VIX for NIFTY, 1.1 x 20d hist-vol otherwise). "
        "Check the live option chain: use the real premium, and manage the trade with the SPOT stop/target "
        "(exit the option when spot hits them).",
        "Backtest = underlying trades re-priced as options (no IV change, no bid-ask spread) - treat as indicative.",
        "Expiries: NSE Tuesday schedule shifted for holidays in config.NSE_HOLIDAYS; on expiry day the next expiry is used unless --expiry-day. Confirm the contract exists.",
        f"{rejected} signal(s) rejected for weak backtest edge; {unaffordable} skipped (1 lot over capital/premium limit).",
    ]
    if mtrend:
        notes.append(f"{against} signal(s) skipped for going against the market trend "
                     f"({mtrend['label']}; SIDEWAYS = no trades). Use --no-trend to disable.")
    header("options", a, asof, mode, p, len(universe), dropped)
    if mtrend and not a.json:
        print(describe(mtrend))
    payload = dict(kind="options", mode=mode, market=mtrend, asof=str(asof), capital=a.capital, params=p.to_dict(),
                   otm=a.otm, picks=rows, rejected=rejected, unaffordable=unaffordable, dropped=dropped)
    finish("options", a, payload, rows, cols, notes)
    return payload


def main(argv=None):
    ap = base_parser("Intraday CE/PE option-buying picks on NIFTY, BANKNIFTY and NIFTY 50 stocks")
    ap.add_argument("--otm", type=int, default=0, help="Strikes out-of-the-money (0 = ATM, 1 = one strike OTM, cheaper)")
    ap.add_argument("--expiry-day", action="store_true",
                    help="Allow contracts expiring today (default: roll to the next expiry on expiry day)")
    ap.add_argument("--max-premium", type=float, default=0, help="Skip options whose premium per unit exceeds this (0 = no limit)")
    analyze(ap.parse_args(argv))


if __name__ == "__main__":
    main()
