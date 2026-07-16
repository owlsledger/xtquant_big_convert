import bigqmt_signal_trader.xtquant_compat as _compat


def __getattr__(name):
    """getattr。
    
    Args:
        name: name
    
    Returns:
         — 处理结果。
    """
    return getattr(_compat.xtdata, name)


def get_full_tick(code_list):
    """获取fulltick。
    
    Args:
        code_list: codelist
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_full_tick(code_list)


def get_market_data(field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1, dividend_type="none", fill_data=True):
    """获取市场data。
    
    Args:
        field_list: fieldlist
        stock_list: 股票list
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        dividend_type: 除权除息type
        fill_data: filldata
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_market_data(field_list, stock_list, period, start_time, end_time, count, dividend_type, fill_data)


def get_market_data_ex(field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1, dividend_type="none", fill_data=True):
    """获取市场dataex。
    
    Args:
        field_list: fieldlist
        stock_list: 股票list
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        dividend_type: 除权除息type
        fill_data: filldata
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_market_data_ex(field_list, stock_list, period, start_time, end_time, count, dividend_type, fill_data)


def get_local_data(field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1, dividend_type="none", fill_data=True, data_dir=None):
    """获取localdata。
    
    Args:
        field_list: fieldlist
        stock_list: 股票list
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        dividend_type: 除权除息type
        fill_data: filldata
        data_dir: datadir
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_local_data(field_list, stock_list, period, start_time, end_time, count, dividend_type, fill_data, data_dir)


def get_instrument_detail(stock_code):
    """获取instrumentdetail。
    
    Args:
        stock_code: 股票代码
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_instrument_detail(stock_code)


def get_instrumentdetail(stock_code):
    """获取instrumentdetail。
    
    Args:
        stock_code: 股票代码
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_instrumentdetail(stock_code)


def get_instrument_type(stock_code, variety_list=None):
    """获取instrumenttype。
    
    Args:
        stock_code: 股票代码
        variety_list: varietylist
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_instrument_type(stock_code, variety_list)


def get_stock_list_in_sector(sector_name, real_timetag=-1):
    """获取股票listinsector。
    
    Args:
        sector_name: sectorname
        real_timetag: realtimetag
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_stock_list_in_sector(sector_name, real_timetag=real_timetag)


def get_sector_list():
    """获取sectorlist。
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_sector_list()


def get_sector_info(sector_name=""):
    """获取sector信息。
    
    Args:
        sector_name: sectorname
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_sector_info(sector_name)


def subscribe_quote(stock_code, period="1d", start_time="", end_time="", count=0, callback=None):
    """订阅quote。
    
    Args:
        stock_code: 股票代码
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        callback: 回调函数
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.subscribe_quote(stock_code, period, start_time, end_time, count, callback)


def subscribe_quote2(stock_code, period="1d", start_time="", end_time="", count=0, dividend_type=None, callback=None):
    """订阅quote2。
    
    Args:
        stock_code: 股票代码
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        dividend_type: 除权除息type
        callback: 回调函数
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.subscribe_quote2(stock_code, period, start_time, end_time, count, dividend_type, callback)


def subscribe_whole_quote(code_list, callback=None):
    """订阅wholequote。
    
    Args:
        code_list: codelist
        callback: 回调函数
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.subscribe_whole_quote(code_list, callback=callback)


def unsubscribe_quote(seq):
    """unsubscribequote。
    
    Args:
        seq: seq
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.unsubscribe_quote(seq)


def run():
    """run。
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.run()


def get_divid_factors(stock_code, start_time="", end_time=""):
    """获取dividfactors。
    
    Args:
        stock_code: 股票代码
        start_time: starttime
        end_time: endtime
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_divid_factors(stock_code, start_time, end_time)


def getDividFactors(*args, **kwargs):
    """获取dividfactors。
    
    Args:
        args: args
        kwargs: kwargs
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_divid_factors(*args, **kwargs)


def download_history_data(stock_code, period, start_time="", end_time="", incrementally=None):
    """downloadhistorydata。
    
    Args:
        stock_code: 股票代码
        period: period
        start_time: starttime
        end_time: endtime
        incrementally: incrementally
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.download_history_data(stock_code, period, start_time, end_time, incrementally)


def download_history_data2(stock_list, period, start_time="", end_time="", callback=None, incrementally=None):
    """downloadhistorydata2。
    
    Args:
        stock_list: 股票list
        period: period
        start_time: starttime
        end_time: endtime
        callback: 回调函数
        incrementally: incrementally
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.download_history_data2(stock_list, period, start_time, end_time, callback, incrementally)


def get_trading_dates(market, start_time="", end_time="", count=-1):
    """获取tradingdates。
    
    Args:
        market: 市场
        start_time: starttime
        end_time: endtime
        count: count
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_trading_dates(market, start_time, end_time, count)


