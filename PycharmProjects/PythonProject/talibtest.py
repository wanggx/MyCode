import talib
import pandas as pd
#查所有函数指标，一共158个
functions = talib.get_functions()
print(len(functions),functions)
#指标太多看不过来，没关系，还可以使用分类查看
groups = talib.get_function_groups()
print(groups)
#单独查看分类名称
print(groups.keys())
#查看每个分类的函数指标个数
table = pd.DataFrame({
'技术指标类别名称': list(groups.keys()),
'该类别指标个数': list(map(lambda x: len(x), groups.values()))
})
print(table)

# 从字典创建 DataFrame
# data = {
#     'name': ['Alice', 'Bob', 'Charlie'],
#     'age': [25, 30, 35],
#     'city': ['New York', 'London', 'Tokyo']
# }
# df = pd.DataFrame(data)
# df.reset_index()
# print(df.filter(items=[1,2], axis=0))


# import pandas as pd
# import numpy as np
#
# df = pd.DataFrame(np.random.randint(0,2,20), columns=['行为']).reset_index()
# df['转换标记'] = df['行为']!=df['行为'].shift()  # 识别信号，判断行为是否发生了改变
# df['行为分组'] = df['转换标记'].cumsum()  # 辅助列，根据识别信号，对相邻的相同行为进行分组，便于计算每组相同行为的连续发生次数
# df['连续行为次数'] = df.groupby(['行为分组'])['index'].rank(method='dense')  # 根据行为分组，使用窗口函数对每条行为标记连续发生次数
# print(df)



# # 创建数据
# data = {
#     'date': pd.date_range(start='2021-01-01', periods=10, freq='D'),
#     'value': [10, 15, 20, 20, 25, 30, 30, 35, 40, 45]
# }
# df = pd.DataFrame(data)
# df.set_index('date', inplace=True)
#
# # 分析连续增长的天数
# df['is_increasing'] = df['value'] > df['value'].shift(1)
# df['consecutive_days'] = df['is_increasing'].cumsum() * df['is_increasing']
# print(df)
# # 筛选出连续增长超过3天的记录并重置索引
# consecutive_days_filter = df.groupby('consecutive_days')['value'].filter(lambda x: len(x) > 2).reset_index(drop=True)
# print(consecutive_days_filter)
#
# import pandas as pd
df = pd.DataFrame({'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-05', '2023-01-06', '2023-01-07']})
df['date'] = pd.to_datetime(df['date'])
df['consecutive_days'] = df['date'].diff().cumsum()
print(df)





