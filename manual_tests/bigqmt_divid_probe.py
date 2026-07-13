# coding: utf-8
"""大 QMT 复权因子（除权除息）数据探测。

这是一个只读策略，不提交任何订单。把它加载到「大 QMT 全终端」里运行，
init 阶段会打印若干只股票的 get_divid_factors 结果，用于确认大 QMT
是否真的返回复权因子数据。

原生调用约定（大 QMT 策略上下文）：
    ContextInfo.get_divid_factors(marketAndStock, date='')
    - marketAndStock: "600519.SH" 这类带市场的代码
    - date: 可选，单日字符串；不传则返回该股票全部历史分红送股记录

返回值：dict（已除权除息的字段字典），大小等于有分红记录的条数；无记录则为空 dict。
"""

_PROBED = False

# 选取有稳定分红历史的标的做探测（覆盖沪市/深市/不同板块）
_PROBE_CODES = [
    "600519.SH",  # 贵州茅台
    "000001.SZ",  # 平安银行
    "601398.SH",  # 工商银行
    "000651.SZ",  # 格力电器
    "300750.SZ",  # 宁德时代
]


def _probe_divid(ContextInfo):
    print("[divid_probe] ===== 开始探测 get_divid_factors =====")
    for code in _PROBE_CODES:
        try:
            # 1) 不带日期：取全部历史分红送股因子
            factors_all = ContextInfo.get_divid_factors(code)
            # 2) 带单个日期：取该日附近的因子（验证 date 参数可用）
            import datetime
            today = datetime.date.today().strftime("%Y%m%d")
            factors_date = ContextInfo.get_divid_factors(code, today)

            n_all = len(factors_all) if isinstance(factors_all, dict) else "非dict"
            n_date = len(factors_date) if isinstance(factors_date, dict) else "非dict"
            print(
                "[divid_probe] code=%s 全部记录数=%s 单日(date=%s)记录数=%s"
                % (code, n_all, today, n_date)
            )

            if isinstance(factors_all, dict) and factors_all:
                # 打印第一条的字段名与样例，确认返回结构
                first_key = next(iter(factors_all))
                first_val = factors_all[first_key]
                print(
                    "[divid_probe]   -> 首条 key=%s value类型=%s"
                    % (first_key, type(first_val).__name__)
                )
                # 若是嵌套 dict，列出子字段
                if isinstance(first_val, dict):
                    print("[divid_probe]   -> 子字段: %s" % ", ".join(first_val.keys()))
                    sample = {k: (str(v)[:40]) for k, v in list(first_val.items())[:6]}
                    print("[divid_probe]   -> 样例: %s" % sample)
        except Exception as exc:
            print("[divid_probe] code=%s 失败: %s" % (code, exc))
    print("[divid_probe] ===== 探测结束 =====")


def init(ContextInfo):
    global _PROBED
    if _PROBED:
        return
    _PROBED = True
    print("[divid_probe] init ok")
    _probe_divid(ContextInfo)


def handlebar(ContextInfo):
    # 只在最后一根 bar 再跑一次，避免刷屏
    if hasattr(ContextInfo, "is_last_bar") and not ContextInfo.is_last_bar():
        return None
    return _probe_divid(ContextInfo)


def adjust(ContextInfo):
    return handlebar(ContextInfo)
