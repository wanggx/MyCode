import akshare as ak
from hk.hkutil import saveHKStockList
from hk.hk_daily import saveHKStockDaily, saveSingleHkData, saveHkStockData
from hk.hkutil import mergeHKDailyData
from hk.hkutil import getHkStockList
from utils.logger import setup_logger

logger = setup_logger()

# saveHKStockList()
# hk_spot = ak.stock_hk_spot_em()
# print(hk_spot.columns)
# print(len(hk_spot))
# print(hk_spot.head())

# saveHKStockDaily("")
# mergeHKDailyData()

# stock_hk_daily_hfq_df = ak.stock_hk_daily(symbol="00700", adjust="")
# print(stock_hk_daily_hfq_df.columns)

# stock_hk_hist_df = ak.stock_hk_hist(symbol="00593", period="daily", start_date="20260224", end_date="20260225", adjust="")
# print(stock_hk_hist_df)
# print(stock_hk_hist_df.columns)
#
# stock_hk_daily_hfq_df = ak.stock_hk_daily(symbol="00700", adjust="hfq")
# print(stock_hk_daily_hfq_df.columns)
# print(stock_hk_daily_hfq_df.head(10))

# saveSingleHkData("00700")

#saveSingleHkData("00089")

hk_stock = getHkStockList()
saveHkStockData(hk_stock)

