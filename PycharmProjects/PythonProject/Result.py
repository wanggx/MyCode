
import pandas as pd


pd5 = pd.read_csv("5.csv")
pd10 = pd.read_csv("10.csv")
pd20 = pd.read_csv("20.csv")
pd30 = pd.read_csv("30.csv")
pd54 = pd.read_csv("54.csv")

# print(pd5.head(1))
# print(pd10.head(1))
# print(pd20.head(1))
# print(pd30.head(1))
# print(pd54.head(1))

pd5.rename(columns={'close':'slope5'}, inplace=True)
pd10.rename(columns={'close':'slope10'}, inplace=True)
pd20.rename(columns={'close':'slope20'}, inplace=True)
pd30.rename(columns={'close':'slope30'}, inplace=True)
pd54.rename(columns={'close':'slope54'}, inplace=True)

ret = (pd5
       .merge(pd10, how = 'inner', on = 'ts_code')
       .merge(pd20, how = 'inner', on = 'ts_code')
       .merge(pd30, how = 'inner', on = 'ts_code')
       .merge(pd54, how = 'inner', on = 'ts_code'))


ret[(ret['slope5'] < 0) &
          (ret['slope10'] < 0) &
          (ret['slope20'] > 0) &
          (ret['slope30'] > 0) &
          (ret['slope54'] > 0)].to_csv('c.csv')