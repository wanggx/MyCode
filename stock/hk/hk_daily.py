

import akshare as ak
import pandas as pd

from hk.hkutil import saveHKDaily


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

