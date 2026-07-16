"""大 QMT 运行文件可复用的转发入口。"""

import datetime as _dt
import traceback


_APP = None


def reset_app():
    """重置app。
    """
    global _APP
    _APP = None


def get_app():
    """获取app。
    
    Returns:
         — 处理结果。
    """
    return _APP


def init_app(context_info, app_factory):
    """初始化app。
    
    Args:
        context_info: context信息
        app_factory: appfactory
    
    Returns:
         — 处理结果。
    """
    global _APP
    _APP = app_factory(context_info)
    if hasattr(_APP, "on_init"):
        _APP.on_init(context_info)
    return _APP


def tick_app(context_info, now=None):
    """tickapp。
    
    Args:
        context_info: context信息
        now: now
    
    Returns:
         — 处理结果。
    """
    if _APP is None:
        return None
    now = now or _dt.datetime.now()
    try:
        return _APP.tick(now)
    except Exception:
        print(traceback.format_exc())
        return None


def forward_order_event(event):
    """forward订单event。
    
    Args:
        event: event
    
    Returns:
         — 处理结果。
    """
    if _APP is None:
        return None
    return _APP.on_order_event(event)


def forward_trade_event(event):
    """forward成交event。
    
    Args:
        event: event
    
    Returns:
         — 处理结果。
    """
    if _APP is None:
        return None
    return _APP.on_trade_event(event)


def sync_positions_app(reason="manual"):
    """同步positionsapp。
    
    Args:
        reason: reason
    
    Returns:
         — 处理结果。
    """
    if _APP is None:
        return None
    return _APP.sync_positions(reason)
