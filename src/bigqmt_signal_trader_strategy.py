# coding: utf-8
"""ThinkTrader Big QMT strategy entry.

Keep this entry file ASCII-only because QMT's strategy editor may save the
generated strategy file with a local code page while preserving this coding
header. Business logic stays in the importable package.
"""

import datetime

from bigqmt_signal_trader.adapter_factory import build_app as _default_build_app
from bigqmt_signal_trader.runner import (
    forward_order_event,
    forward_trade_event,
    init_app,
    reset_app as _reset_runner_app,
    sync_positions_app,
    tick_app,
)
from bigqmt_signal_trader.runtime_bigqmt import BigQmtRuntimeAdapter


_app_factory = None
_account_id = ""
_config = {}
_qmt_api = {}
_adjust_logged = False
_rpc_service = None
_scheduled_adjust = False


def set_app_factory(factory):
    global _app_factory
    _app_factory = factory


def set_account_id(account_id):
    global _account_id
    _account_id = str(account_id or "")


def configure(**kwargs):
    _config.update(kwargs)


def bind_qmt_api(passorder_func=None, cancel_func=None, get_trade_detail_data_func=None):
    if passorder_func is not None:
        _qmt_api["passorder"] = passorder_func
    if cancel_func is not None:
        _qmt_api["cancel"] = cancel_func
    if get_trade_detail_data_func is not None:
        _qmt_api["get_trade_detail_data"] = get_trade_detail_data_func


def reset_app():
    global _adjust_logged, _rpc_service, _scheduled_adjust
    _adjust_logged = False
    _scheduled_adjust = False
    if _rpc_service is not None:
        try:
            _rpc_service.stop()
        except Exception:
            pass
    _rpc_service = None
    _reset_runner_app()


def _resolve_runtime_name(name):
    if name in _qmt_api:
        return _qmt_api[name]
    if name in globals():
        return globals()[name]
    try:
        import builtins
        return getattr(builtins, name)
    except Exception:
        return None


def _build_config():
    config = dict(_config)
    if _account_id:
        config["account_id"] = _account_id
    qmt_api = dict(config.get("qmt_api") or {})
    qmt_api.setdefault("passorder", _resolve_runtime_name("passorder"))
    qmt_api.setdefault("cancel", _resolve_runtime_name("cancel"))
    qmt_api.setdefault("get_trade_detail_data", _resolve_runtime_name("get_trade_detail_data"))
    config["qmt_api"] = qmt_api
    return config


def _build_app(context_info):
    if _app_factory is not None:
        return _app_factory(context_info)
    return _default_build_app(context_info, _build_config())


def _config_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")


def _build_rpc_service(context_info, app, config):
    rpc_config = dict(config.get("rpc") or {})
    enabled = _config_bool(config.get("enable_rpc"), False) or _config_bool(rpc_config.get("enabled"), False)
    if not enabled:
        return None

    from bigqmt_signal_trader.adapters.market_bigqmt import BigQmtMarketDataProvider
    from bigqmt_signal_trader.adapters.position_bigqmt import BigQmtPositionProvider
    from bigqmt_signal_trader.adapters.redis_common import build_redis_client
    from bigqmt_signal_trader.redis_rpc import BigQmtRpcHandlers, RedisPubSubRpcService

    qmt_api = dict(config.get("qmt_api") or {})
    redis_config = dict(config.get("redis") or {})
    redis_config.update(dict(rpc_config.get("redis") or {}))
    redis_client = rpc_config.get("redis_client") or config.get("redis_client") or build_redis_client(redis_config)
    account_id = str(rpc_config.get("account_id") or config.get("account_id") or _account_id or "")
    if not account_id:
        print("[bigqmt_rpc] disabled: account_id is empty")
        return None
    allow_order_methods = _config_bool(rpc_config.get("allow_order_methods"), False)
    handlers = BigQmtRpcHandlers(
        account_id=account_id,
        market_data=BigQmtMarketDataProvider(context_info),
        position_provider=BigQmtPositionProvider(
            get_trade_detail_data_func=qmt_api.get("get_trade_detail_data"),
            account_type=config.get("account_type", "STOCK"),
        ),
        order_gateway=getattr(app, "order_gateway", None),
        position_sync_sink=getattr(app, "position_sync_sink", None),
        allow_order_methods=allow_order_methods,
        allowed_methods=rpc_config.get("allowed_methods"),
    )
    return RedisPubSubRpcService(
        redis_client=redis_client,
        handlers=handlers,
        account_id=account_id,
        request_channel_template=rpc_config.get("request_channel_template", "bigqmt:rpc:req:{account_id}"),
        response_channel_template=rpc_config.get("response_channel_template", "bigqmt:rpc:resp:{account_id}:{request_id}"),
        response_key_template=rpc_config.get("response_key_template", "bigqmt:rpc:resp:{account_id}:{request_id}"),
        response_ttl_seconds=int(rpc_config.get("response_ttl_seconds", 60)),
        max_queue_size=int(rpc_config.get("max_queue_size", 200)),
    )


