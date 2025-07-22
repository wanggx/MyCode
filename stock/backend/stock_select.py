#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股列表查询接口
"""

from flask import request, jsonify
from backend.user import require_auth
from backend.dbutil import get_db_connection
import datetime


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
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            result, error = get_stock_select_from_db(page, page_size, select_date)
            # 新增逻辑：如果查到数据为0，且有select_date，异步触发选股
            if result and result.get('total', 0) == 0 and select_date:
                import threading
                from backend.data.select_daily import selectVolMagnify
                from backend.data.select_daily import selectLowTrendLowShadow
                # 格式化select_date为yyyyMMdd
                try:
                    date_obj = datetime.datetime.strptime(select_date, '%Y-%m-%d')
                    select_date_str = date_obj.strftime('%Y%m%d')
                except Exception:
                    select_date_str = select_date  # 如果已是yyyyMMdd则直接用

                def async_select(date_str, n):
                    selectVolMagnify(date_str, n)
                    selectLowTrendLowShadow(date_str, n)
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