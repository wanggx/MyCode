# Specification (Delta): Stock Platform — MySQL 连接池

## ADDED Requirements

### Requirement: MySQL 连接池

系统 SHALL 使用 SQLAlchemy 内置连接池复用数据库连接，避免每次查询新建 TCP 连接。

#### Scenario: 连接池初始化
- **GIVEN** 系统启动时
- **WHEN** `get_engine()` 首次被调用
- **THEN** 系统 SHALL 创建一个带有 `QueuePool` 的 SQLAlchemy Engine
- **AND** 连接池参数 SHALL 为 `pool_size=10, max_overflow=5, pool_timeout=30, pool_recycle=3600, pool_pre_ping=True`

#### Scenario: 连接复用
- **GIVEN** 连接池已初始化
- **WHEN** `get_db_connection()` 被连续调用多次
- **THEN** 后续调用 SHALL 从池中获取连接而非新建
- **AND** `conn.close()` SHALL 将连接归还池中而非真正关闭

#### Scenario: Engine 单例
- **GIVEN** 系统运行中
- **WHEN** `get_engine()` 被多次调用
- **THEN** 每次 SHALL 返回同一个 Engine 实例
- **AND** `hk/hkutil.py`、`stock_daily_repo.py`、`hk_stock_repo.py` 中的重复 `_get_engine()` SHALL 被消除，统一使用 `core.database.get_engine()`

#### Scenario: 连接健康检查
- **GIVEN** 连接池中存在空闲连接超过 1 小时
- **WHEN** `pool_recycle=3600` 触发
- **THEN** 该连接 SHALL 被自动回收并重建
- **AND** `pool_pre_ping=True` SHALL 确保每次取出的连接可用

#### Scenario: MySQL 断连后自动恢复
- **GIVEN** 连接池正常运行中
- **WHEN** MySQL 服务宕机后恢复
- **THEN** `pool_pre_ping` SHALL 检测到失效连接并丢弃
- **AND** QueuePool SHALL 自动创建新连接替代已失效的连接
- **AND** 整个过程无需应用层代码干预

#### Scenario: mid-query 断连重试
- **GIVEN** 一个正在执行中的数据库查询
- **WHEN** 网络在查询执行过程中断开
- **THEN** `@retry_on_db_failure` 装饰器 SHALL 捕获 `OperationalError`
- **AND** SHALL invalidate 池中所有连接触发重建
- **AND** SHALL 按指数退避重试（0.5s → 1s），最多 2 次

### Requirement: 连接池参数可配置化

连接池参数 SHALL 可通过 `.env` 文件配置，无需修改代码。

#### Scenario: 通过 .env 调整连接池
- **GIVEN** `.env` 文件中设置了 `DB_POOL_SIZE=20`
- **WHEN** 系统启动或首次调用 `get_engine()`
- **THEN** 创建的连接池 SHALL 使用 `pool_size=20`
- **AND** 所有连接池参数（`DB_POOL_SIZE`, `DB_POOL_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`, `DB_POOL_PRE_PING`）SHALL 遵循 `Settings` 的环境变量覆盖规则

## MODIFIED Requirements

### Requirement: 系统健康检查

（无变更 — `/api/health` 返回格式和行为保持一致）
