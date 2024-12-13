import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 获取股票数据
symbol = "600519.SS"
start_date = "2023-01-01"
end_date = "2023-12-01"

data = pd.read_csv('stock.csv', header=0, index_col=0)

# 初始化交叉信号列
data['Signal'] = 0

# 计算每日收益率
data['Daily_Return'] = data['Close'].pct_change()

# 计算策略信号
data['Signal'] = 0
data.loc[data['Daily_Return'] > 0, 'Signal'] = 1  # 以涨幅为信号，可根据需要修改条件

# 计算策略收益
data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']

# 计算累计收益
data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod()

# 绘制累计收益曲线
plt.figure(figsize=(10, 6))
plt.plot(data['Cumulative_Return'], label='Strategy Cumulative Return', color='b')
plt.plot(data['Close'] / data['Close'].iloc[0], label='Stock Cumulative Return', color='g')
plt.title("Cumulative Return of Strategy vs. Stock")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.show()