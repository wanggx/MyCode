import logging

import akshare as ak
import pandas as pd

from hk.hkutil import saveHKDaily
from hk.hkutil import mergeHKDailyData

logger = logging.getLogger('myapp')

def saveHKStockDaily(dateStr):
    hk_spot = ak.stock_hk_spot()
    print(hk_spot.values)
    print(hk_spot.columns)

    # 重命名列
    hk_spot.rename(columns={'日期时间': 'trade_date', '代码': 'ts_code', '今开': 'open',
                            '最高': 'high', '最低': 'low', '最新价': 'close', '昨收': 'pre_close',
                            '涨跌幅': 'change', '涨跌额': 'pch_chg', '成交量': 'vol', '成交额': 'amount'}, inplace=True)

    # 只保留重命名后的列
    columns_to_keep = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pch_chg', 'vol',
                       'amount']
    hk_spot = hk_spot[columns_to_keep]

    # 检查 trade_date 列的类型
    print(hk_spot['trade_date'].dtype)  # 输出: object

    # 将 trade_date 列转换为 yyyyMMdd 格式的字符串
    hk_spot['trade_date'] = pd.to_datetime(hk_spot['trade_date'], format='%Y/%m/%d %H:%M:%S').dt.strftime('%Y%m%d')

    saveHKDaily(hk_spot)

def saveHkStockData(stock_pd):

    for index, stock in stock_pd.iterrows():
        logger.info(f"开始处理: {stock['ts_code']}")
        if stock['ts_code'] < '01620':
            logger.info(f"跳过: {stock['ts_code']}")
            continue
        saveSingleHkData(stock['ts_code'])

def saveSingleHkData(ts_code):
    """
    获取单只港股的历史数据并转换为标准格式
    输入列: date, open, high, low, close, volume
    输出列: trade_date, ts_code, open, high, low, close, pre_close, change, pch_chg, vol, amount
    """
    try:
        # 获取港股历史数据
        hk_stock = ak.stock_hk_daily(symbol=ts_code, adjust="")

        cutoff_date = pd.to_datetime('2020-01-01').date()
        hk_stock = hk_stock[hk_stock['date'] >= cutoff_date]
        # 重命名基础列
        hk_stock.rename(columns={
            'date': 'trade_date',
            'volume': 'vol'
        }, inplace=True)

        # 添加股票代码列
        hk_stock['ts_code'] = ts_code

        # 计算衍生字段
        hk_stock['pre_close'] = hk_stock['close'].shift(1)  # 前一日收盘价
        hk_stock['change'] = hk_stock['close'] - hk_stock['pre_close']  # 涨跌额
        hk_stock['pch_chg'] = (hk_stock['change'] / hk_stock['pre_close'] * 100).round(2)  # 涨跌幅(%)
        hk_stock['amount'] = hk_stock['close'] * hk_stock['vol']  # 成交额

        # 定义目标列顺序
        target_columns = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close',
                          'pre_close', 'change', 'pch_chg', 'vol', 'amount']

        # 对于不存在的列，添加空列
        for col in target_columns:
            if col not in hk_stock.columns:
                if col in ['pre_close', 'change', 'pch_chg', 'amount']:
                    hk_stock[col] = 0  # 数值型字段设为0
                else:
                    hk_stock[col] = None  # 其他字段设为None

        # 只保留目标列并按指定顺序排列
        hk_stock = hk_stock[target_columns]

        # 数据类型处理
        numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pch_chg', 'vol', 'amount']
        for col in numeric_columns:
            if col in hk_stock.columns:
                hk_stock[col] = pd.to_numeric(hk_stock[col], errors='coerce').fillna(0)

        # 日期格式处理
        if 'trade_date' in hk_stock.columns:
            hk_stock['trade_date'] = pd.to_datetime(hk_stock['trade_date'], format='%Y-%m-%d').dt.strftime('%Y%m%d')

        logger.info(f"ts_code, 保存{len(hk_stock)}条数据")

        saveHKDaily(hk_stock)
        mergeHKDailyData()

    except Exception as e:
        logger.info(f"获取港股数据失败: {e}")
        # 返回空的DataFrame，保持指定列结构
        empty_df = pd.DataFrame(columns=['trade_date', 'ts_code', 'open', 'high', 'low', 'close',
                                         'pre_close', 'change', 'pch_chg', 'vol', 'amount'])
        return empty_df
