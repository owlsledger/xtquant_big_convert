# coding: utf-8
"""Live API smoke test + latency bench (read-only, safe for live account).

Covers every read method grouped by category. Reports per-call status and
latency, plus a category summary. Does NOT call any order/cancel method.
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, r"D:\guoseniquant\python")

from bigqmt_signal_trader.xtquant_compat import configure, xtdata, xt_trader  # noqa: E402


GROUPS = {
    "snapshot": [
        ("get_full_tick", {"codes": ["000001.SZ", "600000.SH"]}),
        ("get_instrument", {"code": "000001.SZ"}),
        ("get_stock_name", {"code": "000001.SZ"}),
        ("get_last_close", {"code": "000001.SZ"}),
    ],
    "kline": [
        ("get_market_data", {"field_list": ["close"], "stock_list": ["000001.SZ"],
                             "period": "1d", "count": 5}),
        ("get_market_data_ex", {"field_list": ["close"], "stock_list": ["000001.SZ"],
                                "period": "1d", "count": 5}),
    ],
    "calendar": [
        ("get_trading_dates", {"market": "SH", "start_time": "20260101",
                               "end_time": "20260131"}),
    ],
    "account": [
        ("get_asset", {}),
        ("get_positions", {}),
        ("query_stock_position", {"stock_code": "000001.SZ"}),
    ],
}


def main():
    configure()
    total = 0
    failed = 0
    for category, probes in GROUPS.items():
        print("=== %s ===" % category)
        cat_ok = 0
        cat_ms = 0.0
        for method, params in probes:
            t0 = time.time()
            try:
                if method in ("get_asset", "get_positions", "query_stock_position"):
                    result = getattr(xt_trader, method)(xt_trader.account) if method != "query_stock_position" else getattr(xt_trader, method)(xt_trader.account)
                else:
                    result = getattr(xtdata, method)(**params)
                ok = result is not None
                ms = (time.time() - t0) * 1000
                total += 1
                cat_ms += ms
                if ok:
                    cat_ok += 1
                else:
                    failed += 1
                print("  [%-4s] %-22s %.1fms" % ("OK" if ok else "FAIL", method, ms))
            except Exception as exc:  # noqa: BLE001
                total += 1
                failed += 1
                print("  [FAIL] %-22s %s" % (method, exc))
        print("  -> %d/%d ok, avg %.1fms" % (cat_ok, len(probes),
                                             cat_ms / max(len(probes), 1)))
    print("=== total %d, failed %d ===" % (total, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
