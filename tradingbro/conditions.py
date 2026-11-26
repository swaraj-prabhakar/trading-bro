"""Market conditions known by the 10:05 decision bar (research, branch market-conditions).

Goal: learn which days suit the strategy (Trade / Half size / Skip), not to forecast NIFTY's direction.

    python -m tradingbro.conditions --date 2026-11-26                  # features for one day
    python -m tradingbro.conditions dataset RUN_DIR [RUN_DIR ...] --out research/conditions/dataset.csv

`dataset` joins, for every day replayed in the given replay_days output folders (output_upstox/<date>/),
the features below with the day's outcome (labels). Only data available at 10:05 that day is used for
features: daily bars strictly before the day, and the day's 5-minute bars up to and including 10:05.

Features
- nifty_*: gap, gap vs yesterday's range, opening-range (09:15-09:45) width (absolute and vs its 20-day
  average), move 09:15->10:05, choppiness of that move, position of 10:05 in the day's range so far
- d_*: daily NIFTY context - 1/5/20-day returns, distance from the 20/50-day EMA, ADX(14), realised vol
  10/20 days, yesterday's range, NR7 (yesterday the narrowest range of 7)
- vix_*: India VIX level, 1- and 5-day change, VIX minus 20-day realised vol
- br_*: NIFTY 50 breadth at 10:05 - share up since the open / above yesterday's close / above VWAP,
  dispersion of returns across stocks
- cal_*: weekday, expiry Tuesday, sessions to the monthly expiry, results season
- mkt_*: the agent's own market trend (label and score) at the scan

Labels (per day)
- opt_R / opt_top2_R / opt_pnl / opt_n: options, all picks / first two (the personal picks)
- stk_R / stk_n: stocks
- follow: NIFTY's move 10:05 -> 15:15 in the direction of the agent's market trend (%), defined on every
  day, also days without picks - "did the morning trend continue?"
"""
import argparse
import json
import os
import statistics as st
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ROOT
from .data import fetch
from .options_math import next_expiry
from .universe import load_instruments

DECISION = "10:05"           # label of the last 5-minute bar the 10:10 scan sees
HIST = os.environ.get("TRADINGBRO_HISTORY_SESSIONS", "320")


