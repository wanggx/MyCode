import sys
import os
import time
from datetime import datetime

import numpy as np
from numpy.ma.core import reshape

from moduledir.mod import module_test
from moduledir.Person import Person
import threading

import pyecharts

# print("hello world")
# print("hello world")
# print("hello world")
#
# def greet(name):
#     print("hello world")
#     print("hello world" + name)
#
# if 3 < 5:
#     print("hello world if")
# elif 5 < 3:
#     print("hello world elif ")
# else:
#     print("hello world else")
#
# greet("test")

# module_test("test")
#
# print(sys.path)
#
#
#
# print(os.environ.get('PYTHONPATH'))
#
# try:
#     1 / 0
# except ZeroDivisionError:
#     print("error 0")
# else:
#     print("error 1")
# finally:
#     print("error 2")

# for i in range(10):
#     p = Person('wgx', 33)
#
#     p.display()
#     print(hasattr(p, 'name'))
#
#     del p



# try:
#     thread = threading.Thread(target=module_test, args=("111",))
#     thread.start()
#     thread.join()
# finally:
#     print ("finall")


# from pyecharts.charts import Bar
#
# # 准备数据
# x_data = ['一月', '二月', '三月', '四月', '五月']
# y_data = [10, 20, 15, 25, 30]
#
# # 创建柱状图
# bar_chart = Bar()
# bar_chart.add_xaxis(x_data)
# bar_chart.add_yaxis("销售额", y_data)
#
# # 也可以传入路径参数，如 bar_chart.render("bar_chart.html")
# bar_chart.render()

# a = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
# for i in a:
#     print(i)
#
# d = {'key1':'value1','key2':'value2'}
# for i in d:
#     print(d[i], i)
#
# print (len(d))


import pandas as pd
import matplotlib.pyplot as plt

# s = pd.Series([1,2,3,4,5])

s = pd.date_range("20200101", periods=5)

r = np.random.randn(5, 4)

df1 = pd.DataFrame(np.random.randn(5, 4), index=s, columns=list('ABCD'))

df1['NAME'] = 'A'

df2 = pd.DataFrame(np.random.randn(5, 4), index=s, columns=list('ABCD'))

df2['NAME'] = 'B'

T = pd.concat([df2, df1])

# T['W'] =
# T['M'] = T.index.weekday
# T['Y'] = T.index.year
#
# datetime.now().
#
# print(year, month_number, week_number)

# def week_high(x):
#     return x.max()
#
# def week_low(x):
#     return x.min()
#
# ret = T.groupby(['NAME', 'Y', 'M']).agg({'B': week_high, 'C': week_low})
#
# print(T)
# print(ret)
#
# print(T.index)
#
# T.set_index('A', inplace=True)
# T.sort_index(inplace=True)
#
# print(T)
#
# print(T.index)

# def line(e):
#     length = len(e)
#     print(length)
#     print(e)
#     x = np.arange(length)
#     slope, _ = np.polyfit(x, e.values, 1)
#     return slope
#
# print(T.groupby('NAME')['C'].agg(line))
#
# print(T.groupby('NAME').head(3)['C'].rolling(2).apply(lambda x: np.sum(x)))



# def line(e):
#     length = len(e)
#     # print(length)
#     # print(e)
#     x = np.arange(length)
#     slope, _ = np.polyfit(x, e.values, 1)
#     return slope
#
# T['E'] = T.groupby('NAME').shift(1)['A']
#
# print(T.groupby('NAME').tail(1))

# print(T)

# print(T.groupby('NAME').agg(col1=('A', line), col2=('A', line)))

# print(T.groupby('NAME').agg({'A': line, 'B': [line, 'max']}))

# def str_test(x):
#     print(x)
#     print(str(x.values))
#     ab = str(x['A']) + "|" + str(x['B'])
#     print(ab)
#     return ab
#
# def axis_test(x):
#     # print(x)
#     # print(str(x.values))
#     ab = np.sum(x.values)
#     return ab
#
# print(T[['A','B']].apply(axis_test, axis=1))

# print(df['20200101':'20200102':'20200103'])

# print(df.iloc[:, 1:3])
#
# print(df[df['A'] > 1])

# s1 = pd.Series([1,2,3,4,5,6], pd.date_range("20200101", periods=6))

#print(df)
# df.to_parquet("test.parquet")
# print(df.shift(2))
# print(df.describe())

# def aggtest(a):
#     return np.mean(a) * 2

# print(df.agg(lambda x: np.mean(x) * 2))
#
# print(df.transform(lambda x: abs(x) * 10))
# print(df)
# print(df.groupby(['A','B']).agg(aggtest))
# # df = df.cumsum()
# print(df.head())
# print(df.groupby(['A','B']).sum())
# print(df.cumsum())

# plt.figure(figsize = (10,10))
# df['E'] = df['D'] * 2
# df.plot()
# # plt.legend(loc='best')
# plt.show()


# print(df['E'].values.mean())

# print(pd.concat([df, df]))
# print(pd.merge(df, df, how='left', on='E').values)

# print(df.pivot(columns='E', index='D', values='E'))

# print(df)

# pdf = df.shift(1)['C']
#
# df['P'] = pdf
#
# df['Signal'] = 0
# df.loc[(df['C'] > df['P']) | (df['C'] > df['D']), 'Signal'] = 1
# # print(df.loc[df['Signal'] > 0]['Signal'])
# df['MA2'] = df['D'].rolling(2).mean()
#
# print(df)

# print(df)
#
# rolling_trend = df['A'].rolling(2)
#
# def printroll(x):
#     print(x)
#     return 1
#
# rolling_trend.apply(printroll)

# pdf = df.shift(1)['C']
#
# df['P'] = pdf
#
# df['Signal'] = 0
# df.loc[(df['C'] > df['P']) | (df['C'] > df['D']), 'Signal'] = 1











