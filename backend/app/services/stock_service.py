# -*- coding: utf-8 -*-
"""
股票数据服务：查询、同步
"""
from app.repositories.stock_repo import query_stocks, query_areas, query_industries, query_stock_list_df
from app.repositories.stock_daily_repo import query_daily_data


def get_stock_list(page=1, page_size=10, keyword="", area="", industry=""):
    if page < 1: page = 1
    if page_size < 1 or page_size > 100: page_size = 10
    return query_stocks(page, page_size, keyword, area, industry)


def get_areas():
    return query_areas()


def get_industries():
    return query_industries()


def get_stock_daily(ts_code, start_date, end_date, page=1, page_size=10, data_type="d"):
    if not ts_code or not start_date or not end_date:
        return None, "参数缺失(ts_code, startDate, endDate)"
    if page < 1: page = 1
    if page_size < 1 or page_size > 100: page_size = 10
    return query_daily_data(ts_code, start_date, end_date, page, page_size, data_type)


def sync_stocks():
    """从 Tushare 同步股票列表到 stock_basic"""
    try:
        from app.core.config import settings
        import tushare as ts
        ts.set_token(settings.TUSHARE_TOKEN)
        pro = ts.pro_api()
        data = pro.stock_basic(exchange="", list_status="L")
        from app.core.database import get_engine
        engine = get_engine()
        data.to_sql("stock_basic", con=engine, if_exists="replace", index=False)
        return {"success": True, "message": f"同步成功，共 {len(data)} 只股票"}
    except Exception as e:
        return {"success": False, "message": f"同步失败: {str(e)}"}
