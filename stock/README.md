# 股票数据管理系统

这是一个基于Flask的股票数据管理系统，提供用户登录和数据列表功能。

## 项目结构

```
stock/
├── main.py              # 主程序入口
├── README.md           # 项目说明
└── backend/
    ├── user.py              # 用户登录接口
    ├── stock_list.py        # 股票数据接口
    ├── db_config.py         # 数据库配置文件
    ├── init_database.sql    # 数据库初始化脚本
    ├── requirements.txt     # Python依赖
    └── README.md           # 详细说明文档
```

## 快速开始

### 1. 安装依赖
```bash
cd stock/backend
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
# 执行SQL文件初始化数据库
mysql -h rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com -P 3306 -u root -p8Dm4PQU2pp6!C3y < backend/init_database.sql
```

### 3. 运行服务
```bash
# 在stock目录下运行
python main.py
```

服务将在 `http://localhost:8080` 启动

## 默认账号

- **管理员账号**: admin / 123456
- **测试用户**: user1 / user123

## API接口

- 用户注册: `POST /api/user/register`
- 用户登录: `POST /api/user/login`
- 获取股票列表: `GET /api/stocks`
- 搜索股票: `GET /api/stocks/search`
- 市场概览: `GET /api/stocks/market-overview`

详细API文档请查看 `backend/README.md` 