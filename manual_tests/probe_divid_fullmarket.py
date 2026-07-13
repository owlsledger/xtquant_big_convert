# coding: utf-8
"""全市场复权因子覆盖 + 历史深度探测。

1) 覆盖：对 stock_list 中全部股票(type='1')逐个调 get_divid_factors，统计
   有数据/为空/报错的数量。
2) 历史深度：对上市最早的若干只股票，打印其最早一条除权日，确认数据回溯到早期。

运行：
    set BIGQMT_ACCOUNT_ID=77001381
    python manual_tests/probe_divid_fullmarket.py
"""
import os
import sys
import time
import datetime

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC))
os.environ.setdefault("BIGQMT_ACCOUNT_ID", "77001381")

from xtquant import xtdata


# 早期上市标的（含已退市的"老八股"等），用于验证历史深度
OLD_CODES = [
    "600651.SH",  # 飞乐音响 1989(老八股)
    "600652.SH",  # 爱使股份 1989(老八股)
    "600653.SH",  # 申华控股 1989(老八股)
    "600654.SH",  # 飞乐股份 1989(老八股)
    "600656.SH",  # 浙江凤凰 1990(老八股)
    "600601.SH",  # 方正科技 1990
    "000001.SZ",  # 平安银行 1991
    "000002.SZ",  # 万科A 1991
    "600000.SH",  # 浦发银行 1999
    "600519.SH",  # 贵州茅台 2001
]


def ms_to_date(ms):
    try:
        return datetime.datetime.utcfromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d")
    except Exception:
        return str(ms)


def get_stock_codes():
    """从大 QMT 取沪深A股全部代码（仅当前上市）。"""
    codes = xtdata.get_stock_list_in_sector("沪深A股")
    codes = [c for c in codes if c and c.split(".")[-1] in ("SH", "SZ")]
    return [(c, "") for c in codes]


def main():
    codes = get_stock_codes()
    print("[full] stock_list 股票数(type='1'): %d" % len(codes))

    # 先测 5 只延迟
    t0 = time.time()
    for c in codes[:5]:
        xtdata.get_divid_factors(c[0])
    dt = (time.time() - t0) / 5.0
    print("[full] 单只平均延迟约 %.3fs -> 全量预计 %.1fs" % (dt, dt * len(codes)))

    with_data = 0
    empty = 0
    errors = []
    earliest_ms = None
    earliest_code = None
    # 记录最早上市且最早除权日的样本
    oldest_samples = codes[:15]
    depth_rows = []

    total = len(codes)
    t_start = time.time()
    for i, (code, ipo) in enumerate(codes):
        try:
            f = xtdata.get_divid_factors(code)
            if isinstance(f, dict) and f:
                with_data += 1
                mn = min(int(k) for k in f.keys())
                if earliest_ms is None or mn < earliest_ms:
                    earliest_ms = mn
                    earliest_code = code
            else:
                empty += 1
        except Exception as exc:
            errors.append((code, repr(exc)[:120]))
        if (i + 1) % 500 == 0 or (i + 1) == total:
            el = time.time() - t_start
            print("[full] 进度 %d/%d  有数据=%d 空=%d 错=%d  已用%.1fs" % (
                i + 1, total, with_data, empty, len(errors), el))

    print("\n===== 汇总 =====")
    print("股票总数        : %d" % total)
    print("有复权因子数据  : %d" % with_data)
    print("返回空(无分红)  : %d" % empty)
    print("调用报错        : %d" % len(errors))
    if errors[:5]:
        print("  报错样例: %s" % errors[:5])
    if earliest_ms is not None:
        print("全市场最早除权日: %s (code=%s)" % (ms_to_date(earliest_ms), earliest_code))

    print("\n===== 早期上市标的的历史深度(验证是否回溯到早期) =====")
    for code in OLD_CODES:
        try:
            f = xtdata.get_divid_factors(code)
            if isinstance(f, dict) and f:
                ms = sorted(int(k) for k in f.keys())
                print("  %s 记录数=%d 最早除权=%s 最近除权=%s" % (
                    code, len(ms), ms_to_date(ms[0]), ms_to_date(ms[-1])))
            else:
                print("  %s 无数据" % code)
        except Exception as exc:
            print("  %s 报错 %r" % (code, exc))


if __name__ == "__main__":
    main()
