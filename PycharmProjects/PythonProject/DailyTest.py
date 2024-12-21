
import talib as ta
from moduledir.stockutil import *

df = getStockData('600678.SH', '', '')

integer = ta.CDLDOJISTAR(df['open'], df['high'], df['low'], df['close'])

print(df.head())
print(integer.values)