"""不发真实委托的下单 gateway，用于联调和回放。"""

import hashlib

from ..models import OrderSubmitResult


class DryRunOrderGateway:
    """DryRunOrder网关，提供 submit, cancel, query_orders, query_trades 等方法。
    """
    def __init__(self):
        """初始化实例，设置内部状态和依赖项。
        """
        self.submitted = []
        self.cancelled = []

    def submit(self, request):
        """submit。
        
        Args:
            request: 请求
        
        Returns:
             — 处理结果。
        """
        self.submitted.append(request)
        digest = hashlib.sha1(request.signal_id.encode("utf-8")).hexdigest()[:10]
        return OrderSubmitResult(
            status="DRY_RUN",
            user_order_id=f"dryrun:bq:{digest}:{request.signal_id}",
            order_sys_id=None,
        )

    def cancel(self, order_ref):
        """cancel。
        
        Args:
            order_ref: 订单ref
        
        Returns:
             — 处理结果。
        """
        self.cancelled.append(order_ref)
        return None

    def query_orders(self, account_id, strategy_name):
        """查询orders。
        
        Args:
            account_id: 账号ID
            strategy_name: 策略name
        
        Returns:
             — 处理结果。
        """
        return []

    def query_trades(self, account_id, strategy_name):
        """查询trades。
        
        Args:
            account_id: 账号ID
            strategy_name: 策略name
        
        Returns:
             — 处理结果。
        """
        return []
