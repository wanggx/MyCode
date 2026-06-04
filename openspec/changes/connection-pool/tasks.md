# Tasks: MySQL 连接池

## Step 1: config.py — 新增连接池配置字段

- [ ] `Settings` 新增 5 个字段：`DB_POOL_SIZE=10`, `DB_POOL_OVERFLOW=5`, `DB_POOL_TIMEOUT=30`, `DB_POOL_RECYCLE=3600`, `DB_POOL_PRE_PING=True`
- [ ] `__post_init__` 增加这 5 个字段的环境变量覆盖（整型或布尔转换）

## Step 2: core/database.py — Engine 单例 + 池化连接 + 重试工具

- [ ] `get_engine()` 改为使用模块级全局变量缓存 Engine 实例
- [ ] 从 `settings` 读取连接池参数：`pool_size=settings.DB_POOL_SIZE, max_overflow=settings.DB_POOL_OVERFLOW, pool_timeout=settings.DB_POOL_TIMEOUT, pool_recycle=settings.DB_POOL_RECYCLE, pool_pre_ping=settings.DB_POOL_PRE_PING`
- [ ] `get_db_connection()` 改为 `get_engine().raw_connection()` 返回池化 pymysql 连接
- [ ] `execute_query()` / `execute_count_query()` 自动受益（它们内部调 `get_db_connection()`）
- [ ] 保留 `test_connection()` 不变
- [ ] 提供 `@retry_on_db_failure` 装饰器，捕获 `OperationalError`/`DisconnectionError`，invalidate 后指数退避重试 2 次

## Step 3: 消除重复的 `_get_engine()`

- [ ] `hk/hkutil.py`：删除 `_get_engine()`，所有调用处改为 `from app.core.database import get_engine`
- [ ] `app/repositories/stock_daily_repo.py`：删除 `_get_engine()`，所有调用处改为 `from app.core.database import get_engine`
- [ ] `app/repositories/hk_stock_repo.py`：删除 `_get_engine()`，所有调用处改为 `from app.core.database import get_engine`

## Step 4: 验证

- [ ] 启动后端：`cd backend && .venv/Scripts/python run.py`
- [ ] 确认 6 个模块表初始化成功
- [ ] 冒烟测试：`curl http://localhost:5000/api/health` 返回 200
- [ ] 测试关键 API：signals、portfolio、data-quality 等返回正常
- [ ] 确认连接池日志：一条 `INFO` 日志表明连接池已初始化
- [ ] 模拟断连测试（可选）：重启 MySQL → 确认 API 自动恢复

## 不需要做的

- 不改 repository 文件中的业务逻辑和 SQL
- 不改 API 路由
- 不新增第三方依赖
- 不修改数据库表结构