def get_holidays():
    """获取holidays。
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_holidays()


def download_holiday_data(incrementally=True):
    """downloadholidaydata。
    
    Args:
        incrementally: incrementally
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.download_holiday_data(incrementally)


def get_ipo_info(start_time="", end_time=""):
    """获取ipo信息。
    
    Args:
        start_time: starttime
        end_time: endtime
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_ipo_info(start_time, end_time)


def get_etf_info():
    """获取etf信息。
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_etf_info()


def download_etf_info():
    """downloadetf信息。
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.download_etf_info()


def get_option_list(undl_code, dedate, opttype="", isavailavle=False):
    """获取optionlist。
    
    Args:
        undl_code: undlcode
        dedate: dedate
        opttype: opttype
        isavailavle: isavailavle
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_option_list(undl_code, dedate, opttype, isavailavle)


def get_his_option_list(undl_code, dedate):
    """获取hisoptionlist。
    
    Args:
        undl_code: undlcode
        dedate: dedate
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_his_option_list(undl_code, dedate)


def get_his_option_list_batch(undl_code, start_time="", end_time=""):
    """获取hisoptionlistbatch。
    
    Args:
        undl_code: undlcode
        start_time: starttime
        end_time: endtime
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_his_option_list_batch(undl_code, start_time, end_time)


def get_financial_data(stock_list, table_list=[], start_time="", end_time="", report_type="report_time"):
    """获取financialdata。
    
    Args:
        stock_list: 股票list
        table_list: tablelist
        start_time: starttime
        end_time: endtime
        report_type: reporttype
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_financial_data(stock_list, table_list, start_time, end_time, report_type)


def download_financial_data(stock_list, table_list=[], start_time="", end_time="", incrementally=None):
    """downloadfinancialdata。
    
    Args:
        stock_list: 股票list
        table_list: tablelist
        start_time: starttime
        end_time: endtime
        incrementally: incrementally
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.download_financial_data(stock_list, table_list, start_time, end_time, incrementally)


def download_financial_data2(stock_list, table_list=[], start_time="", end_time="", callback=None):
    """downloadfinancialdata2。
    
    Args:
        stock_list: 股票list
        table_list: tablelist
        start_time: starttime
        end_time: endtime
        callback: 回调函数
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.download_financial_data2(stock_list, table_list, start_time, end_time, callback)


def call_formula(formula_name, stock_code, period, start_time="", end_time="", count=-1, dividend_type=None, extend_param={}):
    """callformula。
    
    Args:
        formula_name: formulaname
        stock_code: 股票代码
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        dividend_type: 除权除息type
        extend_param: extendparam
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.call_formula(formula_name, stock_code, period, start_time, end_time, count, dividend_type, extend_param)


def subscribe_formula(formula_name, stock_code, period, start_time="", end_time="", count=-1, dividend_type=None, extend_param={}, callback=None):
    """订阅formula。
    
    Args:
        formula_name: formulaname
        stock_code: 股票代码
        period: period
        start_time: starttime
        end_time: endtime
        count: count
        dividend_type: 除权除息type
        extend_param: extendparam
        callback: 回调函数
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.subscribe_formula(formula_name, stock_code, period, start_time, end_time, count, dividend_type, extend_param, callback)


def unsubscribe_formula(request_id):
    """unsubscribeformula。
    
    Args:
        request_id: 请求id
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.unsubscribe_formula(request_id)


def get_formula_result(request_id, start_time="", end_time="", count=-1, timeout_second=-1):
    """获取formularesult。
    
    Args:
        request_id: 请求id
        start_time: starttime
        end_time: endtime
        count: count
        timeout_second: 超时(秒)second
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.get_formula_result(request_id, start_time, end_time, count, timeout_second)


def gen_factor_index(data_name, formula_name, vars, sector_list, start_time="", end_time="", period="1d", dividend_type="none"):
    """gen因子索引。
    
    Args:
        data_name: dataname
        formula_name: formulaname
        vars: vars
        sector_list: sectorlist
        start_time: starttime
        end_time: endtime
        period: period
        dividend_type: 除权除息type
    
    Returns:
         — 处理结果。
    """
    return _compat.xtdata.gen_factor_index(data_name, formula_name, vars, sector_list, start_time, end_time, period, dividend_type)