def _start_rpc_service(context_info, app, config):
    global _rpc_service
    if _rpc_service is not None:
        return _rpc_service
    _rpc_service = _build_rpc_service(context_info, app, config)
    if _rpc_service is not None:
        _rpc_service.start()
    return _rpc_service


def _drain_rpc_service(config):
    if _rpc_service is None:
        return 0
    rpc_config = dict(config.get("rpc") or {})
    max_items = int(rpc_config.get("drain_max_items", 20))
    return _rpc_service.drain_pending(max_items=max_items)


def _schedule_adjust_if_needed(context_info, config):
    global _scheduled_adjust
    if _scheduled_adjust:
        return
    if not _config_bool(config.get("schedule_adjust"), False):
        return
    if not hasattr(context_info, "run_time"):
        return
    interval = str(config.get("schedule_adjust_interval") or "3000nMilliSecond")
    start_time = (datetime.datetime.now() + datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        context_info.run_time("adjust", interval, start_time)
        _scheduled_adjust = True
        print("[bigqmt_signal_trader] scheduled adjust interval=%s" % interval)
    except Exception as exc:
        print("[bigqmt_signal_trader] schedule adjust failed: %s" % exc)


def init(ContextInfo):
    if _account_id and hasattr(ContextInfo, "set_account"):
        ContextInfo.set_account(_account_id)
    config = _build_config()
    runtime = BigQmtRuntimeAdapter(ContextInfo)
    app = init_app(runtime, _build_app)
    _start_rpc_service(ContextInfo, app, config)
    _schedule_adjust_if_needed(ContextInfo, config)
    print("[bigqmt_signal_trader] init ok")
    return app


def adjust(ContextInfo):
    global _adjust_logged
    if hasattr(ContextInfo, "is_last_bar") and not ContextInfo.is_last_bar():
        return None
    if not _adjust_logged:
        print("[bigqmt_signal_trader] adjust ok")
        _adjust_logged = True
    _drain_rpc_service(_build_config())
    return tick_app(ContextInfo, datetime.datetime.now())


def handlebar(ContextInfo):
    """Standard Big QMT bar callback."""
    return adjust(ContextInfo)


def on_order(ContextInfo, order):
    return forward_order_event(BigQmtRuntimeAdapter.to_order_event(order))


def on_trade(ContextInfo, trade):
    return forward_trade_event(BigQmtRuntimeAdapter.to_trade_event(trade))


def order_callback(ContextInfo, orderInfo):
    """Standard Big QMT order callback."""
    return on_order(ContextInfo, orderInfo)


def deal_callback(ContextInfo, dealInfo):
    """Standard Big QMT deal callback."""
    return on_trade(ContextInfo, dealInfo)


def sync_positions(ContextInfo):
    return sync_positions_app("manual")
