import logging
import time
from moduledir.stockutil import *
from datetime import datetime, timedelta

logger = logging.getLogger('myapp')


def download_daily_data(startDate, endDate):
    """
    遍历 startDate 和 endDate 之间的所有日期
    
    Args:
        startDate (str): 开始日期，格式为 yyyyMMdd
        endDate (str): 结束日期，格式为 yyyyMMdd
    
    Returns:
        list: 包含所有日期的列表，格式为 yyyyMMdd
    """
    try:
        # 将字符串转换为 datetime 对象
        start_dt = datetime.strptime(startDate, '%Y%m%d')
        end_dt = datetime.strptime(endDate, '%Y%m%d')
        
        # 确保开始日期不大于结束日期
        if start_dt > end_dt:
            raise ValueError("开始日期不能大于结束日期")
        
        stock_pd = getStockList()
        logger.info(f"开始下载数据，开始日期：{start_dt}，结束日期：{end_dt}, 股票数量：{len(stock_pd)}")
        # 遍历日期
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y%m%d')
            logger.info(f"开始下载数据，日期：{date_str}")
            savePdStockData(stock_pd, date_str)
            mergeDailyData()
            logger.info(f"下载数据完成，日期：{date_str}")
            time.sleep(2)
            current_dt += timedelta(days=1)
        
        return date_str
    except ValueError as e:
        print(f"日期格式错误: {e}")
        return []
    except Exception as e:
        print(f"遍历日期时发生错误: {e}")
        return []

# 示例使用
# dates = traverse_dates('20240101', '20240131')
# for date in dates:
#     print(date)

