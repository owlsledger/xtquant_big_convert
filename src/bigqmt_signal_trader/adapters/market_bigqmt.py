"""Big QMT market data adapter.

This module only wraps ContextInfo. It does not make trading decisions.
"""

from ..code_utils import normalize_stock_code


class BigQmtMarketDataProvider:
    def __init__(self, context_info):
        self.context_info = context_info

    def get_ticks(self, codes):
        normalized_codes = [normalize_stock_code(code) for code in codes]
        data = self.context_info.get_full_tick(normalized_codes)
        return data or {}

    def get_instrument(self, code):
        normalized = normalize_stock_code(code)
        data = self.context_info.get_instrumentdetail(normalized)
        return data or {}
