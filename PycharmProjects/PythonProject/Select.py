import pandas as pd
import numpy as np
from scipy import stats

# # 创建包含趋势数据的Series对象
# data = pd.Series([1, 2, 4, 8, 5, 6, 7, 8, 9, 10])
#
# # 计算滚动窗口内的趋势线
# window_size = 3
# rolling_trend = data.rolling(window_size)
#
# # 定义计算斜率的函数
# def calculate_slope(window):
#     x = np.arange(window_size)
#     y = window.values
#     slope, _ = np.polyfit(x, y, 1)
#     return slope
#
# # 计算每个滚动窗口的斜率
# slopes = rolling_trend.apply(calculate_slope)
#
# # 打印计算得到的斜率
# print(slopes)

x = np.arange(20)
y = [110, 100.98, 99.08,11.01,11.2,11.15,11.21,11.18, 11.22,11.05, 9.23, 8.20, 11.25, 11.24, 11.26,11.20, 9.25, 7.27,11.30, 8.15]
slope = np.polyfit(x, y, 1, full=True)


print(slope)

#
# slope, _, _, _, _= stats.linregress(x, y)
#
# print(slope)

# p = np.poly1d([1,2,3])
#
# print(p(3))