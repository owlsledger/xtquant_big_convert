"""Big QMT order gateway.

The passorder signature follows src/api/qmt_jq_trade.
"""

import hashlib

from ..code_utils import normalize_stock_code
from ..models import CancelResult, OrderSnapshot, OrderSubmitResult, SignalAction, TradeSnapshot
from .position_bigqmt import _attr, _full_code


PRICE_TYPE_ALIASES = {
    "LIMIT": 11,
    "FIX_PRICE": 11,
    "LATEST_PRICE": 5,
    "MARKET_PEER_PRICE_FIRST": 44,
    "MARKET_SH_CONVERT_5_LIMIT": 43,
    "MARKET_SZ_CONVERT_5_CANCEL": 47,
}


def _action_from_offset_flag(offset_flag):
    """actionfromoffsetflag。
    
    Args:
        offset_flag: offsetflag
    
    Returns:
         — 处理结果。
    """
    return SignalAction.BUY.value if int(offset_flag or 0) == 48 else SignalAction.SELL.value


def _price_type_value(value, default):
    """pricetype值。
    
    Args:
        value: 值
        default: default
    
    Returns:
         — 处理结果。
    """
    if value is None or value == "":
        return int(default)
    try:
        return int(value)
    except (TypeError, ValueError):
        text = str(value).strip().upper()
        return int(PRICE_TYPE_ALIASES.get(text, default))


