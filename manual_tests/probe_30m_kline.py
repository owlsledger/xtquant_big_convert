# coding: utf-8
"""探测大QMT 30分钟K线数据可用性（直接获取 vs 先下载后获取）"""
import sys, os, json

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC))

os.environ.setdefault("BIGQMT_ACCOUNT_ID", "8890831573")

from xtquant import xtdata


def try_fetch(code, period, label):
    print("=== %s period=%s ===" % (label, period))
    try:
        d = xtdata.get_market_data_ex(stock_list=[code], period=period, count=5)
        if code in d and d[code] is not None:
            df = d[code]
            print("  返回类型: %s" % type(df).__name__)
            if hasattr(df, "shape"):
                print("  形状: %s" % str(df.shape))
            if hasattr(df, "columns"):
                print("  列: %s" % list(df.columns))
            print("  样例:")
            print(df.tail(3))
            return True
        else:
            print("  数据为空/无此key")
            return False
    except Exception as e:
        print("  失败: %s" % repr(e)[:200])
        return False


code = "600519.SH"

# 1) 1分钟 K 线 (作为对照)
try_fetch(code, "1m", "对照-1分钟")

# 2) 30分钟 K 线 — 直接获取
ok = try_fetch(code, "30m", "直接获取")

# 3) 如果直接不行，试 download_history_data2
if not ok:
    print()
    print("=== 尝试 download_history_data2 period=30m ===")
    try:
        r = xtdata.download_history_data2(stock_list=[code], period="30m")
        print("  下载返回: %s" % r)
    except Exception as e:
        print("  下载失败: %s" % repr(e)[:200])

    # 4) 下载后再试
    try_fetch(code, "30m", "下载后再获取")

# 5) 也试一下 get_local_data
print()
print("=== get_local_data period=30m ===")
try:
    ld = xtdata.get_local_data(stock_list=[code], period="30m", count=5)
    if code in ld and ld[code] is not None:
        print("  形状: %s" % str(ld[code].shape))
        print(ld[code].tail(3))
    else:
        print("  无数据")
except Exception as e:
    print("  失败: %s" % repr(e)[:200])

print()
print("=== 探测完成 ===")
