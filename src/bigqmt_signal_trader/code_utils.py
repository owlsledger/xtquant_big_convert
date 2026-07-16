"""证券代码标准化和委托数量处理。"""

import re


_DIGIT_CODE_RE = re.compile(r"^\d{6}$")


def normalize_stock_code(code):
    """标准化/归一化股票code。
    
    Args:
        code: code
    
    Returns:
         — 处理结果。
    """
    text = str(code or "").strip().upper()
    if not text:
        return ""
    if text.startswith("SH") and _DIGIT_CODE_RE.match(text[2:]):
        return f"{text[2:]}.SH"
    if text.startswith("SZ") and _DIGIT_CODE_RE.match(text[2:]):
        return f"{text[2:]}.SZ"
    if text.endswith(".SH") or text.endswith(".SZ"):
        prefix = text[:6]
        if _DIGIT_CODE_RE.match(prefix):
            return text
    if _DIGIT_CODE_RE.match(text):
        market = "SH" if text.startswith(("5", "6")) else "SZ"
        return f"{text}.{market}"
    raise ValueError(f"invalid stock code: {code}")


def min_lot(stock_code):
    """minlot。
    
    Args:
        stock_code: 股票代码
    
    Returns:
         — 处理结果。
    """
    normalized = normalize_stock_code(stock_code)
    pure = normalized.split(".")[0]
    return 200 if pure.startswith("688") else 100


def round_buy_volume(stock_code, amount):
    """四舍五入buyvolume。
    
    Args:
        stock_code: 股票代码
        amount: amount
    
    Returns:
         — 处理结果。
    """
    lot = min_lot(stock_code)
    value = int(amount or 0)
    if value <= 0:
        return 0
    return (value // lot) * lot


def round_sell_volume(stock_code, amount, sell_all=False):
    """四舍五入sellvolume。
    
    Args:
        stock_code: 股票代码
        amount: amount
        sell_all: sellall
    
    Returns:
         — 处理结果。
    """
    value = int(amount or 0)
    if value <= 0:
        return 0
    if sell_all:
        return value
    lot = min_lot(stock_code)
    return (value // lot) * lot