def _adx(d, n=14):
    up, dn = d.high.diff(), -d.low.diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([d.high - d.low, (d.high - d.close.shift()).abs(), (d.low - d.close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    pdi = 100 * pd.Series(plus, index=d.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    mdi = 100 * pd.Series(minus, index=d.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


class Data:
    """Everything needed for the features, loaded once (Upstox cache)."""

    def __init__(self):
        stocks, _ = load_instruments()
        self.n5 = fetch(["^NSEI"], "5m", f"{HIST}d")["^NSEI"]
        self.nd = fetch(["^NSEI"], "1d", "2y")["^NSEI"]
        self.vix = fetch(["^INDIAVIX"], "1d", "2y")["^INDIAVIX"]
        self.s5 = fetch([s.yahoo for s in stocks], "5m", f"{HIST}d")
        self.adx = _adx(self.nd)
        t = self.n5.index.strftime("%H:%M")
        orr = self.n5[(t >= "09:15") & (t < "09:45")]
        g = orr.groupby(orr.index.date)
        self.or_width = (g.high.max() - g.low.min())            # NIFTY opening-range width per day (points)


def features(D: Data, day) -> dict:
    day = pd.Timestamp(day).date()
    b = D.n5[D.n5.index.date == day]
    t = b.index.strftime("%H:%M")
    upto = b[t <= DECISION]
    prev = D.nd[D.nd.index.date < day]
    pv = D.vix[D.vix.index.date < day]
    if len(upto) < 6 or len(prev) < 60:
        return {}
    pc, ph, pl = prev.close.iloc[-1], prev.high.iloc[-1], prev.low.iloc[-1]
    op, px = upto.open.iloc[0], upto.close.iloc[-1]
    orr = upto[upto.index.strftime("%H:%M") < "09:45"]
    width = orr.high.max() - orr.low.min()
    past_w = D.or_width[[d < day for d in D.or_width.index]].iloc[-20:]
    r5 = upto.close.pct_change().dropna()
    ret = np.log(prev.close).diff()
    rng = prev.high - prev.low
    f = dict(
        nifty_gap=(op / pc - 1) * 100,
        nifty_gap_vs_range=(op - pc) / max(ph - pl, 1e-9),
        nifty_or_width=width / pc * 100,
        nifty_or_rel=width / past_w.mean() if len(past_w) else np.nan,
        nifty_move=(px / op - 1) * 100,
        nifty_chop=r5.abs().sum() / max(abs(px / op - 1), 1e-6),
        nifty_pos=(px - upto.low.min()) / max(upto.high.max() - upto.low.min(), 1e-9),
        d_ret1=(pc / prev.close.iloc[-2] - 1) * 100,
        d_ret5=(pc / prev.close.iloc[-6] - 1) * 100,
        d_ret20=(pc / prev.close.iloc[-21] - 1) * 100,
        d_ema20=(pc / prev.close.ewm(span=20).mean().iloc[-1] - 1) * 100,
        d_ema50=(pc / prev.close.ewm(span=50).mean().iloc[-1] - 1) * 100,
        d_adx=float(D.adx[D.adx.index.date < day].iloc[-1]),
        d_rv10=ret.iloc[-10:].std() * np.sqrt(252) * 100,
        d_rv20=ret.iloc[-20:].std() * np.sqrt(252) * 100,
        d_range=(ph - pl) / pc * 100,
        d_nr7=float(rng.iloc[-1] <= rng.iloc[-7:].min()),
    )
    if len(pv) >= 6:
        f.update(vix=pv.close.iloc[-1], vix_chg1=(pv.close.iloc[-1] / pv.close.iloc[-2] - 1) * 100,
                 vix_chg5=(pv.close.iloc[-1] / pv.close.iloc[-6] - 1) * 100)
        f["vix_minus_rv"] = f["vix"] - f["d_rv20"]
    ups, above_pc, above_vwap, rets = [], [], [], []
    for df in D.s5.values():
        sb = df[df.index.date == day]
        sb = sb[sb.index.strftime("%H:%M") <= DECISION]
        sp = df[df.index.date < day]
        if len(sb) < 6 or not len(sp):
            continue
        c, o, spc = sb.close.iloc[-1], sb.open.iloc[0], sp.close.iloc[-1]
        tp = (sb.high + sb.low + sb.close) / 3
        vw = (tp * sb.volume).sum() / sb.volume.sum() if sb.volume.sum() > 0 else tp.mean()
        ups.append(c > o)
        above_pc.append(c > spc)
        above_vwap.append(c > vw)
        rets.append((c / spc - 1) * 100)
    if len(rets) >= 30:                                 # breadth only when most of the 50 stocks have data
        f.update(br_up_open=np.mean(ups), br_above_prev=np.mean(above_pc), br_above_vwap=np.mean(above_vwap),
                 br_dispersion=float(np.std(rets)))
    exp = next_expiry(day, "monthly")
    sessions = sorted({x for x in D.nd.index.date if day <= x <= exp}) or [day]
    f.update(cal_weekday=day.weekday(), cal_expiry_day=float(day == exp),
             cal_to_expiry=len(sessions) if exp <= D.nd.index.date[-1] else (exp - day).days * 5 / 7,
             cal_results=float(day.month in (1, 4, 7, 10) and day.day >= 10 or day.month in (2, 5, 8, 11) and day.day <= 15))
    return f


def follow(D: Data, day, direction):
    b = D.n5[D.n5.index.date == pd.Timestamp(day).date()]
    t = b.index.strftime("%H:%M")
    a, z = b[t <= DECISION], b[t <= "15:15"]
    if not len(a) or not len(z) or direction == 0:
        return np.nan
    return direction * (z.close.iloc[-1] / a.close.iloc[-1] - 1) * 100


def labels(run_dir):
    """{date: labels} from a replay_days output folder."""
    out = {}
    for rvf in sorted((Path(run_dir) / "output_upstox").glob("20??-??-??/review.json")):
        rv = json.loads(rvf.read_text())
        if rv.get("status") != "final":
            continue
        res = {(r["source"], r["label"]): r for r in rv["predictions"]}
        lab, mkt = {}, {}
        for f in sorted(rvf.parent.glob("*_*.json")):
            if f.name.startswith("review"):
                continue
            pl = json.loads(f.read_text())
            mkt = pl.get("market") or mkt
            rows = []
            for p in pl["picks"]:
                r = res.get((f.name, p.get("option") or f"{p['symbol']} {p.get('side', 'BUY')}"))
                if r is not None and r.get("pnl") is not None:
                    rows.append(r)
            k = "opt" if pl["kind"] == "options" else "stk"
            lab[f"{k}_n"] = len(rows)
            lab[f"{k}_R"] = st.mean(r["r"] for r in rows) if rows else np.nan
            lab[f"{k}_pnl"] = sum(r["pnl"] for r in rows)
            lab[f"{k}_top2_R"] = st.mean(r["r"] for r in rows[:2]) if rows else np.nan
        lab.update(mkt_label=mkt.get("label"), mkt_score=mkt.get("score"), mkt_trend=mkt.get("trend", 0))
        out[rvf.parent.name] = lab
    return out


def build_dataset(run_dirs, out):
    D = Data()
    rows = []
    for rd in run_dirs:
        for day, lab in labels(rd).items():
            f = features(D, day)
            if not f:
                print(f"{day}: not enough data, skipped", flush=True)
                continue
            rows.append(dict(date=day, **f, **lab, follow=follow(D, day, lab.get("mkt_trend") or 0)))
    df = pd.DataFrame(rows).drop_duplicates("date", keep="last").sort_values("date")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"{out}: {len(df)} days, {df.date.min()} -> {df.date.max()}")
    return df


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "dataset":
        ap = argparse.ArgumentParser()
        ap.add_argument("runs", nargs="+")
        ap.add_argument("--out", default=str(ROOT / "research" / "conditions" / "dataset.csv"))
        a = ap.parse_args(argv[1:])
        build_dataset(a.runs, a.out)
        return
    ap = argparse.ArgumentParser(description="Market-condition features known at 10:05")
    ap.add_argument("--date", required=True)
    a = ap.parse_args(argv)
    for k, v in features(Data(), a.date).items():
        print(f"{k:18s} {v:,.3f}")


if __name__ == "__main__":
    main()
