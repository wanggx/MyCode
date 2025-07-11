import random
import datetime
from flask import request, jsonify
from backend.user import require_auth

# Mock股票数据
MOCK_STOCKS = [
    {
        'code': '000001',
        'name': '平安银行',
        'price': 12.34,
        'change': 0.45,
        'change_percent': 3.78,
        'volume': 12345678,
        'market_cap': 268.5,
        'pe_ratio': 8.5,
        'sector': '银行'
    },
    {
        'code': '000002',
        'name': '万科A',
        'price': 18.67,
        'change': -0.23,
        'change_percent': -1.22,
        'volume': 9876543,
        'market_cap': 215.8,
        'pe_ratio': 12.3,
        'sector': '房地产'
    },
    {
        'code': '000858',
        'name': '五粮液',
        'price': 156.78,
        'change': 2.34,
        'change_percent': 1.52,
        'volume': 3456789,
        'market_cap': 608.9,
        'pe_ratio': 25.6,
        'sector': '白酒'
    },
    {
        'code': '002415',
        'name': '海康威视',
        'price': 32.45,
        'change': -1.23,
        'change_percent': -3.65,
        'volume': 5678901,
        'market_cap': 304.2,
        'pe_ratio': 18.7,
        'sector': '科技'
    },
    {
        'code': '600036',
        'name': '招商银行',
        'price': 45.67,
        'change': 0.89,
        'change_percent': 1.99,
        'volume': 2345678,
        'market_cap': 1150.3,
        'pe_ratio': 9.2,
        'sector': '银行'
    },
    {
        'code': '600519',
        'name': '贵州茅台',
        'price': 1789.00,
        'change': 15.67,
        'change_percent': 0.88,
        'volume': 123456,
        'market_cap': 2248.5,
        'pe_ratio': 32.1,
        'sector': '白酒'
    },
    {
        'code': '000725',
        'name': '京东方A',
        'price': 4.56,
        'change': 0.12,
        'change_percent': 2.70,
        'volume': 45678901,
        'market_cap': 156.7,
        'pe_ratio': 15.8,
        'sector': '科技'
    },
    {
        'code': '002594',
        'name': '比亚迪',
        'price': 234.56,
        'change': -5.67,
        'change_percent': -2.36,
        'volume': 3456789,
        'market_cap': 683.2,
        'pe_ratio': 45.6,
        'sector': '汽车'
    },
    {
        'code': '300059',
        'name': '东方财富',
        'price': 23.45,
        'change': 0.78,
        'change_percent': 3.44,
        'volume': 6789012,
        'market_cap': 247.8,
        'pe_ratio': 28.9,
        'sector': '金融'
    },
    {
        'code': '600276',
        'name': '恒瑞医药',
        'price': 67.89,
        'change': -2.34,
        'change_percent': -3.33,
        'volume': 2345678,
        'market_cap': 425.6,
        'pe_ratio': 35.2,
        'sector': '医药'
    }
]

