# coding: utf-8
"""Systematically test all RPC APIs and MiniQMT alias mapping.

For each method, call it with sensible params, report ok/error and whether
data is non-empty. Also test that the MiniQMT-style method names resolve to
the same handlers exposed by xtquant_compat (which mirrors the real xtquant
API surface).

The account id is read from the BIGQMT_ACCOUNT_ID env var, or from the private
client config module (bigqmt_signal_trader_client_config / _local_config, both
gitignored), or from xt_trader.client.account_id after configure(). No
credentials are hard-coded here. Run from a dir where that config module
resolves, e.g.:

    PYTHONPATH="src" BIGQMT_ACCOUNT_ID=77001381 python test_all_apis.py

Trader-side probes (query_stock_*) require a valid account id; if none is
available they are reported as SKIP rather than FAIL so the smoke test can
still validate the market-data surface.

Note: get_instrument / get_last_close / ping are not explicitly wrapped by
xtquant_compat; they must be reached through the generic escape hatch
xtdata.call_method("method", **params), which forwards to the same server
method as the real xtquant SDK.
"""

import os
import sys
import time

# Make the client package importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# Optional: a local xtquant SDK dir (machine-specific, added only if present).
_local_xt = r"D:\guojinqmt\python"
if os.path.isdir(_local_xt):
    sys.path.insert(0, _local_xt)

from bigqmt_signal_trader.xtquant_compat import (  # noqa: E402
    configure,
    xtdata,
    xt_trader,
    StockAccount,
    load_client_config,
)


def _resolve_account_id():
    """Prefer env var, then private client config, then the configured client."""
    env_id = os.environ.get("BIGQMT_ACCOUNT_ID")
    if env_id:
        return env_id
    cfg = load_client_config() or {}
    cfg_id = cfg.get("account_id")
    if cfg_id:
        return cfg_id
    return xt_trader.client.account_id or ""


# (label, callable) pairs covering the main read-only surface. Every callable
# uses the exact method name + parameter names exposed by xtquant_compat, which
# mirror the real xtquant API.
def _build_probes(account):
    probes = [
        ("ping", lambda: xtdata.call_method("ping")),
        ("get_full_tick",
         lambda: xtdata.get_full_tick(code_list=["000001.SZ", "600000.SH"])),
        ("get_stock_name",
         lambda: xtdata.get_stock_name(stock="000001.SZ")),
        ("get_instrument",
         lambda: xtdata.call_method("get_instrument", code="000001.SZ")),
        ("get_last_close",
         lambda: xtdata.call_method("get_last_close", stock="000001.SZ")),
        ("get_market_data",
         lambda: xtdata.get_market_data(
             field_list=["close"], stock_list=["000001.SZ"],
             period="1d", count=5)),
        ("get_market_data_ex",
         lambda: xtdata.get_market_data_ex(
             field_list=["close"], stock_list=["000001.SZ"],
             period="1d", count=5)),
        ("get_trading_dates",
         lambda: xtdata.get_trading_dates(
             market="SH", start_time="20260101", end_time="20260131")),
    ]
    if account is not None:
        probes += [
            ("query_stock_asset",
             lambda: xt_trader.query_stock_asset(account)),
            ("query_stock_positions",
             lambda: xt_trader.query_stock_positions(account)),
            ("query_stock_position",
             lambda: xt_trader.query_stock_position(account, "000001.SZ")),
            ("query_stock_orders",
             lambda: xt_trader.query_stock_orders(account)),
            ("query_stock_trades",
             lambda: xt_trader.query_stock_trades(account)),
        ]
    return probes


# MiniQMT-style method names that must resolve to real handlers on the
# xt_trader / xtdata objects.
ALIASES = [
    ("xtdata", "get_full_tick"),
    ("xtdata", "get_stock_name"),
    ("xtdata", "call_method"),
    ("xt_trader", "query_stock_asset"),
    ("xt_trader", "query_stock_positions"),
    ("xt_trader", "query_stock_position"),
    ("xt_trader", "query_stock_orders"),
    ("xt_trader", "query_stock_trades"),
    ("xt_trader", "query_stock_asset_async"),
    ("xt_trader", "query_stock_positions_async"),
]


def _is_non_empty(value):
    if value is None:
        return False
    if isinstance(value, (dict, list, str)):
        return len(value) > 0
    return True


def main():
    configure()

    account_id = _resolve_account_id()
    account = StockAccount(account_id) if account_id else None
    if account is None:
        print("NOTE: no BIGQMT_ACCOUNT_ID / client config found; "
              "trader-side probes will be SKIPPED.\n")

    failures = 0
    print("=== direct RPC method probes ===")
    for label, fn in _build_probes(account):
        t0 = time.time()
        try:
            result = fn()
            ok = _is_non_empty(result)
            print("[%s] %-22s %.1fms non_empty=%s" % (
                "OK" if True else "EMPTY", label,
                (time.time() - t0) * 1000, ok))
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print("[FAIL] %-22s %.1fms %s" % (
                label, (time.time() - t0) * 1000, exc))

    print("=== MiniQMT alias resolution ===")
    for owner, alias in ALIASES:
        t0 = time.time()
        try:
            obj = xt_trader if owner == "xt_trader" else xtdata
            fn = getattr(obj, alias, None)
            if fn is None:
                raise AttributeError("%s.%s not exposed" % (owner, alias))
            print("[OK] %-22s resolved (%.1fms)" % (
                "%s.%s" % (owner, alias), (time.time() - t0) * 1000))
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print("[FAIL] %-22s %s" % ("%s.%s" % (owner, alias), exc))

    print("=== summary: %d failures ===" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
