# BigQMT 数据请求方式 — ztrade 项目使用记录

本文档仅记录 ztrade 项目中向 BigQMT 请求数据的实际方式。

---

## 1. 导入方式

ztrade 项目使用两种导入路径，最终都收敛到 `bigqmt_signal_trader.xtquant_compat.xtdata`（通过 RPC 代理）：

### 路径 A：shim 劫持（主要方式）

```python
from xtquant import xtdata
```

shim 包 `xtquant/xtdata.py` 将所有属性访问委托给兼容层：
```python
# src/xtquant/xtdata.py → __getattr__ 注入 _compat.xtdata
def get_divid_factors(ts_code):
    return _compat.xtdata.get_divid_factors(ts_code)
```

### 路径 B：直接导入兼容层

```python
from bigqmt_signal_trader.xtquant_compat import xtdata
```

---

## 2. 使用模块清单

### 2.1 daily_kline — 日线 K 线

**文件**：`src/ztrade/data/daily_kline.py`

```python
from xtquant import xtdata

# 第 1 步：批量下载历史数据（自动增量）
xtdata.download_history_data2(stock_list=batch, period="1d")

# 第 2 步：读取本地缓存
raw = xtdata.get_local_data(stock_list=batch, period="1d", count=-1)
```

**参数**：
- `stock_list`：分批传入，默认 50 只/批（`ZTRADE_BQ_BATCH_SIZE`）
- `period`：固定 `"1d"`
- `count=-1`：获取全部本地可用数据

**返回**：`{ts_code: DataFrame(stime, open, high, low, close, volume, amount)}`

### 2.2 minute_kline — 30 分钟 K 线

**文件**：`src/ztrade/data/minute_kline.py`

```python
from xtquant import xtdata

xtdata.download_history_data2(stock_list=batch, period="30m")
raw = xtdata.get_local_data(stock_list=batch, period="30m", count=30)  # ≈4天
```

**条件**：日常增量更新时走 BigQMT，历史回填走 Baostock（由 `minute_kline.update_all()` 中 `p in BIGQMT_PERIODS and not historical_start_dt` 条件控制）

### 2.3 adjust_factor_bigqmt — 复权因子

**文件**：`src/ztrade/data/adjust_factor_bigqmt.py`

```python
from xtquant import xtdata

factors = xtdata.get_divid_factors(ts_code)
```

**返回**：`{毫秒时间戳: [div_cash, allot_ratio, bonus_ratio, conversion_ratio, allot_price, flag, qfq_factor]}`

### 2.4 bigqmt_extra — 港股通明细

**文件**：`src/ztrade/data/bigqmt_extra.py`

```python
from bigqmt_signal_trader.xtquant_compat import xtdata

result = xtdata.get_hkt_details(stock_code=code)
```

**路径 B 原因**：该模块要求显式声明依赖，不依赖 shim 包的 `__getattr__` 动态委托。

### 2.5 已弃用接口（仅保留兼容旧调用，实际已改用 Tushare/AkShare）

```python
# bigqmt_extra.py 中标记为 # deprecated
xtdata.get_longhubang(...)           # → 改用 akshare stock_lhb_detail_em
xtdata.get_north_finance_change(...)  # → 改用 Tushare moneyflow_hsgt
xtdata.get_hkt_statistics(...)        # → 改用 Tushare hk_hold
```

---

## 3. 环境变量

ztrade 项目中 BigQMT 相关环境变量：

| 变量 | 默认值 | 设置位置 | 用途 |
|------|--------|----------|------|
| `QMT_BIGQMT=1` | — | `.env` | 启用 BigQMT 模式，跳过 MiniQMT 检查 |
| `QMT_ACCOUNT_ID` | `""` | `.env` | 资金账号 `77001381` |
| `BIGQMT_RPC_TIMEOUT_SECONDS` | `3600` | 各模块内 `setdefault` | RPC 超时，大盘日线设为 1h |
| `BIGQMT_ACCOUNT_ID` | `QMT_ACCOUNT_ID` | `_ensure_bigqmt_env()` | RPC 账号 fallback |
| `PYTHONPATH` | — | 系统变量 / `setx` | 指向 `.../xtquant_big_convert/src` |

**PYTHONPATH 注入方式**（自动兜底）：

```python
# daily_kline.py / minute_kline.py
_BQ_SRC = os.environ.get("BIGQMT_SRC_DIR")
if not _BQ_SRC:
    _BQ_SRC = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..",
        "qmt", "xtquant_big_convert", "src",
    ))
if os.path.isdir(_BQ_SRC) and _BQ_SRC not in sys.path:
    sys.path.insert(0, _BQ_SRC)
```

---

## 4. alidate 测试脚本

**文件**：`qmt/xtquant_big_convert/manual_tests/test_rpc_connection.py`

```python
from bigqmt_signal_trader.redis_rpc import call_redis_rpc

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=5)
response = call_redis_rpc(
    redis_client, account_id="77001381",
    method="ping", timeout_seconds=30,
)
```

不经过 shim，直接用 `call_redis_rpc` 做低层探活。
