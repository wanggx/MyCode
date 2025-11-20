#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股列表查询接口
"""
import threading
from flask import request, jsonify
from backend.user import require_auth
from backend.dbutil import get_db_connection
import datetime

# 添加一个全局变量来跟踪正在执行的选股任务
_running_select_tasks = set()
_running_tasks_lock = threading.Lock()


def remove_selectedstock_from_db(select_date):
    """
    从数据库中删除指定日期的选股记录
    
    Args:
        select_date (str): 选股日期，格式为 'YYYY-MM-DD'
    
    Returns:
        tuple: (success_count, error_message)
               success_count: 成功删除的记录数，如果出错则为None
               error_message: 错误信息，如果没有错误则为None
    """
    try:
        connection = get_db_connection()
        if not connection:
            return None, "数据库连接失败"
        
        cursor = connection.cursor()
        # 执行删除操作
        sql = "DELETE FROM stock_select WHERE select_date = %s"
        affected_rows = cursor.execute(sql, (select_date,))
        
        # 提交事务
        connection.commit()
        
        # 关闭连接
        cursor.close()
        connection.close()
        
        return affected_rows, None
        
    except Exception as e:
        print(f"删除选股数据失败: {e}")
        return None, f"删除失败: {str(e)}"


def get_stock_select_from_db(page=1, page_size=10, select_date=None):
    """从数据库获取选股列表"""
    try:
        connection = get_db_connection()
        if not connection:
            return None, "数据库连接失败"
        cursor = connection.cursor()
        # 构建查询条件
        where_conditions = []
        params = []
        if select_date:
            where_conditions.append("select_date = %s")
            params.append(select_date)
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        # 获取总数
        count_sql = f"SELECT COUNT(*) as total FROM stock_select {where_clause}"
        cursor.execute(count_sql, params)
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0
        # 获取分页数据
        offset = (page - 1) * page_size
        sql = f"""
            SELECT 
                select_date,
                ts_code,
                name,
                vol,
                trend3,
                trend5,
                trend10,
                trend20,
                trend30
            FROM stock_select
            {where_clause}
            ORDER BY select_date DESC, ts_code
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, params + [page_size, offset])
        rows = cursor.fetchall()
        formatted_rows = []
        for row in rows:
            formatted_rows.append({
                'select_date': str(row['select_date']),
                'ts_code': row['ts_code'],
                'name': row['name'],
                'vol': row['vol'],
                'trend3': row['trend3'],
                'trend5': row['trend5'],
                'trend10': row['trend10'],
                'trend20': row['trend20'],
                'trend30': row['trend30']
            })
        cursor.close()
        connection.close()
        return {
            'items': formatted_rows,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }, None
    except Exception as e:
        print(f"查询选股数据失败: {e}")
        return None, f"查询失败: {str(e)}"

def create_stock_select_routes(app):
    """创建选股相关的路由"""
    @app.route('/api/stock_select', methods=['GET'])
    @require_auth
    def get_stock_select():
        """获取选股列表 - 支持分页和日期筛选"""
        try:
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            select_date = request.args.get('select_date', None)
            # 获取reselect参数，默认为False
            reselect = request.args.get('reselect', 'false').lower() == 'true'

            # 格式化select_date为yyyyMMdd
            try:
                date_obj = datetime.datetime.strptime(select_date, '%Y-%m-%d')
                select_date_str = date_obj.strftime('%Y%m%d')
            except Exception:
                select_date_str = select_date  # 如果已是yyyyMMdd则直接用

            # 唯一性判断，防止重复执行
            task_key = select_date_str
            with _running_tasks_lock:
                if task_key in _running_select_tasks:
                    return jsonify({'error': '选股任务已在执行中，请稍后查询', 'total': 0}), 200

            # 如果reselect为True且select_date存在，则先删除现有数据
            if reselect and select_date:
                remove_selectedstock_from_db(select_date)

            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            # 只有当reselect为False时才查询现有数据
            if not reselect:
                result, error = get_stock_select_from_db(page, page_size, select_date)
            else:
                # 如果是reselect模式，直接设置result为空，触发后续的选股逻辑
                result = {'total': 0}  # 设置total为0触发选股逻辑
                error = None

            # 新增逻辑：如果查到数据为0，且有select_date，异步触发选股
            if result and result.get('total', 0) == 0 and select_date:
                from backend.data.select_daily import selectVolMagnify
                from backend.data.select_daily import selectLowTrendLowShadow
                from backend.data.select import select

                def async_select(date_str, n):
                    try:
                        _running_select_tasks.add(task_key)
                        selectVolMagnify(date_str, n)
                        # selectLowTrendLowShadow(date_str, n)
                        select(date_str)
                    finally:
                        # 任务完成后从运行集合中移除
                        with _running_tasks_lock:
                            _running_select_tasks.discard(task_key)

                threading.Thread(target=async_select, args=(select_date_str, 100), daemon=True).start()
                return jsonify({'error': '当前没有查到数据，正在选股中，请稍后查询', 'total': 0}), 200
            if error:
                return jsonify({'error': error}), 500
            return jsonify({
                'message': '获取成功',
                'data': result
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取选股列表失败: {str(e)}'}), 500 

    @app.route('/api/stock/select/mock', methods=['POST'])
    @require_auth
    def stock_select_mock():
        """Mock选股接口，返回指定ts_code的选股结果（DataFrame转json文本）"""
        try:
            import json
            from backend.data.select_daily import mockSelect
            ts_code = request.json.get('ts_code')
            date_str = request.json.get('date_str')
            n = int(request.json.get('n', 100))
            if not ts_code or not date_str:
                return jsonify({'error': '参数ts_code和date_str必填'}), 400
            df = mockSelect(ts_code, date_str, n)
            if df is None or len(df) == 0:
                return jsonify({'result': '无数据'}), 200
            result_json = df.to_json(orient='records', force_ascii=False)
            return jsonify({'result': result_json}), 200
        except Exception as e:
            return jsonify({'error': f'Mock选股失败: {str(e)}'}), 500

    @app.route('/api/vol_line', methods=['GET'])
    #@require_auth
    def get_vol_line_data():
        """Get volume line data for date range"""
        try:
            start_date = request.args.get('startDate')
            end_date = request.args.get('endDate')

            if not start_date or not end_date:
                return jsonify({'error': 'startDate and endDate parameters are required'}), 400

            connection = get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500

            cursor = connection.cursor()

            # Query to get count of stocks per date within the date range
            sql = """
                SELECT select_date, COUNT(1) as count 
                FROM stock_select 
                WHERE select_date >= %s AND select_date <= %s 
                GROUP BY select_date 
                ORDER BY select_date
            """

            cursor.execute(sql, (start_date, end_date))
            rows = cursor.fetchall()

            # Format the results
            result_data = []
            for row in rows:
                result_data.append({
                    'select_date': str(row['select_date']),
                    'count': row['count']
                })

            cursor.close()
            connection.close()

            return jsonify({
                'message': 'Success',
                'data': result_data
            }), 200

        except Exception as e:
            return jsonify({'error': f'Failed to get volume line data: {str(e)}'}), 500
