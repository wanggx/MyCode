import pymysql
import hashlib
import jwt
import datetime
from flask import Flask, request, jsonify
from functools import wraps
from backend.db_config import DB_CONFIG, JWT_SECRET

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def test_database_connection():
    """测试数据库连接"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result[0] == 1:
                print("数据库连接测试成功!")
                return True
            else:
                print("数据库连接测试失败!")
                return False
        else:
            print("数据库连接失败!")
            return False
            
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False

def hash_password(password):
    """密码加密"""
    return hashlib.md5(password.encode()).hexdigest()

def generate_token(user_id, username, role):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '缺少认证token'}), 401
        
        # 移除Bearer前缀
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': '无效的token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def register_user(username, password, email=None):
    """注册用户"""
    connection = get_db_connection()
    if not connection:
        return False, "数据库连接失败"
    
    try:
        cursor = connection.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "用户名已存在"
        
        # 加密密码
        hashed_password = hash_password(password)
        
        # 插入新用户
        insert_sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (username, hashed_password, email))
        connection.commit()
        
        return True, "注册成功"
        
    except Exception as e:
        return False, f"注册失败: {str(e)}"
    finally:
        connection.close()

def login_user(username, password):
    """用户登录"""
    connection = get_db_connection()
    if not connection:
        return False, "数据库连接失败", None
    
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 验证用户名和密码
        hashed_password = hash_password(password)
        cursor.execute(
            "SELECT id, username, email, role FROM users WHERE username = %s AND password = %s",
            (username, hashed_password)
        )
        
        user = cursor.fetchone()
        if not user:
            return False, "用户名或密码错误", None
        
        # 生成token
        token = generate_token(user['id'], user['username'], user['role'])
        
        return True, "登录成功", {
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }
        
    except Exception as e:
        return False, f"登录失败: {str(e)}", None
    finally:
        connection.close()

def get_user_info(user_id):
    """获取用户信息"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT id, username, email, role, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        return user
        
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return None
    finally:
        connection.close()

# Flask路由函数
def create_user_routes(app):
    """创建用户相关的路由"""
    
    @app.route('/api/user/register', methods=['POST'])
    def register():
        """用户注册"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        success, message = register_user(username, password, email)
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400
    
    @app.route('/api/user/login', methods=['POST'])
    def login():
        """用户登录"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        success, message, result = login_user(username, password)
        if success:
            return jsonify({
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({'error': message}), 401
    
    @app.route('/api/user/info', methods=['GET'])
    @require_auth
    def get_user_info_route():
        """获取当前用户信息"""
        user_id = request.user['user_id']
        user_info = get_user_info(user_id)
        
        if user_info:
            return jsonify({
                'message': '获取成功',
                'data': user_info
            }), 200
        else:
            return jsonify({'error': '获取用户信息失败'}), 500
    


# 初始化数据库
if __name__ == '__main__':
    init_database() 