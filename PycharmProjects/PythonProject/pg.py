import pandas as pd
import numpy as np

s = pd.date_range("20200101", periods=5)

r = np.random.randn(5, 4)

df1 = pd.DataFrame(np.random.randn(5, 4), index=s, columns=list('ABCD'))

df1['NAME'] = 'A'

df2 = pd.DataFrame(np.random.randn(5, 4), index=s, columns=list('ABCD'))

df2['NAME'] = 'B'

df = pd.concat([df2, df1])

dfg = df.groupby('NAME')

print(df)

def apply_open_close(df):
    df.sort_values(by='A', ascending=True, inplace=True)
    df['E'] = df['A'].shift(1)
    df['F'] = 0
    df.loc[df['E'] > df['C'], 'F'] = 1

    def calculate_slope(window):
        x = np.arange(len(window))
        y = window.values
        slope, _ = np.polyfit(x, y, 1)
        return slope

    slope = df['D'].agg({'slope1': calculate_slope, 'slope2': calculate_slope, 'slope3': calculate_slope})
    # print(slope)
    df['slope1'] = slope['slope1']
    df['slope2'] = slope['slope2']
    df['slope3'] = slope['slope3']
    # print(df)
    return df.tail(1)

print(dfg.tail(3).groupby('NAME').apply(apply_open_close, include_groups=False))

def transfrom_open(x):
    return x.iloc[len(x)-1]

print(dfg.transform(transfrom_open))

print(dfg.agg(transfrom_open))



