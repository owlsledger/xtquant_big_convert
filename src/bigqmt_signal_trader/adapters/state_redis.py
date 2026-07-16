"""Redis signal state store."""

import datetime as _dt


class RedisStateStore:
    """redisstatestore，提供 claim, mark_submitted, mark_finished 等方法。
    """
    def __init__(
        self,
        redis_client,
        account_id="default",
        claim_key_template="bigqmt:signal_claim:{account_id}:{signal_id}",
        status_key_template="bigqmt:signal_status:{account_id}:{signal_id}",
        claim_ttl_seconds=3600,
        status_ttl_seconds=86400,
    ):
        """初始化实例，设置内部状态和依赖项。
        
        Args:
            redis_client: redisclient
            account_id: 账号ID
            claim_key_template: claim键模板
            status_key_template: status键模板
            claim_ttl_seconds: claimttlseconds
            status_ttl_seconds: statusttlseconds
        """
        self.redis = redis_client
        self.account_id = account_id
        self.claim_key_template = claim_key_template
        self.status_key_template = status_key_template
        self.claim_ttl_seconds = int(claim_ttl_seconds)
        self.status_ttl_seconds = int(status_ttl_seconds)
        self._accounts_by_signal_id = {}

    def _account_for(self, signal_id):
        """accountfor。
        
        Args:
            signal_id: 信号id
        
        Returns:
             — 处理结果。
        """
        return self._accounts_by_signal_id.get(signal_id) or self.account_id

    def _claim_key(self, account_id, signal_id):
        """claim键。
        
        Args:
            account_id: 账号ID
            signal_id: 信号id
        
        Returns:
             — 处理结果。
        """
        return self.claim_key_template.format(account_id=account_id, signal_id=signal_id)

    def _status_key(self, account_id, signal_id):
        """status键。
        
        Args:
            account_id: 账号ID
            signal_id: 信号id
        
        Returns:
             — 处理结果。
        """
        return self.status_key_template.format(account_id=account_id, signal_id=signal_id)

    @staticmethod
    def _now_text():
        """nowtext。
        
        Returns:
             — 处理结果。
        """
        return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write_status(self, account_id, signal_id, mapping):
        """writestatus。
        
        Args:
            account_id: 账号ID
            signal_id: 信号id
            mapping: mapping
        """
        key = self._status_key(account_id, signal_id)
        fields = {
            "signal_id": signal_id,
            "account_id": account_id,
            "updated_at": self._now_text(),
        }
        fields.update({k: "" if v is None else str(v) for k, v in mapping.items()})
        self.redis.hset(key, mapping=fields)
        if self.status_ttl_seconds > 0:
            self.redis.expire(key, self.status_ttl_seconds)

    def claim(self, signal, consumer_id):
        """claim。
        
        Args:
            signal: 信号
            consumer_id: consumerid
        
        Returns:
             — 处理结果。
        """
        account_id = signal.account_id or self.account_id
        self._accounts_by_signal_id[signal.signal_id] = account_id
        key = self._claim_key(account_id, signal.signal_id)
        ok = self.redis.set(key, consumer_id, nx=True, ex=self.claim_ttl_seconds)
        if ok:
            self._write_status(
                account_id,
                signal.signal_id,
                {
                    "status": "CLAIMED",
                    "consumer_id": consumer_id,
                    "stock_code": signal.stock_code,
                    "action": signal.action.value,
                    "message": "",
                },
            )
        return bool(ok)

    def mark_submitted(self, signal_id, result):
        """marksubmitted。
        
        Args:
            signal_id: 信号id
            result: result
        """
        account_id = self._account_for(signal_id)
        self._write_status(
            account_id,
            signal_id,
            {
                "status": result.status,
                "user_order_id": result.user_order_id,
                "order_sys_id": result.order_sys_id,
                "message": result.message,
            },
        )

    def mark_finished(self, signal_id, status, message=""):
        """markfinished。
        
        Args:
            signal_id: 信号id
            status: status
            message: message
        """
        account_id = self._account_for(signal_id)
        self._write_status(
            account_id,
            signal_id,
            {
                "status": status,
                "message": message,
            },
        )
