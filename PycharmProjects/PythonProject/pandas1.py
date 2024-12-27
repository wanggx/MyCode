import numpy as np
from pandas import Series
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline

# 准备数据
# data = [
#     [2320.26, 2320.26, 2287.3, 2362.94],
#     [2300, 2291.3, 2288.26, 2308.38],
#     [2295.35, 2346.5, 2295.35, 2345.92],
#     [2347.22, 2358.98, 2337.35, 2363.8],
#     # ... more data
# ]
#
# # 配置 Kline 图
# kline = (
#     Kline()
#     .add_xaxis(xaxis_data=["2017-10-24", "2017-10-25", "2017-10-26", "2017-10-27"])
#     .add_yaxis(series_name="Kline", y_axis=data)
#     .set_global_opts(
#         xaxis_opts=opts.AxisOpts(is_scale=True),
#         yaxis_opts=opts.AxisOpts(is_scale=True),
#         title_opts=opts.TitleOpts(title="Kline 示例"),
#     )
# )
#
# # 渲染图表
# kline.render("kline_chart.html")

# s1 = Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], index= [i + 10 for i in range(10)])
# s2 = Series([i + 10 for i in range(10)], index= [i + 10 for i in range(10)])
#
# # print(s)
#
# df = pd.DataFrame({'s1': s1, 's2':s2}, index= [i + 10 for i in range(10)])
#
# print(df['s1'])

# print(len(df))
# print(df.size)
# print(df.drop(10))
# print(df.drop('s1', axis=1))
#
# print(df.mean())
# print(df.mean(axis=1))
#
# print(df['s2'].value_counts())

import pandas as pd


# pd5 = pd.read_csv("5.csv", header=0)
# pd10 = pd.read_csv("10.csv", header=0)
#
#
# pd5.rename(columns={'close':'slope5'}, inplace=True)
# pd10.rename(columns={'close':'slope10'}, inplace=True)
#
# print(pd5.columns)
# print(pd10.columns)
# ret = pd5.join(pd10, how='inner', lsuffix='_left', rsuffix='_right')
#
# print(ret)


# left = pd.DataFrame( {"A": [1, 2, 2], "B": ["B0", "B1", "B2"]}, index=["K0", "K1", "K2"])
#
#
# right = pd.DataFrame({"C": ["C0", "C2", "C3"], "D": ["D0", "D2", "D3"]}, index=["K0", "K2", "K3"])
#
#
# result = left.join(right, how="outer")
#
# print(result)


left = pd.DataFrame({
    "A": ["A0", "A1", "A2", "A3"],
    "B": ["B0", "B1", "B2", "B3"],
    "key": ["K0", "K1", "K0", "K1"],})


right = pd.DataFrame({"C": ["C0", "C1"], "D": ["D0", "D1"]}, index=["K0", "K1"])

result = left.join(right, on="key")

print(result)

