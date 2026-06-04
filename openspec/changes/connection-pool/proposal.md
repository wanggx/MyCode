# Change Proposal: MySQL 连接池

## Why

当前系统中所有数据库操作都通过 `get_db_connection()` 获取连接，这个函数每次被调用时都创建一个全新的 `pymysql.connect()` TCP 连接。经统计，整个代码库中 `get_db_connection()` 被调用了 100+ 次，分布在 10+ 个 repository 文件中。每次 HTTP 请求可能涉及多次数据库查询，每次查询都新建和销毁连接，带来严重问题：

1. **性能开销大**：MySQL 连接建立需要 TCP 三次握手 + 认证握手，每次耗时 10-50ms。一个页面请求涉及 3-5 次查询，仅连接建立就浪费 30-250ms。
2. **连接数不可控**：无连接池意味着高并发下每个请求都创建新连接，容易达到 MySQL `max_connections` 限制（默认 151），导致服务不可用。
3. **连接泄漏风险**：repository 层的 try/finally 模式依赖开发者确保 `conn.close()` 执行，异常路径下可能泄漏连接。
4. **重复的引擎创建**：`get_engine()` 和 `hk/hkutil.py` 的 `_get_engine()` 每次调用都创建新的 SQLAlchemy Engine，浪费了 SQLAlchemy 内置的连接池能力。

## What

引入统一的 MySQL 连接池，所有数据库操作复用池中连接，不再每次新建。

变更范围：

- **新增**：在 `core/database.py` 中实现 `ConnectionPool` 管理类
- **修改**：`core/database.py` 中的 `get_db_connection()` 改为从池中获取
- **修改**：`core/database.py` 中的 `get_engine()` 改为缓存单例
- **修改**：消除 `hk/hkutil.py`、`stock_daily_repo.py`、`hk_stock_repo.py` 中的重复 `_get_engine()` 定义
- **不动**：各 repository 文件中的业务逻辑、SQL 语句、方法签名全部保持不变

## Impact

- **性能提升**：预计 API 响应时间降低 20-50%（取决于查询次数）
- **连接数稳定**：池大小 = 10，不再随并发增加
- **行为变更**：无。所有 API 的路径、参数、响应格式不变
- **新依赖**：无。复用 SQLAlchemy 内置的 `QueuePool` + `raw_connection()`
- **影响范围**：仅 `backend/app/core/database.py` + 消除 3 处重复 `_get_engine()`