def generate_mock_data():
    """生成动态mock数据"""
    stocks = []
    for stock in MOCK_STOCKS:
        # 随机生成价格变化
        price_change = random.uniform(-5, 5)
        new_price = max(0.01, stock['price'] + price_change)
        change_percent = (price_change / stock['price']) * 100
        
        # 随机生成成交量
        volume_change = random.uniform(0.5, 2.0)
        new_volume = int(stock['volume'] * volume_change)
        
        stock_copy = stock.copy()
        stock_copy.update({
            'price': round(new_price, 2),
            'change': round(price_change, 2),
            'change_percent': round(change_percent, 2),
            'volume': new_volume,
            'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        stocks.append(stock_copy)
    
    return stocks

def get_stock_by_code(code):
    """根据股票代码获取股票信息"""
    for stock in MOCK_STOCKS:
        if stock['code'] == code:
            return stock
    return None

def search_stocks(keyword):
    """搜索股票"""
    keyword = keyword.lower()
    results = []
    
    for stock in MOCK_STOCKS:
        if (keyword in stock['code'].lower() or 
            keyword in stock['name'].lower() or 
            keyword in stock['sector'].lower()):
            results.append(stock)
    
    return results

def filter_stocks_by_sector(sector):
    """按行业筛选股票"""
    if not sector:
        return MOCK_STOCKS
    
    return [stock for stock in MOCK_STOCKS if stock['sector'] == sector]

def get_sectors():
    """获取所有行业"""
    sectors = list(set(stock['sector'] for stock in MOCK_STOCKS))
    return sorted(sectors)

# Flask路由函数
def create_stock_routes(app):
    """创建股票相关的路由"""
    
    @app.route('/api/stocks', methods=['GET'])
    @require_auth
    def get_stocks():
        """获取股票列表"""
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            keyword = request.args.get('keyword', '')
            sector = request.args.get('sector', '')
            sort_by = request.args.get('sort_by', 'code')
            sort_order = request.args.get('sort_order', 'asc')
            
            # 获取股票数据
            stocks = generate_mock_data()
            
            # 搜索过滤
            if keyword:
                stocks = search_stocks(keyword)
            
            # 行业过滤
            if sector:
                stocks = filter_stocks_by_sector(sector)
            
            # 排序
            reverse = sort_order.lower() == 'desc'
            if sort_by == 'price':
                stocks.sort(key=lambda x: x['price'], reverse=reverse)
            elif sort_by == 'change_percent':
                stocks.sort(key=lambda x: x['change_percent'], reverse=reverse)
            elif sort_by == 'volume':
                stocks.sort(key=lambda x: x['volume'], reverse=reverse)
            elif sort_by == 'market_cap':
                stocks.sort(key=lambda x: x['market_cap'], reverse=reverse)
            else:
                stocks.sort(key=lambda x: x['code'], reverse=reverse)
            
            # 分页
            total = len(stocks)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_stocks = stocks[start:end]
            
            return jsonify({
                'message': '获取成功',
                'data': {
                    'stocks': paginated_stocks,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total': total,
                        'total_pages': (total + page_size - 1) // page_size
                    }
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'获取股票列表失败: {str(e)}'}), 500
    
    @app.route('/api/stocks/<code>', methods=['GET'])
    @require_auth
    def get_stock_detail(code):
        """获取股票详情"""
        try:
            stock = get_stock_by_code(code)
            if not stock:
                return jsonify({'error': '股票不存在'}), 404
            
            # 生成动态数据
            stock_data = generate_mock_data()
            stock_detail = next((s for s in stock_data if s['code'] == code), None)
            
            if stock_detail:
                return jsonify({
                    'message': '获取成功',
                    'data': stock_detail
                }), 200
            else:
                return jsonify({'error': '获取股票详情失败'}), 500
                
        except Exception as e:
            return jsonify({'error': f'获取股票详情失败: {str(e)}'}), 500
    
    @app.route('/api/stocks/sectors', methods=['GET'])
    @require_auth
    def get_sectors_route():
        """获取所有行业"""
        try:
            sectors = get_sectors()
            return jsonify({
                'message': '获取成功',
                'data': sectors
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取行业列表失败: {str(e)}'}), 500
    
    @app.route('/api/stocks/search', methods=['GET'])
    @require_auth
    def search_stocks_route():
        """搜索股票"""
        try:
            keyword = request.args.get('keyword', '')
            if not keyword:
                return jsonify({'error': '搜索关键词不能为空'}), 400
            
            results = search_stocks(keyword)
            return jsonify({
                'message': '搜索成功',
                'data': results
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'搜索失败: {str(e)}'}), 500
    
    @app.route('/api/stocks/market-overview', methods=['GET'])
    @require_auth
    def get_market_overview():
        """获取市场概览"""
        try:
            stocks = generate_mock_data()
            
            # 计算市场统计
            total_stocks = len(stocks)
            up_stocks = len([s for s in stocks if s['change_percent'] > 0])
            down_stocks = len([s for s in stocks if s['change_percent'] < 0])
            flat_stocks = total_stocks - up_stocks - down_stocks
            
            total_market_cap = sum(s['market_cap'] for s in stocks)
            avg_pe_ratio = sum(s['pe_ratio'] for s in stocks) / total_stocks
            
            # 计算行业分布
            sector_distribution = {}
            for stock in stocks:
                sector = stock['sector']
                if sector not in sector_distribution:
                    sector_distribution[sector] = 0
                sector_distribution[sector] += 1
            
            return jsonify({
                'message': '获取成功',
                'data': {
                    'total_stocks': total_stocks,
                    'up_stocks': up_stocks,
                    'down_stocks': down_stocks,
                    'flat_stocks': flat_stocks,
                    'total_market_cap': round(total_market_cap, 2),
                    'avg_pe_ratio': round(avg_pe_ratio, 2),
                    'sector_distribution': sector_distribution,
                    'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'获取市场概览失败: {str(e)}'}), 500
    


if __name__ == '__main__':
    print("股票数据服务模块")
    print(f"可用股票数量: {len(MOCK_STOCKS)}")
    print(f"可用行业: {get_sectors()}") 