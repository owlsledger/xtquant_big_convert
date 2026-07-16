"""大 QMT 运行环境适配器骨架。"""

import datetime as _dt


class BigQmtRuntimeAdapter:
    """BigQmtRuntime适配器，提供 now, to_order_event, to_trade_event 等方法。
    """
    def __init__(self, context_info):
        """初始化实例，设置内部状态和依赖项。
        
        Args:
            context_info: context信息
        """
        self.context_info = context_info

    def now(self):
        """now。
        
        Returns:
             — 处理结果。
        """
        return _dt.datetime.now()

    @staticmethod
    def to_order_event(order):
        """将当前对象转换为订单event格式返回。
        
        Args:
            order: 订单
        
        Returns:
             — 处理结果。
        """
        return order

    @staticmethod
    def to_trade_event(trade):
        """将当前对象转换为成交event格式返回。
        
        Args:
            trade: 成交
        
        Returns:
             — 处理结果。
        """
        return trade
