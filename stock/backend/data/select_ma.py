from datetime import datetime, timedelta

import pandas as pd

from moduledir.chatutil import sendMsg, sendGroupFile
from moduledir.stockutil import getStockData, getStockList

def ma(df):
    if df is None or len(df) == 0:
        print('计算ma均线: 输入df为空')
        return None
    try:
        df.sort_values(by=['trade_date'], inplace=True, ascending=True)
        df['ma3'] = df['close'].rolling(3).mean()
        df['ma5'] = df['close'].rolling(5).mean()

        # 创建一个辅助函数来处理整个DataFrame
        def check_last_n_days(n):
            last_n_days = df.tail(n)
            return (last_n_days['ma3'] > last_n_days['ma5']).all()

        # 使用 agg 进行多列聚合
        result = pd.Series({
            'ma35_3': check_last_n_days(3),
            'ma35_5': check_last_n_days(5),
            'ma3': df.tail(1)['ma3'].values[0],
            'ma5': df.tail(1)['ma5'].values[0]
        })

        return result
    except Exception as e:
        print(f'计算ma异常: {e}')
        return None


def selectMa(date_str, n):
    """
    date_str: 结束日期（字符串，格式如'20250710'）
    n: 向前推的天数
    """
    import time
    start_time = time.time()
    # 发送开始选股消息
    sendMsg(f"开始{date_str}的均线选股")
    # 计算startDate
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n-1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockData('001317.SZ', start_str, date_str)

    close_ma_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'low']].groupby(['ts_code']).tail(60)
    stock_ma_df = (close_ma_df.groupby(['ts_code'])
                         .filter(lambda x: x['trade_date'].max() == date_str)
                         .groupby(['ts_code'])
                         .apply(ma, include_groups=False).reset_index())
    if stock_ma_df is None or len(stock_ma_df) == 0:
        sendMsg(f"{date_str}没有选中任何股票")
        return None

    stock_ma_df = stock_ma_df[stock_ma_df['ma35_3']
                              & stock_ma_df['ma35_5']]
    stock_ma_df.insert(0, 'select_date', date_str)
    stock_df = getStockList()
    join_df = pd.merge(stock_ma_df, stock_df[['ts_code', 'name']], on='ts_code', how='left')
    print(join_df.columns)
    final_df = join_df[['select_date', 'ts_code', 'name', 'ma35_3', 'ma35_5', 'ma3', 'ma5']].round(3)
    final_df.to_csv('ma35.csv', index=True)
    sendGroupFile('ma35.csv')
    # 发送结束选股消息
    elapsed = int(time.time() - start_time)
    sendMsg(f"结束{date_str}的均线选股，耗时{elapsed}s")
