"""Run any TradingBro command on Upstox market data instead of Yahoo.

    python -m tradingbro.up stocks  --capital 50000
    python -m tradingbro.up futures --capital 200000
    python -m tradingbro.up options --capital 20000
    python -m tradingbro.up review  [--date 2026-11-25]
    python -m tradingbro.up validate
    python -m tradingbro.up daily   scan|midday|final|results|picks|compare
    python -m tradingbro.up orders                     # Upstox order page for the Upstox-data picks

Everything is kept apart from the Yahoo pipeline: predictions and reviews go to
output_upstox/, results to Result_upstox.md / Picks_upstox.md, cache to .cache/upstox/.
It is the same as setting TRADINGBRO_SOURCE=upstox before running the normal module.
"""
import importlib
import os
import sys

COMMANDS = {"stocks", "futures", "options", "review", "validate", "daily", "compare"}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in COMMANDS | {"orders"}:
        sys.exit(__doc__)
    if "tradingbro.config" in sys.modules and sys.modules["tradingbro.config"].SOURCE != "upstox":
        sys.exit("tradingbro.config was already loaded with another data source - run this as a fresh process.")
    os.environ["TRADINGBRO_SOURCE"] = "upstox"     # must be set before tradingbro.config is imported
    cmd, rest = argv[0], argv[1:]
    if cmd == "orders":
        importlib.import_module("tradingbro.upstox").main(["orders", *rest])
    else:
        importlib.import_module(f"tradingbro.{cmd}").main(rest)


if __name__ == "__main__":
    main()
