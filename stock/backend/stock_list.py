#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据查询接口
"""

from flask import request, jsonify
from backend.user import require_auth
from backend.dbutil import get_db_connection

def get_stocks_from_db(page=1, page_size=10, keyword='', area='', industry=''):
    """从数据库获取股票列表"""
    try:
        connection = get_db_connection()
        if not connection:
            return None, "数据库连接失败"
        
        cursor = connection.cursor()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if keyword:
            where_conditions.append("(ts_code LIKE %s OR symbol LIKE %s OR name LIKE %s)")
            keyword_param = f"%{keyword}%"
            params.extend([keyword_param, keyword_param, keyword_param])
        
        if area:
            where_conditions.append("area = %s")
            params.append(area)
        
        if industry:
            where_conditions.append("industry = %s")
            params.append(industry)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as total FROM stock {where_clause}"
        cursor.execute(count_sql, params)
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0
        
        # 获取分页数据
        offset = (page - 1) * page_size
        sql = f"""
            SELECT 
                ts_code,
                symbol,
                name,
                area,
                industry,
                cnspell,
                market,
                list_date,
                act_name,
                act_ent_type
            FROM stock 
            {where_clause}
            ORDER BY ts_code
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(sql, params + [page_size, offset])
        stocks = cursor.fetchall()
        
        # 处理数据格式
        formatted_stocks = []
        for stock in stocks:
            formatted_stock = {
                'ts_code': stock['ts_code'],
                'symbol': str(stock['symbol']) if stock['symbol'] else '',
                'name': stock['name'],
                'area': stock['area'],
                'industry': stock['industry'],
                'cnspell': stock['cnspell'],
                'market': stock['market'],
                'list_date': str(stock['list_date']) if stock['list_date'] else '',
                'act_name': stock['act_name'],
                'act_ent_type': stock['act_ent_type']
            }
            formatted_stocks.append(formatted_stock)
        
        cursor.close()
        connection.close()
        
        return {
            'stocks': formatted_stocks,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }, None
        
    except Exception as e:
        print(f"查询股票数据失败: {e}")
        return None, f"查询失败: {str(e)}"

def get_areas_from_db():
    """从数据库获取所有地域"""
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        sql = "SELECT DISTINCT area FROM stock WHERE area IS NOT NULL AND area != '' ORDER BY area"
        cursor.execute(sql)
        areas = [row['area'] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return areas
    except Exception as e:
        print(f"获取地域列表失败: {e}")
        return []

def get_industries_from_db():
    """从数据库获取所有行业"""
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        sql = "SELECT DISTINCT industry FROM stock WHERE industry IS NOT NULL AND industry != '' ORDER BY industry"
        cursor.execute(sql)
        industries = [row['industry'] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return industries
    except Exception as e:
        print(f"获取行业列表失败: {e}")
        return []

def create_stock_routes(app):
    """创建股票相关的路由"""
    
    @app.route('/api/stocks', methods=['GET'])
    @require_auth
    def get_stocks():
        """获取股票列表 - 从数据库查询"""
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            keyword = request.args.get('keyword', '')
            area = request.args.get('area', '')
            industry = request.args.get('industry', '')
            
            # 参数验证
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # 从数据库获取数据
            result, error = get_stocks_from_db(page, page_size, keyword, area, industry)
            
            if error:
                return jsonify({'error': error}), 500
            
            return jsonify({
                'message': '获取成功',
                'data': result
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'获取股票列表失败: {str(e)}'}), 500
    
    @app.route('/api/stocks/areas', methods=['GET'])
    @require_auth
    def get_areas():
        """获取所有地域"""
        try:
            areas = get_areas_from_db()
            return jsonify({
                'message': '获取成功',
                'data': areas
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取地域列表失败: {str(e)}'}), 500
    
    @app.route('/api/stocks/industries', methods=['GET'])
    @require_auth
    def get_industries():
        """获取所有行业"""
        try:
            industries = get_industries_from_db()
            return jsonify({
                'message': '获取成功',
                'data': industries
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取行业列表失败: {str(e)}'}), 500

    def sync_stocks():
        """
        同步股票数据（mock 实现）
        """
        try:
            from moduledir.stockutil import refreshStockList
            refreshStockList()
            # TODO: 这里可以添加实际的同步逻辑，例如调用 Tushare API 并更新数据库
            return {"success": True, "message": "同步成功"}, 200
        except Exception as e:
            return {"success": False, "message": f"同步失败: {str(e)}"}, 500


    @app.route('/api/stocks/sync', methods=['POST'])
    @require_auth
    def sync_stocks_route():
        """同步股票数据接口"""
        result, status_code = sync_stocks()
        return jsonify(result), status_code

    @app.route('/api/stock/data', methods=['GET'])
    @require_auth
    def get_stock_daily_data():
        """获取指定ts_code近60天的日线数据，支持分页"""
        try:
            ts_code = request.args.get('ts_code')
            start_date = request.args.get('startDate')
            end_date = request.args.get('endDate')
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            if not ts_code or not start_date or not end_date:
                return jsonify({'error': '参数缺失(ts_code, startDate, endDate)'}), 400
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            connection = get_db_connection()
            if not connection:
                return jsonify({'error': '数据库连接失败'}), 500
            cursor = connection.cursor()
            # 获取总数
            count_sql = """
                SELECT COUNT(*) as total FROM stock_daily
                WHERE ts_code = %s AND trade_date BETWEEN %s AND %s
            """
            cursor.execute(count_sql, (ts_code, start_date, end_date))
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0
            # 获取分页数据
            offset = (page - 1) * page_size
            sql = """
                SELECT ts_code, trade_date, open, high, low, close, pre_close, `change`, pct_chg, vol
                FROM stock_daily
                WHERE ts_code = %s AND trade_date BETWEEN %s AND %s
                ORDER BY trade_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (ts_code, start_date, end_date, page_size, offset))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify({
                'message': '获取成功',
                'data': {
                    'items': rows,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取日线数据失败: {str(e)}'}), 500
