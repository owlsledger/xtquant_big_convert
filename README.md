# xtquant_big_convert

大 QMT 运行环境里的 Redis RPC 桥接包，用于把大 QMT 内置 Python 能力封装成可替换的交易/查询适配层，并兼容一组常用 MiniQMT 方法名。

## 能力

- 在大 QMT 策略进程中启动 Redis Pub/Sub RPC 服务。
- 查询资产、持仓、委托、成交、tick 和合约详情。
- 兼容 `query_stock_asset`、`query_stock_positions`、`query_stock_orders`、`query_stock_trades`、`get_full_tick`、`order_stock` 等 MiniQMT 常用方法名。
- 默认只读，`order_stock` / `cancel_order_stock_sysid` 等下单撤单接口默认关闭。
- 提供 dry-run 信号消费、Redis 状态写回和持仓同步骨架。

## 目录

- `src/bigqmt_signal_trader/`：核心包和适配器。
- `src/bigqmt_signal_trader_strategy.py`：大 QMT 策略基础入口。
- `src/bigqmt_signal_trader_redis_rpc_runtime.py`：只启用 Redis RPC 的大 QMT 入口。
- `src/bigqmt_signal_trader_redis_dryrun.py`：Redis 信号 dry-run 入口。
- `tests/bigqmt_signal_trader/`：无 QMT 环境也能运行的单元测试。
- `docs/`：运行说明和 RPC 协议。

## 本地测试

```powershell
python -B -m unittest discover -s tests\bigqmt_signal_trader
```

当前测试覆盖 41 个用例。

## QMT 本地配置

复制配置样例到 QMT 的 `python` 目录，并改成真实配置：

```text
src/bigqmt_signal_trader_local_config.example.py
```

目标文件名：

```text
bigqmt_signal_trader_local_config.py
```

真实配置文件不要提交。里面可能包含资金账号和 Redis 密码。

## 运行入口

在大 QMT 策略编辑器里建议使用 `docs/BIG_QMT_REDIS_RPC.md` 中的 reload 入口脚本。这样更新包文件后，重新运行策略即可刷新 `redis_rpc` 子模块，避免 QMT 进程缓存旧白名单。

## 安全默认值

`rpc_allow_order_methods` 默认为 `False`。此时远程调用 `order_stock` 会被拒绝，适合先上线查询和持仓同步链路。只有确认接入方、账号和风控后，再在本地私有配置里显式打开。