class BigQmtOrderGateway:
    """BigQmtOrder网关，提供 build_user_order_id, submit, cancel, query_orders, query_trades 等方法。
    """
    def __init__(
        self,
        context_info,
        account_id="",
        passorder_func=None,
        cancel_func=None,
        get_trade_detail_data_func=None,
        account_type="STOCK",
        combo_type=1101,
        price_type=11,
        quick_trade=2,
    ):
        """初始化实例，设置内部状态和依赖项。
        
        Args:
            context_info: context信息
            account_id: 账号ID
            passorder_func: passorderfunc
            cancel_func: cancelfunc
            get_trade_detail_data_func: get成交detaildatafunc
            account_type: 账号类型
            combo_type: combotype
            price_type: pricetype
            quick_trade: quick成交
        """
        self.context_info = context_info
        self.account_id = account_id
        self.passorder = passorder_func
        self.cancel_func = cancel_func
        self.get_trade_detail_data = get_trade_detail_data_func
        self.account_type = account_type
        self.combo_type = combo_type
        self.price_type = price_type
        self.quick_trade = quick_trade

    def _require_passorder(self):
        """requirepassorder。
        
        Returns:
             — 处理结果。
        """
        if self.passorder is None:
            raise RuntimeError("passorder is not available in Big QMT runtime")
        return self.passorder

    def _require_cancel(self):
        """requirecancel。
        
        Returns:
             — 处理结果。
        """
        if self.cancel_func is None:
            raise RuntimeError("cancel is not available in Big QMT runtime")
        return self.cancel_func

    def _require_query_func(self):
        """requirequeryfunc。
        
        Returns:
             — 处理结果。
        """
        if self.get_trade_detail_data is None:
            raise RuntimeError("get_trade_detail_data is not available in Big QMT runtime")
        return self.get_trade_detail_data

    @staticmethod
    def build_user_order_id(signal_id):
        """构建user订单id。
        
        Args:
            signal_id: 信号id
        
        Returns:
             — 处理结果。
        """
        text = str(signal_id or "")
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
        return "bq:%s:%s" % (digest, text[:30])

    def submit(self, request):
        """submit。
        
        Args:
            request: 请求
        
        Returns:
             — 处理结果。
        """
        passorder = self._require_passorder()
        action = str(request.action).upper()
        if action == SignalAction.BUY.value:
            op_type = 23
        elif action == SignalAction.SELL.value:
            op_type = 24
        else:
            raise ValueError("unsupported order action: %s" % request.action)

        user_order_id = self.build_user_order_id(request.signal_id)
        account_id = request.account_id or self.account_id
        passorder(
            op_type,
            self.combo_type,
            account_id,
            normalize_stock_code(request.stock_code),
            _price_type_value(request.price_type, self.price_type),
            float(request.price),
            int(request.volume),
            request.strategy_name,
            self.quick_trade,
            user_order_id,
            self.context_info,
        )
        return OrderSubmitResult(
            status="SUBMITTED",
            user_order_id=user_order_id,
            order_sys_id=None,
            message="passorder submitted",
        )

    def cancel(self, order_ref):
        """cancel。
        
        Args:
            order_ref: 订单ref
        
        Returns:
             — 处理结果。
        """
        cancel_func = self._require_cancel()
        ok = cancel_func(order_ref.order_sys_id, self.account_id, self.account_type, self.context_info)
        return CancelResult(success=bool(ok), message="" if ok else "cancel returned false")

    def query_orders(self, account_id, strategy_name):
        """查询orders。
        
        Args:
            account_id: 账号ID
            strategy_name: 策略name
        
        Returns:
             — 处理结果。
        """
        query = self._require_query_func()
        # QMT's get_trade_detail_data can raise on ORDER queries in some states
        # (e.g. context not bound). Degrade to empty like query_trades does.
        try:
            rows = query(account_id, self.account_type, "ORDER", strategy_name) or []
        except Exception:
            return []
        result = []
        for row in rows:
            result.append(
                OrderSnapshot(
                    order_sys_id=str(_attr(row, ("m_strOrderSysID", "order_sys_id"), "") or ""),
                    user_order_id=str(_attr(row, ("m_strRemark", "user_order_id", "remark"), "") or ""),
                    stock_code=_full_code(
                        _attr(row, ("m_strInstrumentID", "instrument_id", "stock_code")),
                        _attr(row, ("m_strExchangeID", "exchange_id", "market")),
                    ),
                    action=_action_from_offset_flag(_attr(row, ("m_nOffsetFlag", "offset_flag"), 0)),
                    volume=int(_attr(row, ("m_nVolumeTotalOriginal", "volume"), 0) or 0),
                    traded_volume=int(_attr(row, ("m_nVolumeTraded", "traded_volume"), 0) or 0),
                    status=str(_attr(row, ("m_nOrderStatus", "status"), "") or ""),
                    price=float(_attr(row, ("m_dLimitPrice", "m_dPrice", "price"), 0.0) or 0.0),
                    strategy_name=str(_attr(row, ("m_strStrategyName", "strategy_name"), "") or ""),
                    remark=str(_attr(row, ("m_strRemark", "remark"), "") or ""),
                )
            )
        return result

    def query_trades(self, account_id, strategy_name):
        """查询trades。
        
        Args:
            account_id: 账号ID
            strategy_name: 策略name
        
        Returns:
             — 处理结果。
        """
        query = self._require_query_func()
        rows = []
        for detail_type in ("DEAL", "TRADE"):
            try:
                rows = query(account_id, self.account_type, detail_type, strategy_name) or []
                if rows:
                    break
            except Exception:
                rows = []
        result = []
        for row in rows:
            result.append(
                TradeSnapshot(
                    trade_id=str(_attr(row, ("m_strTradeID", "trade_id"), "") or ""),
                    order_sys_id=str(_attr(row, ("m_strOrderSysID", "order_sys_id"), "") or ""),
                    stock_code=_full_code(
                        _attr(row, ("m_strInstrumentID", "instrument_id", "stock_code")),
                        _attr(row, ("m_strExchangeID", "exchange_id", "market")),
                    ),
                    action=_action_from_offset_flag(_attr(row, ("m_nOffsetFlag", "offset_flag"), 0)),
                    volume=int(_attr(row, ("m_nVolume", "volume"), 0) or 0),
                    price=float(_attr(row, ("m_dPrice", "m_dTradePrice", "price"), 0.0) or 0.0),
                    traded_at=str(_attr(row, ("m_strTradeTime", "trade_time", "traded_at"), "") or ""),
                )
            )
        return result
