# coding: utf-8
"""通过 Redis RPC 连运行中的大 QMT，探测 get_divid_factors 是否返回复权因子。

运行（在 qmt/xtquant_big_convert 下，确保 PYTHONPATH 含 src）：
    set BIGQMT_ACCOUNT_ID=8890831573
    python manual_tests/probe_divid_rpc.py
"""
import os
import sys
import json
import datetime

# 让 import xtquant 命中 shim 包
SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC))

os.environ.setdefault("BIGQMT_ACCOUNT_ID", "8890831573")

from xtquant import xtdata

CODES = [
    "600519.SH",  # 贵州茅台
    "000001.SZ",  # 平安银行
    "601398.SH",  # 工商银行
    "000651.SZ",  # 格力电器
    "300750.SZ",  # 宁德时代
]


def main():
    print("[probe] 客户端 xtdata 已加载, account=%s" % os.environ.get("BIGQMT_ACCOUNT_ID"))
    today = datetime.date.today().strftime("%Y%m%d")
    for code in CODES:
        try:
            all_f = xtdata.get_divid_factors(code)
            date_f = xtdata.get_divid_factors(code, "", today)
            n_all = len(all_f) if isinstance(all_f, dict) else "非dict:%s" % type(all_f).__name__
            n_date = len(date_f) if isinstance(date_f, dict) else "非dict:%s" % type(date_f).__name__
            print("[probe] code=%s 全部记录数=%s 单日(date=%s)记录数=%s" % (code, n_all, today, n_date))
            if isinstance(all_f, dict) and all_f:
                fk = next(iter(all_f))
                fv = all_f[fk]
                print("[probe]   首条 key=%s value类型=%s" % (fk, type(fv).__name__))
                if isinstance(fv, dict):
                    print("[probe]   子字段: %s" % ", ".join(fv.keys()))
                    sample = {k: str(v)[:40] for k, v in list(fv.items())[:6]}
                    print("[probe]   样例: %s" % json.dumps(sample, ensure_ascii=False))
        except Exception as exc:
            print("[probe] code=%s 失败: %r" % (code, exc))
    print("[probe] 完成")


if __name__ == "__main__":
    main()
