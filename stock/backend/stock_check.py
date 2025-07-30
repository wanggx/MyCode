from flask import Blueprint, request, jsonify
from .dbutil import get_db_connection
from datetime import datetime, timedelta
import re
from backend.data.daily import download_daily_data
import threading
bp = Blueprint('stock_check', __name__)

@bp.route('/api/stock/check', methods=['GET'])
def stock_check():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    sql = "SELECT trade_date, COUNT(1) as cnt FROM stock_daily WHERE 1=1"
    params = []
    if start_date:
        sql += " AND trade_date >= %s"
        params.append(start_date)
    if end_date:
        sql += " AND trade_date <= %s"
        params.append(end_date)
    sql += " GROUP BY trade_date ORDER BY trade_date DESC"
    count_sql = f"SELECT COUNT(*) FROM ({sql}) t"
    sql += " LIMIT %s OFFSET %s"
    params.extend([page_size, offset])
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(count_sql, params[:-2])
            total_row = cursor.fetchone()
            if isinstance(total_row, dict):
                total = list(total_row.values())[0] if total_row else 0
            elif isinstance(total_row, (list, tuple)):
                total = total_row[0] if total_row else 0
            else:
                total = 0
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            result = []
            for r in rows:
                if isinstance(r, dict):
                    result.append({'trade_date': r.get('trade_date', ''), 'cnt': r.get('cnt', 0)})
                elif isinstance(r, (list, tuple)):
                    result.append({'trade_date': r[0], 'cnt': r[1]})
            
        return jsonify({'code': 0, 'data': {'list': result, 'total': total}})
    except Exception as e:
        return jsonify({'code': 1, 'message': str(e)})
    finally:
        conn.close()

@bp.route('/api/stock/daily/add', methods=['POST'])
def stock_daily_add():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    data_type = data.get('type', 'd')  # 默认为日数据
    date_pattern = re.compile(r'^\d{8}$')
    if not start_date or not end_date:
        return jsonify({'success': False, 'message': 'start_date和end_date必填'})
    if not date_pattern.match(start_date) or not date_pattern.match(end_date):
        return jsonify({'success': False, 'message': '日期格式应为yyyyMMdd'})
    try:
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        if start_dt > end_dt:
            return jsonify({'success': False, 'message': '开始日期不能大于结束日期'})
        if ((end_dt - start_dt).days > 30) & (data_type == 'd'):
            return jsonify({'success': False, 'message': '补录区间不能超过一个月'})
    except Exception as e:
        return jsonify({'success': False, 'message': '日期格式错误'})

    # 异步调用下载数据
    def async_download():
        if data_type == 'd':
            from backend.data.daily import download_daily_data
            download_daily_data(start_date, end_date)
        elif data_type == 'w':
            from backend.data.wm import iterate_weeks
            iterate_weeks(start_date, end_date)
        elif data_type == 'm':
            from backend.data.wm import iterate_months
            iterate_months(start_date, end_date)
    threading.Thread(target=async_download, daemon=True).start()

    return jsonify({'success': True, 'message': '补录任务已提交，正在后台处理'})

def create_stock_check_routes(app):
    app.register_blueprint(bp) 