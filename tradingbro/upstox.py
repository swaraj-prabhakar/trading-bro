"""Upstox integration: daily login, exact contract lookup, lot-size sync and a local
"Review & place" page that opens Upstox's pre-filled order confirmation (UpLink).

    python -m tradingbro.upstox setup        # creates upstox_credentials.json to fill in
    python -m tradingbro.upstox login        # once per day (token expires 03:30 next day)
    python -m tradingbro.upstox sync-lots    # update lot sizes in data/instruments.json
    python -m tradingbro.upstox orders       # latest saved picks -> Review & place page

No order is ever placed by this tool: every button opens Upstox's own confirmation
screen, where you check, edit or delete the order and press "Place order" yourself.
"""
import argparse
import gzip
import html
import json
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from .config import CACHE_DIR, DATA_DIR, OUTPUT_DIR, ROOT
from .data import now_ist

CRED_FILE = ROOT / "upstox_credentials.json"
TOKEN_FILE = ROOT / ".upstox_token.json"
INSTR_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
DIALOG_URL = "https://api.upstox.com/v2/login/authorization/dialog"
TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"
UPLINK_URL = "https://api.upstox.com/v2/uplink/order/place"
HOST, PORT = "127.0.0.1", 8765
USER_AGENT = "TradingBro/1.0 (personal Upstox API app)"
IST = timezone(timedelta(hours=5, minutes=30))


# ---------------------------------------------------------------- credentials / token
def load_creds():
    if not CRED_FILE.exists():
        sys.exit(f"Missing {CRED_FILE.name}. Run: python -m tradingbro.upstox setup")
    c = json.loads(CRED_FILE.read_text())
    if not c.get("api_key") or not c.get("api_secret") or "PASTE" in c["api_key"] + c["api_secret"]:
        sys.exit(f"Fill api_key and api_secret in {CRED_FILE}")
    return c


def load_token():
    if not TOKEN_FILE.exists():
        return None
    t = json.loads(TOKEN_FILE.read_text())
    if datetime.fromisoformat(t["expires"]) <= datetime.now(IST):
        return None
    return t["access_token"]


def setup(_):
    if CRED_FILE.exists():
        print(f"{CRED_FILE} already exists - edit it if needed.")
        return
    CRED_FILE.write_text(json.dumps({"api_key": "PASTE_API_KEY", "api_secret": "PASTE_API_SECRET",
                                     "redirect_uri": f"http://{HOST}:{PORT}/callback"}, indent=2))
    print(f"Created {CRED_FILE}\nOpen it, paste your API key and secret, save, then run: python -m tradingbro.upstox login")


class _Server(HTTPServer):
    allow_reuse_address = True


