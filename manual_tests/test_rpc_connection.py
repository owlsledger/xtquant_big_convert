# coding: utf-8
"""通过 Redis RPC 测试大 QMT 连接。

运行（在 qmt/xtquant_big_convert 下，确保 PYTHONPATH 含 src）：
    python manual_tests/test_rpc_connection.py

需先在 QMT 中启动 BIGQMT_REDIS_DRYRUN.py 策略。
"""
import json
import os
import sys
import datetime
import time

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC))

from bigqmt_signal_trader.redis_rpc import call_redis_rpc
import redis as _redis

# ─── Redis 连接配置（与 QMT 端 bigqmt_signal_trader_local_config.py 一致）───
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 5
REDIS_PASSWORD = ""
ACCOUNT_ID = "8890831573"

redis_client = _redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD or None,
    decode_responses=False,
)


def rpc(method, params=None, timeout=30.0):
    """调用 RPC 并打印结果。"""
    t0 = time.time()
    try:
        response = call_redis_rpc(
            redis_client,
            account_id=ACCOUNT_ID,
            method=method,
            params=params or {},
            timeout_seconds=timeout,
        )
        elapsed = time.time() - t0
        ok = response.get("ok", False)
        if ok:
            data = response.get("data")
            print("  [OK] %s 成功 (%.3fs) data type=%s" % (method, elapsed, type(data).__name__))
            return data
        else:
            print("  [FAIL] %s 失败 (%.3fs): %s" % (method, elapsed, response.get("error", "unknown")))
            return None
    except Exception as e:
        elapsed = time.time() - t0
        print("  [FAIL] %s 异常 (%.3fs): %r" % (method, elapsed, e))
        return None


def main():
    print("=" * 60)
    print("BigQMT RPC 连接测试")
    print("  Redis: %s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DB))
    print("  Account: %s" % ACCOUNT_ID)
    now = datetime.datetime.now()
    print("  当前时间: %s" % now.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # 1. ping - 探活
    print("\n[1] ping - 检查 RPC 服务是否在线")
    result = rpc("ping")
    if result:
        print("     响应: %s" % json.dumps(result, ensure_ascii=False))

    # 2. get_instrument - 合约详情
    print("\n[2] get_instrument - 获取合约详情")
    result = rpc("get_instrument", {"code": "000001.SZ"})
    if result and isinstance(result, dict):
        print("     代码: %s" % result.get("code", "?"))
        print("     名称: %s" % result.get("InstrumentName", result.get("name", "?")))
        print("     状态: %s" % result.get("InstrumentStatus", "?"))

    # 3. get_instrument_type
    print("\n[3] get_instrument_type - 获取品种类型")
    result = rpc("get_instrument_type", {"code": "000001.SZ"})
    if result:
        print("     品种类型: %s" % json.dumps(result, ensure_ascii=False))

    # 4. get_stock_list_in_sector - 板块成分股
    print("\n[4] get_stock_list_in_sector - 沪深A股数量")
    result = rpc("get_stock_list_in_sector", {"sector_name": "沪深A股"})
    if result and isinstance(result, list):
        print("     沪深A股数量: %d" % len(result))
        print("     前5只: %s" % result[:5])

    # 5. get_market_data_ex - K线数据
    print("\n[5] get_market_data_ex - 获取日K线(平安银行,5天)")
    result = rpc("get_market_data_ex", {
        "field_list": ["open", "high", "low", "close", "volume", "amount"],
        "stock_list": ["000001.SZ"],
        "period": "1d",
        "count": 5,
        "dividend_type": "front",
        "fill_data": True,
    })
    if result:
        for code, df in result.items():
            if hasattr(df, "shape"):
                print("     %s: shape=%s" % (code, df.shape))
            elif isinstance(df, dict):
                print("     %s: keys=%s" % (code, list(df.keys())))
            else:
                print("     %s: type=%s" % (code, type(df).__name__))

    # 6. get_trading_dates - 交易日历
    print("\n[6] get_trading_dates - 获取近期交易日")
    result = rpc("get_trading_dates", {
        "market": "SH",
        "start_time": "20260701",
        "end_time": "20260713",
    })
    if result and isinstance(result, (list, tuple)):
        print("     交易日: %s" % result)

    # 7. get_ticks（get_full_tick）- 实时快照
    print("\n[7] get_ticks - 获取实时行情快照")
    result = rpc("get_ticks", {"codes": ["000001.SZ", "600519.SH"]})
    if result and isinstance(result, dict):
        for code, tick in result.items():
            print("     %s: lastPrice=%s open=%s high=%s low=%s volume=%s" % (
                code,
                tick.get("lastPrice", "?"),
                tick.get("open", "?"),
                tick.get("high", "?"),
                tick.get("low", "?"),
                tick.get("volume", "?"),
            ))

    # 8. get_divid_factors - 复权因子
    print("\n[8] get_divid_factors - 获取复权因子(600519.SH)")
    result = rpc("get_divid_factors", {"stock_code": "600519.SH"})
    if result:
        if isinstance(result, dict):
            n = len(result)
            print("     记录数: %d" % n)
            if n > 0:
                fk = next(iter(result))
                print("     首条key=%s value=%s" % (fk, list(result[fk].keys()) if isinstance(result[fk], dict) else type(result[fk]).__name__))
        else:
            print("     类型: %s, len=%s" % (type(result).__name__, len(result) if hasattr(result, "__len__") else "?"))

    # 9. get_stock_name - 股票名称
    print("\n[9] get_stock_name - 获取股票名称")
    result_600519 = rpc("get_stock_name", {"stock": "600519.SH"})
    result_000001 = rpc("get_stock_name", {"stock": "000001.SZ"})
    if result_600519:
        print("     600519.SH: %s" % result_600519)
    if result_000001:
        print("     000001.SZ: %s" % result_000001)

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
