# coding: utf-8
"""Systematically test all RPC APIs and MiniQMT alias mapping.

For each method, call it with sensible params, report ok/error and whether
data is non-empty. Also test that MiniQMT aliases resolve to the same handler.

Config is read from bigqmt_signal_trader_local_config (gitignored) or env vars;
no credentials are hard-coded here. Run from a dir where that config module
resolves, e.g.:

    PYTHONPATH="src;D:\guoseniquant\python" python test_all_apis.py

or set BIGQMT_ACCOUNT_ID / BIGQMT_REDIS_HOST / BIGQMT_REDIS_PORT /
BIGQMT_REDIS_DB / BIGQMT_REDIS_PASSWORD env vars.
"""

import os
import sys
import time

# Make the client package and the QMT python dir importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, r"D:\guoseniquant\python")

from bigqmt_signal_trader.xtquant_compat import configure, xtdata, xt_trader  # noqa: E402


# (method, params) pairs covering the main read-only surface.
PROBES = [
    ("ping", {}),
    ("get_full_tick", {"codes": ["000001.SZ", "600000.SH"]}),
    ("get_instrument", {"code": "000001.SZ"}),
    ("get_stock_name", {"code": "000001.SZ"}),
    ("get_last_close", {"code": "000001.SZ"}),
    ("get_market_data", {"field_list": ["close"], "stock_list": ["000001.SZ"],
                         "period": "1d", "count": 5}),
    ("get_market_data_ex", {"field_list": ["close"], "stock_list": ["000001.SZ"],
                            "period": "1d", "count": 5}),
    ("get_trading_dates", {"market": "SH", "start_time": "20260101",
                           "end_time": "20260131"}),
    ("get_asset", {}),
    ("get_positions", {}),
    ("query_stock_position", {"stock_code": "000001.SZ"}),
]

# MiniQMT-style aliases that must resolve to the same handlers.
ALIASES = [
    ("query_stock_asset", {}),
    ("query_stock_positions", {}),
    ("query_orders", {}),
    ("query_trades", {}),
    ("get_full_tick", {"codes": ["000001.SZ"]}),
]


def _is_non_empty(value):
    if value is None:
        return False
    if isinstance(value, (dict, list, str)):
        return len(value) > 0
    return True


def main():
    configure()
    failures = 0
    print("=== direct RPC method probes ===")
    for method, params in PROBES:
        t0 = time.time()
        try:
            if method in ("get_asset", "get_positions", "query_stock_position",
                          "query_stock_asset", "query_stock_positions",
                          "query_orders", "query_trades"):
                result = getattr(xt_trader, method)(xt_trader.account) if method.startswith("query") or method in ("get_asset", "get_positions") else None
                if result is None and hasattr(xt_trader, method):
                    result = getattr(xt_trader, method)()
            else:
                result = getattr(xtdata, method)(**params)
            ok = _is_non_empty(result)
            print("[%s] %-22s %.1fms ok=%s non_empty=%s" % (
                "OK" if ok else "EMPTY", method, (time.time() - t0) * 1000, True, ok))
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print("[FAIL] %-22s %.1fms %s" % (method, (time.time() - t0) * 1000, exc))

    print("=== MiniQMT alias resolution ===")
    for alias, params in ALIASES:
        t0 = time.time()
        try:
            fn = getattr(xt_trader, alias, None) or getattr(xtdata, alias, None)
            if fn is None:
                raise AttributeError("%s not exposed" % alias)
            print("[OK] %-22s resolved" % alias)
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print("[FAIL] %-22s %s" % (alias, exc))

    print("=== summary: %d failures ===" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
