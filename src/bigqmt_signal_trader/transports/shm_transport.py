"""Shared-memory transport stub.

Reserved for a future low-latency same-host backend. Not implemented because
the QMT runtime ships Python 3.6, where ``multiprocessing.shared_memory`` is
unavailable (added in 3.8). A ``mmap``-plus-named-mutex implementation is
possible but non-trivial; until it lands, selecting this transport raises a
clear error so misconfiguration fails fast.
"""

from .base import RpcTransport, TransportError


class SharedMemoryTransport(RpcTransport):
    """SharedMemory传输层，继承自 RpcTransport，提供 send_request, send_response, start_receiving 等方法。
    """
    name = "shm"

    def __init__(self, account_id="", print_prefix="[bigqmt_rpc]", **kwargs):
        """初始化实例，设置内部状态和依赖项。
        
        Args:
            account_id: 账号ID
            print_prefix: print前缀
            kwargs: kwargs
        """
        super(SharedMemoryTransport, self).__init__(
            account_id=account_id, print_prefix=print_prefix
        )

    def _unsupported(self):
        """unsupported。
        """
        raise TransportError(
            "shared-memory transport is not implemented yet "
            "(requires Python 3.8+ shared_memory or a custom mmap ring buffer)"
        )

    def send_request(self, request, timeout_seconds):
        """发送请求。
        
        Args:
            request: 请求
            timeout_seconds: 超时(秒)seconds
        """
        self._unsupported()

    def send_response(self, request, response):
        """发送响应。
        
        Args:
            request: 请求
            response: 响应
        """
        self._unsupported()

    def start_receiving(self, on_request, **kwargs):
        """启动receiving。
        
        Args:
            on_request: on请求
            kwargs: kwargs
        """
        self._unsupported()