def login(_):
    c = load_creds()
    state = secrets.token_urlsafe(16)
    got = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if self.path.startswith("/callback") and "code" in q:
                got["ok"] = q.get("state", [""])[0] == state
                got["code"] = q["code"][0]
                msg = "Login received - you can close this tab." if got["ok"] else "State mismatch - login rejected."
            else:
                msg = "Waiting for Upstox login..."
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<h3>TradingBro</h3><p>{msg}</p>".encode())

    srv = _Server((HOST, PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = DIALOG_URL + "?" + urllib.parse.urlencode(dict(response_type="code", client_id=c["api_key"],
                                                         redirect_uri=c["redirect_uri"], state=state))
    print("Opening Upstox login in your browser. If it does not open, visit:\n" + url)
    webbrowser.open(url)
    t0 = time.time()
    while "code" not in got and time.time() - t0 < 300:
        time.sleep(0.5)
    srv.shutdown()
    if "code" not in got:
        sys.exit("No login within 5 minutes.")
    if not got["ok"]:
        sys.exit("State mismatch - possible forged callback. Try again.")

    body = urllib.parse.urlencode(dict(code=got["code"], client_id=c["api_key"], client_secret=c["api_secret"],
                                       redirect_uri=c["redirect_uri"], grant_type="authorization_code")).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST", headers={
        "accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT})   # Upstox's Cloudflare rejects Python's default client name
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Token request failed: {e.code} {e.read().decode(errors='replace')[:300]}")
    now = datetime.now(IST)
    exp = (now + timedelta(days=1)).replace(hour=3, minute=30, second=0, microsecond=0)
    if now.hour < 3 or (now.hour == 3 and now.minute < 30):
        exp -= timedelta(days=1)
    TOKEN_FILE.write_text(json.dumps(dict(access_token=resp["access_token"], user_id=resp.get("user_id"),
                                          created=now.isoformat(), expires=exp.isoformat())))
    print(f"Logged in as {resp.get('user_id')} - token valid until {exp:%d %b %H:%M} IST.")


# ---------------------------------------------------------------- instruments
def instruments(refresh=False):
    d = CACHE_DIR / "upstox"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"NSE_{now_ist():%Y%m%d}.json.gz"
    if refresh or not p.exists():
        with urllib.request.urlopen(urllib.request.Request(INSTR_URL, headers={"User-Agent": USER_AGENT}),
                                    timeout=120) as r:
            p.write_bytes(r.read())
        for old in d.glob("NSE_*.json.gz"):
            if old != p:
                old.unlink()
    return json.load(gzip.open(p))


def _ist_date(ms):
    return datetime.fromtimestamp(ms / 1000, IST).date().isoformat()


class Contracts:
    def __init__(self, recs):
        self.eq = {r["isin"]: r for r in recs if r.get("segment") == "NSE_EQ" and r.get("isin")}
        self.fo = {}
        for r in recs:
            if r.get("segment") == "NSE_FO":
                self.fo.setdefault(r["underlying_symbol"], []).append(r)

    def future(self, sym, expiry):
        f = [r for r in self.fo.get(sym, []) if r["instrument_type"] == "FUT"]
        exact = [r for r in f if _ist_date(r["expiry"]) == expiry]
        return exact[0] if exact else None

    def option(self, sym, expiry, kind, strike):
        opts = [r for r in self.fo.get(sym, []) if r["instrument_type"] == kind and _ist_date(r["expiry"]) == expiry]
        if not opts:
            return None, False
        best = min(opts, key=lambda r: abs(r["strike_price"] - strike))
        return best, best["strike_price"] == strike

    def lot(self, sym):
        f = sorted((r for r in self.fo.get(sym, []) if r["instrument_type"] == "FUT"), key=lambda r: r["expiry"])
        return f[0]["lot_size"] if f else None


def sync_lots(a):
    c = Contracts(instruments(a.refresh))
    p = DATA_DIR / "instruments.json"
    d = json.loads(p.read_text())
    changed = []
    for grp in ("indices", "stocks"):
        for it in d[grp]:
            lot = c.lot(it["symbol"])
            if lot and lot != it["lot"]:
                changed.append(f"{it['symbol']}: {it['lot']} -> {lot}")
                it["lot"] = int(lot)
    p.write_text(json.dumps(d, indent=1))
    print("\n".join(changed) if changed else "All lot sizes already match Upstox.")
    print(f"{len(changed)} lot size(s) updated in {p}")


# ---------------------------------------------------------------- orders page
def _tick(price, tick_paise):
    t = (tick_paise or 5) / 100
    return round(round(price / t) * t, 2)


def build_orders(files):
    c = Contracts(instruments())
    from .universe import load_instruments
    s, i = load_instruments()
    isin = {x.symbol: x for x in s + i}
    raw = {x["symbol"]: x for g in ("stocks", "indices")
           for x in json.loads((DATA_DIR / "instruments.json").read_text())[g]}
    cards = []
    for f in files:
        pl = json.loads(f.read_text())
        kind = pl["kind"]
        for r in pl["picks"]:
            sym = r["symbol"]
            warn = []
            if kind == "stocks":
                rec = c.eq.get(raw.get(sym, {}).get("isin", ""))
                qty = int(r["units"])
                side = r["side"]
                order_type, price = "LIMIT", _tick(r["price"], rec and rec.get("tick_size"))
                levels = f"Stop {r['stop']:,.2f} · Target {r['target']:,.2f}"
                title = f"{sym} {side}"
            elif kind == "futures":
                rec = c.future(sym, r["expiry"])
                side = r["side"]
                if rec and rec["lot_size"] != r["lot"]:
                    warn.append(f"Lot size is {rec['lot_size']} on Upstox (scan used {r['lot']}) - margin/P&L scale accordingly.")
                qty = int(r["lots"] * (rec["lot_size"] if rec else r["lot"]))
                order_type, price = "MARKET", 0
                basis = r["fut_price"] - r["spot"]
                levels = (f"Spot stop {r['stop'] - basis:,.2f} · Spot target {r['target'] - basis:,.2f} "
                          f"(futures ≈ {r['stop']:,.1f} / {r['target']:,.1f})")
                title = f"{sym} FUT {r['expiry']} {side}"
            else:
                rec, exact = c.option(sym, r["expiry"], r["type"], r["strike"])
                side = "BUY"
                if rec and not exact:
                    warn.append(f"Strike {r['strike']:g} not listed; nearest is {rec['strike_price']:g}.")
                if rec and rec["lot_size"] != r["lot"]:
                    warn.append(f"Lot size is {rec['lot_size']} on Upstox (scan used {r['lot']}).")
                qty = int(r["lots"] * (rec["lot_size"] if rec else r["lot"]))
                order_type, price = "MARKET", 0
                levels = (f"Exit when SPOT hits stop {r['spot_stop']:,.2f} or target {r['spot_target']:,.2f} "
                          f"(est. premium {r['premium']:.1f} → SL {r['prem_stop']:.1f} / TGT {r['prem_target']:.1f})")
                title = r["option"]
            if rec is None:
                cards.append(dict(title=title, kind=kind, error="Contract not found in today's Upstox instruments file."))
                continue
            order = dict(quantity=qty, product="I", validity="DAY", price=price, instrument_token=rec["instrument_key"],
                         order_type=order_type, transaction_type=side, disclosed_quantity=0, is_amo=False,
                         tag="TradingBro")
            cards.append(dict(title=title, kind=kind, symbol=rec["trading_symbol"], order=order, levels=levels,
                              warn=warn, votes=r.get("votes", ""), max_loss=r.get("max_loss"),
                              max_gain=r.get("max_gain"), at=r.get("signal_time"), src=f.name))
    return cards


PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TradingBro orders</title><style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b1f24;--mut:#5b6470;--line:#dde1e6;--buy:#1a7f37;--sell:#b42318;--warn:#9a6700}
@media (prefers-color-scheme:dark){:root{--bg:#111418;--card:#1a1e24;--ink:#e6e9ed;--mut:#9aa4b0;--line:#2c323a;--buy:#3fb950;--sell:#f85149;--warn:#d29922}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:860px;margin:0 auto;padding:20px 16px}h1{font-size:20px;margin:0 0 4px}.mut{color:var(--mut);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:baseline}
.t{font-weight:600;font-size:16px}.k{font-size:12px;text-transform:uppercase;color:var(--mut);margin-left:6px}
.row{display:flex;gap:18px;flex-wrap:wrap;margin:8px 0;font-size:14px}.row b{font-variant-numeric:tabular-nums}
.warn{color:var(--warn);font-size:13px;margin:4px 0}.err{color:var(--sell)}
button{border:0;border-radius:8px;padding:9px 14px;font-weight:600;color:#fff;cursor:pointer;font-size:14px}
.BUY{background:var(--buy)}.SELL{background:var(--sell)}.banner{padding:10px 12px;border-radius:8px;border:1px solid var(--warn);color:var(--warn)}
</style></head><body><main><h1>TradingBro → Upstox</h1>
<p class="mut">%HEAD%</p>%BANNER%%CARDS%
<p class="mut">Each button opens Upstox's own confirmation screen with the order pre-filled. Check it, edit if needed (e.g. change MARKET to LIMIT at the live premium), then press <b>Place order</b> there. Nothing is placed from this page. After the buy fills, place your stop-loss in Upstox at the level shown. Square off by 15:15. Educational tool, not investment advice.</p>
</main></body></html>"""


def render(cards, token, redirect, head):
    out = []
    for n, c in enumerate(cards):
        if "error" in c:
            out.append(f'<div class="card"><div class="t">{html.escape(c["title"])}<span class="k">{c["kind"]}</span></div>'
                       f'<p class="err">{html.escape(c["error"])}</p></div>')
            continue
        o = c["order"]
        price = "MARKET" if o["order_type"] == "MARKET" else f"LIMIT ₹{o['price']:,.2f}"
        warns = "".join(f'<p class="warn">⚠ {html.escape(w)}</p>' for w in c["warn"])
        ml = f"₹{c['max_loss']:,.0f}" if c.get("max_loss") is not None else "-"
        mg = f"₹{c['max_gain']:,.0f}" if c.get("max_gain") is not None else "-"
        form = ""
        if token:
            form = (f'<form method="post" action="{UPLINK_URL}" target="_blank">'
                    f'<input type="hidden" name="access_token" value="{html.escape(token)}">'
                    f'<input type="hidden" name="redirect_url" value="{html.escape(redirect)}">'
                    f'<input type="hidden" name="data" value="{html.escape(json.dumps([o]))}">'
                    f'<button class="{o["transaction_type"]}">Review &amp; {o["transaction_type"].lower()} on Upstox</button></form>')
        out.append(f'<div class="card"><div class="top"><div><span class="t">{html.escape(c["title"])}</span>'
                   f'<span class="k">{c["kind"]} · {html.escape(str(c["votes"]))} · signal {c["at"]}</span></div>{form}</div>'
                   f'<div class="row"><span>Contract <b>{html.escape(c["symbol"])}</b></span><span>Qty <b>{o["quantity"]}</b></span>'
                   f'<span><b>{price}</b> · Intraday</span><span>Max loss <b>{ml}</b></span><span>Max gain <b>{mg}</b></span></div>'
                   f'<div class="mut">{html.escape(c["levels"])}</div>{warns}</div>')
    banner = "" if token else ('<p class="banner">Not logged in to Upstox (or token expired). Run '
                               '<code>python -m tradingbro.upstox login</code> and reload this page.</p>')
    return PAGE.replace("%HEAD%", html.escape(head)).replace("%BANNER%", banner).replace("%CARDS%", "".join(out))


def latest_files(day):
    folder = OUTPUT_DIR / day
    best = {}
    for f in sorted(folder.glob("*_*.json")):
        k = f.stem.split("_")[0]
        if k in ("stocks", "futures", "options"):
            best[k] = f                       # sorted -> last one is the latest HHMM
    return [best[k] for k in ("stocks", "futures", "options") if k in best]


def orders(a):
    day = a.date or f"{now_ist():%Y-%m-%d}"
    files = [OUTPUT_DIR / day / n for n in a.files] if a.files else latest_files(day)
    if not files:
        sys.exit(f"No saved picks in output/{day}. Run a scanner during market hours first.")
    cards = build_orders(files)
    c = json.loads(CRED_FILE.read_text()) if CRED_FILE.exists() else {}
    redirect = c.get("redirect_uri", f"http://{HOST}:{PORT}/callback")
    head = f"{day} · picks from {', '.join(f.name for f in files)} · generated {now_ist():%H:%M} IST"

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path.startswith("/callback"):
                body = "<h3>TradingBro</h3><p>Back from Upstox - you can close this tab.</p>"
            else:
                body = render(cards, load_token(), redirect, head)   # token read at request time, never written to disk
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode())

    srv = _Server((HOST, PORT), H)
    url = f"http://{HOST}:{PORT}/"
    print(f"{len(cards)} order card(s) from {', '.join(f.name for f in files)}")
    for c_ in cards:
        print("  -", c_["title"], "->", c_.get("symbol", c_.get("error")), *c_.get("warn", []))
    if not load_token():
        print("Not logged in - buttons are hidden. Run: python -m tradingbro.upstox login")
    print(f"Order page: {url}  (Ctrl+C to stop)")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="Upstox login, lot sync and order review page")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(fn=setup)
    sub.add_parser("login").set_defaults(fn=login)
    s = sub.add_parser("sync-lots")
    s.add_argument("--refresh", action="store_true")
    s.set_defaults(fn=sync_lots)
    o = sub.add_parser("orders")
    o.add_argument("--date", help="YYYY-MM-DD (default today)")
    o.add_argument("--files", nargs="*", help="Specific files in output/<date>/, e.g. options_1145.json")
    o.add_argument("--no-browser", action="store_true")
    o.set_defaults(fn=orders)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
