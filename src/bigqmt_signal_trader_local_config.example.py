# coding: utf-8
"""Local private config example for the QMT python directory.

Copy this file to the QMT python directory as:

    bigqmt_signal_trader_local_config.py

Do not commit the real file. It may contain account ids and Redis credentials.
"""

BIGQMT_ACCOUNT_ID = "YOUR_ACCOUNT_ID"

BIGQMT_REDIS_CONFIG = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 5,
    "username": "",
    "password": "",
    # Keep order RPC disabled unless you explicitly want remote order/cancel.
    "rpc_allow_order_methods": False,
}
