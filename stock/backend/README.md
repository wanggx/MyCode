# 股票数据管理系统 - Backend

这是一个基于Flask的股票数据管理系统后端，提供用户登录和数据列表功能。

## 功能特性

- 用户注册和登录（JWT认证）
- 用户信息管理
- 股票数据列表（Mock数据）
- 股票搜索和筛选
- 市场概览统计
- MySQL数据库存储

## 项目结构

```
stock/
├── main.py              # 主程序入口
└── backend/
    ├── user.py              # 用户登录接口
    ├── stock_list.py        # 股票数据接口
    ├── db_config.py         # 数据库配置文件
    ├── init_database.sql    # 数据库初始化脚本
    ├── requirements.txt     # Python依赖
    └── README.md           # 项目说明
```

## 安装和配置

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

数据库配置在 `db_config.py` 文件中：

```python
DB_CONFIG = {
    'host': 'rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com',
    'port': 3306,
    'user': 'root',
    'password': '8Dm4PQU2pp6!C3y',
    'database': 'stock',
    'charset': 'utf8mb4'
}
```

### 3. 初始化数据库

**重要**: 请先手动执行SQL文件初始化数据库

```bash
# 方法1: 使用mysql命令行
mysql -h rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com -P 3306 -u root -p8Dm4PQU2pp6!C3y < init_database.sql

# 方法2: 在MySQL客户端中执行
mysql -h rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com -P 3306 -u root -p8Dm4PQU2pp6!C3y
source init_database.sql;
```

## 运行服务

```bash
# 在stock目录下运行
cd stock
python main.py
```

服务将在 `http://localhost:8080` 启动

## API接口文档

### 用户相关接口

#### 1. 用户注册
- **URL**: `POST /api/user/register`
- **请求体**:
```json
{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
}
```

#### 2. 用户登录
- **URL**: `POST /api/user/login`
- **请求体**:
```json
{
    "username": "admin",
    "password": "123456"
}
```
- **响应**:
```json
{
    "message": "登录成功",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin"
        }
    }
}
```

#### 3. 获取用户信息
- **URL**: `GET /api/user/info`
- **Headers**: `Authorization: Bearer <token>`

### 股票数据接口

#### 1. 获取股票列表
- **URL**: `GET /api/stocks`
- **Headers**: `Authorization: Bearer <token>`
- **查询参数**:
  - `page`: 页码（默认1）
  - `page_size`: 每页数量（默认10）
  - `keyword`: 搜索关键词
  - `sector`: 行业筛选
  - `sort_by`: 排序字段（code/price/change_percent/volume/market_cap）
  - `sort_order`: 排序方向（asc/desc）

#### 2. 获取股票详情
- **URL**: `GET /api/stocks/<code>`
- **Headers**: `Authorization: Bearer <token>`

#### 3. 搜索股票
- **URL**: `GET /api/stocks/search?keyword=<关键词>`
- **Headers**: `Authorization: Bearer <token>`

#### 4. 获取行业列表
- **URL**: `GET /api/stocks/sectors`
- **Headers**: `Authorization: Bearer <token>`

#### 5. 市场概览
- **URL**: `GET /api/stocks/market-overview`
- **Headers**: `Authorization: Bearer <token>`

### 健康检查

- **URL**: `GET /api/health`

## 默认账号

系统初始化后会创建以下默认账号：

- **管理员账号**:
  - 用户名: `admin`
  - 密码: `123456`

- **测试用户账号**:
  - 用户名: `user1`, 密码: `user123`
  - 用户名: `user2`, 密码: `user123`
  - 用户名: `manager`, 密码: `manager123`

## 数据库管理

### 测试数据库连接
```bash
cd stock
python -c "from backend.user import test_database_connection; test_database_connection()"
```

### 查看数据库信息
```sql
USE stock;
SELECT id, username, email, role, status, created_at FROM users;
```

## 使用示例

### 1. 用户登录
```bash
curl -X POST http://localhost:8080/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'
```

### 2. 获取股票列表
```bash
curl -X GET http://localhost:8080/api/stocks \
  -H "Authorization: Bearer <your_token>"
```

### 3. 搜索股票
```bash
curl -X GET "http://localhost:8080/api/stocks/search?keyword=银行" \
  -H "Authorization: Bearer <your_token>"
```

## 注意事项

1. 确保MySQL数据库服务可访问
2. 股票数据为Mock数据，每次请求会随机生成
3. JWT token有效期为24小时
4. 所有股票数据接口都需要认证
5. 密码使用MD5加密存储
6. 支持跨域请求（CORS）

## 开发说明

- 用户认证使用JWT token
- 数据库使用PyMySQL连接
- 股票数据为模拟数据，包含10只股票
- 支持按行业、价格、涨跌幅等条件筛选
- 提供分页、排序、搜索功能
- 包含定时任务调度器 