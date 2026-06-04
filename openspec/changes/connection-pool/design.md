# Design: MySQL 连接池

## 现状分析

### 当前调用链

```
HTTP Request → API → Service → Repository
                                   |
                                   ├── get_db_connection()  ← 每次新建 pymysql 连接
                                   │     ├── cursor.execute()
                                   │     └── conn.close()
                                   │
                                   ├── get_engine()  ← 每次新建 SQLAlchemy Engine（含新连接池）
                                   │     └── pd.read_sql() / df.to_sql()
                                   │
                                   └── _get_engine()  ← hk/ 模块重复定义
```

### 问题量化

当前关键路径上的连接创建次数：

| 模块 | 位置 | 连接方式 | 调用次数 |
|------|------|---------|---------|
| `get_db_connection()` | `core/database.py` | 每次 `pymysql.connect()` | ~100+ |
| `get_engine()` | `core/database.py` | 每次 `create_engine()` | 不限 |
| `_get_engine()` | `hk/hkutil.py` | 每次 `create_engine()` | 6 |
| `_get_engine()` | `stock_daily_repo.py` | 每次 `create_engine()` | 8 |
| `_get_engine()` | `hk_stock_repo.py` | 每次 `create_engine()` | 5 |

## 设计方案

### 核心思路：单例 Engine + QueuePool

SQLAlchemy 的 `create_engine()` 默认使用 `QueuePool`（池大小=5），问题在于每次都创建新 engine 导致这个池从未被复用。解决方案：

1. **Engine 改为模块级单例**：`get_engine()` 首次调用时创建，之后复用
2. **`get_db_connection()` 改为从 Engine 取 raw_connection**：`engine.raw_connection()` 返回池化的 pymysql 连接
3. **消除所有重复的 `_get_engine()`**：统一使用 `core.database.get_engine()`

### 架构图

```
┌─────────────────────────────────────┐
│         ConnectionPool              │
│         (模块级单例)                  │
│                                     │
│  SQLAlchemy Engine (1个)            │
│  ┌─────────────────────────────┐   │
│  │  QueuePool (size=10)        │   │
│  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐  │   │
│  │  │ C1│ │ C2│ │...│ │C10│  │   │
│  │  └───┘ └───┘ └───┘ └───┘  │   │
│  │  overflow=5                │   │
│  │  timeout=30s               │   │
│  │  recycle=3600s             │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
          │               │
          ▼               ▼
  engine.connect()   engine.raw_connection()
  (pd.read_sql)      (pymysql DictCursor)
```

### 连接池配置

| 参数 | 值 | 说明 |
|------|----|------|
| `pool_size` | 10 | 核心连接数 |
| `max_overflow` | 5 | 峰值额外连接数 |
| `pool_timeout` | 30 | 等连接超时秒数 |
| `pool_recycle` | 3600 | 连接 1 小时后回收 |
| `pool_pre_ping` | True | 每次取连接前发 ping |

### 参数可配置化

所有连接池参数不在 `database.py` 中硬编码，而是通过 `core/config.py` 的 `Settings` 读取 `.env` 配置：

```ini
# backend/.env 新增
DB_POOL_SIZE=10
DB_POOL_OVERFLOW=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True
```

`config.py` 中新增对应字段，支持环境变量覆盖（遵循现有模式）。这样无需改代码即可调优连接池。

### 断连自动恢复机制

SQLAlchemy 的 `QueuePool` 提供 4 层防护：

```
请求连接
  │
  ▼
┌─────────────────────────────────┐
│ Layer 1: pool_pre_ping          │  ← 每次取连接前执行 SELECT 1
│  ├── 成功 → 返回可用连接         │     失败自动标记 invalidate
│  └── 失败 → discard + 新建连接   │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│ Layer 2: pool_recycle           │  ← 连接超过 TTL 后强制回收
│  (默认 3600s, 需 < MySQL        │     防止 MySQL wait_timeout 杀连接
│   wait_timeout)                 │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│ Layer 3: 自动 invalidate + 重建  │  ← MySQL 重启后 pool_pre_ping
│  QueuePool 自动创建新连接        │     检测到所有连接失效 → 逐个丢弃
│  替代已失效的                    │     → 新建连接 → 池恢复
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│ Layer 4: 查询级重试              │  ← mid-query 断连时的兜底
│  @retry_on_db_failure           │     捕获 OperationalError
│  最多重试 2 次，指数退避          │     invalidate 失效连接后重试
└─────────────────────────────────┘
```

#### Layer 1-3：连接池自动恢复（无需应用层代码）

MySQL 重启或网络闪断场景下的自动恢复流程：

```
时间线：
1. MySQL 宕机 / 网络断
2. 请求到达，pool_pre_ping 执行 SELECT 1 → 失败
3. QueuePool 标记该连接 invalidate → 丢弃
4. pool 尝试创建新连接 → MySQL 未恢复 → 失败
5. 后续请求全部在 pool_timeout=30s 内等待
6. MySQL 恢复
7. 下一个请求触发 pool_pre_ping → 新建连接 → SELECT 1 成功
8. 池自动恢复，后续请求正常处理
```

整个过程**不需要应用层代码干预**，连接池自行恢复。

#### Layer 4：查询级重试（mid-query 断连兜底）

如果连接在查询**执行过程中**断掉（而非取连接时），`pool_pre_ping` 无法覆盖。需要 `@retry_on_db_failure` 重试装饰器兜底：

```python
import time
from functools import wraps
from sqlalchemy.exc import OperationalError, DisconnectionError


def retry_on_db_failure(max_retries=2, base_delay=0.5):
    """数据库操作重试装饰器：捕获连接错误，invalidate 后重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_error = e
                    if attempt < max_retries:
                        # invalidate 池中所有连接，触发重建
                        from app.core.database import get_engine
                        get_engine().pool.invalidate()
                        time.sleep(base_delay * (2 ** attempt))  # 指数退避
            raise last_error
        return wrapper
    return decorator
```

此装饰器**可选使用**，用在关键写入路径（创建信号、保存回测结果等），只读查询可用默认行为（失败让上层处理）。

设计原则：连接池自身负责自动恢复，重试装饰器作为 mid-query 断连的兜底，不强制全量使用。

### 兼容性保障

- `engine.raw_connection()` 返回的底层是 `pymysql.connections.Connection`，与现有 `DictCursor` 模式完全兼容
- `with conn.cursor() as cursor:` 模式不变
- `conn.commit()` / `conn.close()` 不变（close 归还连接到池，而非真正关闭）

### 文件修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/core/config.py` | 修改 | Settings 新增 `DB_POOL_*` 字段 |
| `app/core/database.py` | 修改 | Engine 改为单例，`get_db_connection()` 从池取 |
| `hk/hkutil.py` | 修改 | 消除 `_get_engine()`，使用 `from app.core.database import get_engine` |
| `app/repositories/stock_daily_repo.py` | 修改 | 消除 `_get_engine()`，使用 `get_engine()` |
| `app/repositories/hk_stock_repo.py` | 修改 | 消除 `_get_engine()`，使用 `get_engine()` |

## 回滚方案

恢复 `core/database.py` 和 `core/config.py` 到修改前版本即可，各 repository 文件无需改动。
