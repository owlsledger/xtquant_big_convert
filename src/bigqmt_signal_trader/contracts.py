"""可替换 adapter 的接口定义。"""

import datetime as _dt
from typing import Dict, List

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol

from .models import (
    AccountSnapshot,
    AssetSnapshot,
    CancelResult,
    OrderRef,
    OrderRequest,
    OrderSnapshot,
    OrderSubmitResult,
    PositionSnapshot,
    TradeSignal,
    TradeSnapshot,
)


class SignalSource(Protocol):
    """信号source，继承自 Protocol，提供 fetch, ack 等方法。
    """
    def fetch(self, account_id: str, limit: int) -> List[TradeSignal]:
        ...

    def ack(self, signal: TradeSignal) -> None:
        ...


class MarketDataProvider(Protocol):
    """MarketData提供者，继承自 Protocol，提供 get_ticks, get_instrument 等方法。
    """
    def get_ticks(self, codes: List[str]) -> Dict[str, dict]:
        ...

    def get_instrument(self, code: str) -> dict:
        ...


class PositionProvider(Protocol):
    """Position提供者，继承自 Protocol，提供 get_positions, get_asset 等方法。
    """
    def get_positions(self, account_id: str) -> Dict[str, PositionSnapshot]:
        ...

    def get_asset(self, account_id: str) -> AssetSnapshot:
        ...


class OrderGateway(Protocol):
    """Order网关，继承自 Protocol，提供 submit, cancel, query_orders, query_trades 等方法。
    """
    def submit(self, request: OrderRequest) -> OrderSubmitResult:
        ...

    def cancel(self, order_ref: OrderRef) -> CancelResult:
        ...

    def query_orders(self, account_id: str, strategy_name: str) -> List[OrderSnapshot]:
        ...

    def query_trades(self, account_id: str, strategy_name: str) -> List[TradeSnapshot]:
        ...


class PositionSyncSink(Protocol):
    """持仓syncsink，继承自 Protocol，提供 publish 等方法。
    """
    def publish(self, snapshot: AccountSnapshot) -> None:
        ...


class StateStore(Protocol):
    """statestore，继承自 Protocol，提供 claim, mark_submitted, mark_finished 等方法。
    """
    def claim(self, signal: TradeSignal, consumer_id: str) -> bool:
        ...

    def mark_submitted(self, signal_id: str, result: OrderSubmitResult) -> None:
        ...

    def mark_finished(self, signal_id: str, status: str, message: str = "") -> None:
        ...


class RuntimeAdapter(Protocol):
    """Runtime适配器，继承自 Protocol，提供 now 等方法。
    """
    def now(self) -> _dt.datetime:
        ...
