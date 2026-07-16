# coding: utf-8
"""Big QMT diagnostics for market data and positions.

This strategy entry never submits orders. It only probes QMT runtime APIs.
"""


_ACCOUNT_ID = ""
_PROBED = False


def _resolve_runtime_name(name):
    """resolveruntimename。
    
    Args:
        name: name
    
    Returns:
         — 处理结果。
    """
    if name in globals():
        return globals()[name]
    try:
        import builtins
        return getattr(builtins, name)
    except Exception:
        return None


def _safe_attr(obj, name, default=None):
    """safeattr。
    
    Args:
        obj: obj
        name: name
        default: default
    
    Returns:
         — 处理结果。
    """
    return getattr(obj, name, default)


def _detect_account():
    """detectaccount。
    
    Returns:
         — 处理结果。
    """
    account_value = _resolve_runtime_name("account")
    return str(account_value or "")


def _probe_market(ContextInfo):
    """probe市场。
    
    Args:
        ContextInfo: context信息
    """
    code = "000300.SH"
    try:
        ticks = ContextInfo.get_full_tick([code])
        tick = (ticks or {}).get(code)
        if not tick:
            print("[bigqmt_diagnostic] market tick missing code=%s raw=%s" % (code, ticks))
        else:
            print(
                "[bigqmt_diagnostic] market tick ok code=%s lastPrice=%s bid1=%s ask1=%s"
                % (
                    code,
                    tick.get("lastPrice"),
                    (tick.get("bidPrice") or [None])[0],
                    (tick.get("askPrice") or [None])[0],
                )
            )
    except Exception as exc:
        print("[bigqmt_diagnostic] market tick failed: %s" % exc)

    try:
        detail = ContextInfo.get_instrumentdetail(code)
        if not detail:
            print("[bigqmt_diagnostic] instrument missing code=%s" % code)
        else:
            print(
                "[bigqmt_diagnostic] instrument ok code=%s status=%s up=%s down=%s"
                % (
                    code,
                    detail.get("InstrumentStatus"),
                    detail.get("UpStopPrice"),
                    detail.get("DownStopPrice"),
                )
            )
    except Exception as exc:
        print("[bigqmt_diagnostic] instrument failed: %s" % exc)


def _probe_positions(account_id):
    """probepositions。
    
    Args:
        account_id: 账号ID
    """
    query = _resolve_runtime_name("get_trade_detail_data")
    if query is None:
        print("[bigqmt_diagnostic] position failed: get_trade_detail_data missing")
        return
    if not account_id:
        print("[bigqmt_diagnostic] position skipped: account is empty")
        return

    try:
        positions = query(account_id, "STOCK", "POSITION") or []
        print("[bigqmt_diagnostic] position ok account=%s count=%s" % (account_id, len(positions)))
        for pos in positions[:8]:
            print(
                "[bigqmt_diagnostic] position item code=%s.%s name=%s volume=%s available=%s"
                % (
                    _safe_attr(pos, "m_strInstrumentID", ""),
                    _safe_attr(pos, "m_strExchangeID", ""),
                    _safe_attr(pos, "m_strInstrumentName", ""),
                    _safe_attr(pos, "m_nVolume", ""),
                    _safe_attr(pos, "m_nCanUseVolume", ""),
                )
            )
    except Exception as exc:
        print("[bigqmt_diagnostic] position failed account=%s error=%s" % (account_id, exc))


def _probe(ContextInfo, reason):
    """probe。
    
    Args:
        ContextInfo: context信息
        reason: reason
    """
    global _PROBED
    if _PROBED:
        return
    _PROBED = True
    print("[bigqmt_diagnostic] probe start reason=%s account=%s" % (reason, _ACCOUNT_ID))
    _probe_market(ContextInfo)
    _probe_positions(_ACCOUNT_ID)
    print("[bigqmt_diagnostic] probe end")


def init(ContextInfo):
    """init。
    
    Args:
        ContextInfo: context信息
    """
    global _ACCOUNT_ID
    _ACCOUNT_ID = _detect_account()
    if _ACCOUNT_ID and hasattr(ContextInfo, "set_account"):
        ContextInfo.set_account(_ACCOUNT_ID)
    print("[bigqmt_diagnostic] init ok account=%s" % _ACCOUNT_ID)
    _probe(ContextInfo, "init")


def handlebar(ContextInfo):
    """处理bar。
    
    Args:
        ContextInfo: context信息
    
    Returns:
         — 处理结果。
    """
    if hasattr(ContextInfo, "is_last_bar") and not ContextInfo.is_last_bar():
        return None
    return _probe(ContextInfo, "handlebar")


def adjust(ContextInfo):
    """复权因子。
    
    Args:
        ContextInfo: context信息
    
    Returns:
         — 处理结果。
    """
    return handlebar(ContextInfo)


def order_callback(ContextInfo, orderInfo):
    """订单回调函数。
    
    Args:
        ContextInfo: context信息
        orderInfo: 订单信息
    
    Returns:
         — 处理结果。
    """
    return None


def deal_callback(ContextInfo, dealInfo):
    """deal回调函数。
    
    Args:
        ContextInfo: context信息
        dealInfo: deal信息
    
    Returns:
         — 处理结果。
    """
    return None
