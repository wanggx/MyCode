import akshare as ak
from hk.hkutil import saveHKStockList
from hk.hk_daily import saveHKStockDaily
from hk.hkutil import mergeHKDailyData

#hk_spot = ak.stock_hk_spot()
# hk_spot = ak.stock_hk_spot_em()
# print(hk_spot.columns)
# print(len(hk_spot))
# print(hk_spot.head())

saveHKStockDaily("")
mergeHKDailyData()

# stock_hk_hist_df = ak.stock_hk_hist(symbol="00593", period="daily", start_date="20260224", end_date="20260225", adjust="")
# print(stock_hk_hist_df)
#
# stock_hk_daily_hfq_df = ak.stock_hk_daily(symbol="00700", adjust="hfq")
# print(stock_hk_daily_hfq_df)

