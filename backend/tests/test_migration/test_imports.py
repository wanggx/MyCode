# -*- coding: utf-8 -*-
"""
验证所有模块可正确导入
"""


def test_core_imports():
    from app.core.config import Settings, settings, load_settings
    from app.core.database import get_engine, get_db_connection, execute_query, execute_count_query, test_connection
    from app.core.security import hash_password, generate_token, verify_token, require_auth
    from app.core.response import success, error
    from app.core.logger import setup_logger


def test_utils_imports():
    from app.utils.dateutil import saturday, friday, get_month_range, calculate_date
    from app.utils.notify import sendMsg, sendGroupFile


def test_repositories_imports():
    from app.repositories.base import paginate_sql
    from app.repositories.user_repo import find_user_by_username, create_user, get_user_by_id
    from app.repositories.stock_repo import query_stocks, query_areas, query_industries
    from app.repositories.stock_daily_repo import query_daily_data, query_stock_data_df
    from app.repositories.stock_select_repo import query_stock_select, save_select_result_to_db
    from app.repositories.tushare_repo import get_pro_api, fetch_daily_data
    from app.repositories.hk_stock_repo import save_hk_stock_list, get_hk_stock_list, get_hk_stock_data


def test_analysis_imports():
    from app.analysis.indicators import calc_macd_and_kdj, process_macd_and_kdj
    from app.analysis.ma_analysis import ma, process_ma, select_ma_by_daily
    from app.analysis.volume_analysis import polyline, volmagnify, polylineslope
    from app.analysis.aggregation import process_week_df, process_month_df


def test_services_imports():
    from app.services.auth_service import register, login, get_info, change_password
    from app.services.stock_service import get_stock_list, get_areas, get_industries, get_stock_daily, sync_stocks
    from app.services.select_service import get_select_results, trigger_async_select, mock_select
    from app.services.data_service import download_daily_data, iterate_weeks, iterate_months
    from app.services.notify_service import send_text, send_file


def test_api_imports():
    from app.api.auth import auth_bp
    from app.api.stocks import stocks_bp
    from app.api.stock_select import select_bp
    from app.api.stock_check import check_bp
    from app.api.vol_line import vol_line_bp


def test_app_factory():
    from app import create_app
    app = create_app()
    assert app is not None


def test_tasks_imports():
    from tasks.scheduler import start_scheduler, job


def test_hk_imports():
    from hk.hkutil import getHkStockList, getHkStockData, saveHKStockList
    from hk.hk_daily import saveHKStockDaily
