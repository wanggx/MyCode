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