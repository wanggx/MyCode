# Tasks: Backend Refactoring

## 阶段总览

| 阶段 | 内容 | 文件数 | 验证方式 |
|------|------|--------|---------|
| 一 | 基础设施 (core + utils) | 8 | 模块导入验证 |
| 二 | 数据访问层 (repositories) | 7 | 模块导入验证 |
| 三 | 分析算法层 (analysis) + 单元测试 | 4+4 | pytest backend/tests/test_analysis/ |
| 四 | 服务层 (services) | 5 | 模块导入验证 |
| 五 | API 路由层 (api) | 5 | 模块导入验证 |
| 六 | 启动入口 | 3 | `python run.py` 启动 + 冒烟测试 |
| 七 | HK 模块迁移 | 3 | 模块导入验证 |
| 八 | 测试基建 + API 集成测试 | 10+ | pytest 全量通过 |
| 九 | 收尾清理 + 全体验证 | — | 9 项验收清单 + 前端对比确认 |

---

## Phase 1: Infrastructure

- [ ] Create `backend/` directory tree with all subdirectories
- [ ] Create `app/core/config.py` — `Settings` dataclass reading `.env`
- [ ] Create `app/core/database.py` — unified `get_engine()` from 3 existing DB files
- [ ] Create `app/core/security.py` — JWT + password hashing (from `user.py`)
- [ ] Create `app/core/response.py` — `success()` / `error()` helpers
- [ ] Create `app/core/logger.py` — (move from `utils/logger.py`)
- [ ] Create `app/utils/dateutil.py` — (move from `moduledir/dateutil.py`)
- [ ] Create `app/utils/notify.py` — (move + rename from `moduledir/chatutil.py`)

> **验证**: `python -c "from app.core.config import settings; print(settings.DB_HOST)"`

## Phase 2: Data Access Layer

- [ ] Create `repositories/base.py` — generic pagination template
- [ ] Create `repositories/user_repo.py` — users table CRUD
- [ ] Create `repositories/stock_repo.py` — stock basic info table
- [ ] Create `repositories/stock_daily_repo.py` — daily/weekly/monthly price data
- [ ] Create `repositories/stock_select_repo.py` — stock selection results
- [ ] Create `repositories/tushare_repo.py` — Tushare external API wrapper
- [ ] Create `repositories/hk_stock_repo.py` — HK stock data (from `hk/hkutil.py`)

> **验证**: `python -c "from app.repositories.base import BaseRepository; print('OK')"`

## Phase 3: Analysis Algorithms + 算法测试

- [ ] Create `analysis/indicators.py` — MACD/KDJ (from `backend/data/talib_metric.py`)
- [ ] Create `analysis/ma_analysis.py` — moving average (from `backend/data/select_ma.py`)
- [ ] Create `analysis/volume_analysis.py` — volume slope/magnify (from `backend/data/select_daily.py`)
- [ ] Create `analysis/aggregation.py` — weekly/monthly aggregation (from `backend/data/wm.py`)
- [ ] Write `backend/tests/test_analysis/test_indicators.py` — MACD/KDJ 计算正确性验证
- [ ] Write `backend/tests/test_analysis/test_ma.py` — 均线计算验证
- [ ] Write `backend/tests/test_analysis/test_volume.py` — 成交量斜率/放大计算验证
- [ ] Write `backend/tests/test_analysis/test_aggregation.py` — 周月聚合逻辑验证

> **验证**: `pytest backend/tests/test_analysis/ -v`

## Phase 4: Service Layer

- [ ] Create `services/auth_service.py` — login/register/change-password orchestration
- [ ] Create `services/stock_service.py` — stock query/sync orchestration
- [ ] Create `services/select_service.py` — stock selection orchestration with async thread
- [ ] Create `services/data_service.py` — data download/backfill orchestration
- [ ] Create `services/notify_service.py` — WeChat notification wrapper

> **验证**: `python -c "from app.services.auth_service import AuthService; print('OK')"`

## Phase 5: API Routes

- [ ] Create `api/auth.py` — Blueprint: register, login, info, change-password
- [ ] Create `api/stocks.py` — Blueprint: list, areas, industries, data, sync
- [ ] Create `api/stock_select.py` — Blueprint: select, mock
- [ ] Create `api/stock_check.py` — Blueprint: check, daily/add (migrate existing)
- [ ] Create `api/vol_line.py` — Blueprint: vol_line

> **验证**: `python -c "from app.api.auth import auth_bp; print('OK')"`

## Phase 6: Entry Point + 冒烟测试

- [ ] Create `app/__init__.py` — `create_app()` factory, register blueprints
- [ ] Create `tasks/scheduler.py` — daily 16:30 scheduler thread
- [ ] Create `run.py` — application entry point
- [ ] Write `backend/tests/smoke_test.py` — 独立冒烟脚本（不依赖 pytest）

> **验证**: `python backend/run.py` 启动成功 → 在另一个终端 `curl http://localhost:8080/api/health` 返回 200
>
> **冒烟测试**: `python backend/tests/smoke_test.py` 全部 PASS

## Phase 7: HK Module

- [ ] Move `stock/hk/` into `backend/hk/`, update imports

> **验证**: `python -c "from hk.hkutil import getHkStockList; print('OK')"`

## Phase 8: 测试基建 + API 集成测试

- [ ] Create `backend/tests/conftest.py` — Flask test client fixture
- [ ] Create `backend/tests/test_core/test_config.py` — Settings 读取 & 环境变量覆盖
- [ ] Create `backend/tests/test_core/test_security.py` — JWT 生成/验证/密码哈希
- [ ] Create `backend/tests/test_core/test_response.py` — 统一响应格式
- [ ] Create `backend/tests/test_api/test_auth.py` — 注册/登录/信息/改密 8 场景
- [ ] Create `backend/tests/test_api/test_stocks.py` — 股票列表/搜索/日线 6 场景
- [ ] Create `backend/tests/test_api/test_select.py` — 选股查询/异步触发/重复拦截 4 场景
- [ ] Create `backend/tests/test_api/test_check.py` — 数据补录/校验 3 场景
- [ ] Create `backend/tests/test_api/test_vol_line.py` — 成交量线 2 场景
- [ ] Create `backend/tests/test_migration/test_imports.py` — 所有模块可导入验证
- [ ] Create `backend/tests/test_migration/test_structure.py` — 新旧目录结构完整性验证
- [ ] Create `backend/tests/test_migration/test_secrets.py` — grep 验证无硬编码密钥残留

> **验证**: `pytest backend/tests/ -v` 全部通过

## Phase 9: 收尾清理 + 全体验证

### 部署脚本测试

- [ ] `bash -n bin/start.sh` — start.sh 语法检查
- [ ] `bash -n bin/stop.sh` — stop.sh 语法检查
- [ ] 创建 `tests/test_deploy/test_start_stop.sh` — 部署脚本集成测试
- [ ] 运行部署集成测试（手动）：
  - [ ] `bash bin/start.sh` → 应用正常启动，`.backend_pid` 文件创建
  - [ ] `curl http://localhost:8080/api/health` → 200
  - [ ] `bash bin/start.sh` → 输出 "already running"（二次启动检测）
  - [ ] `bash bin/stop.sh` → 进程终止，`.backend_pid` 删除
  - [ ] `bash bin/start.sh` → 再次正常启动（停止后可重新拉起）

### 迁移验证清单

- [ ] `pytest backend/tests/test_migration/test_imports.py` — 所有模块可正确导入
- [ ] `pytest backend/tests/test_migration/test_structure.py` — 新目录结构完整，旧目录已删除
- [ ] `pytest backend/tests/test_migration/test_secrets.py` — 无硬编码密码/token/key 残留
- [ ] `pytest backend/tests/test_api/ -v` — 全部 15 个 API 接口行为一致
- [ ] `pytest backend/tests/test_analysis/ -v` — 分析算法计算结果一致
- [ ] `pytest backend/tests/test_core/ -v` — 基础设施单元测试通过
- [ ] Delete old directories: `stock/stock/backend/`, `stock/stock/moduledir/`, `stock/stock/db/`, `stock/stock/utils/`, `stock/stock/test/`, `stock/stock/backend/data/`
- [ ] Rebuild venv at `backend/.venv`: `python -m venv backend/.venv && source backend/.venv/bin/activate && pip install -r backend/requirements.txt`
- [ ] Update `.github/workflows/backend-deploy.yml` — `paths: 'stock/**'` 改为 `paths: 'backend/**'`
- [ ] Update `bin/start.sh` — `MAIN_PY` 路径从 `stock/main.py` 改为 `backend/run.py`
- [ ] Update `.gitignore` — 补充 `__pycache__/`, `.venv/`, `.env`, `.idea/`, `logs/`, `*.csv`, `*.pid`

### 前端完整性检查

- [ ] `git diff frontend/` 输出为空 — 确认前端代码无任何改动
- [ ] 重构后打开前端页面，逐一核对各页面布局、样式、交互与重构前一致

### 验收标准

- [ ] `python backend/run.py` 启动成功，Flask 监听 8080
- [ ] `GET /api/health` 返回 `{"status": "healthy"}`
- [ ] 用户注册 → 登录 → 获取信息 → 修改密码 完整流程正常
- [ ] 股票列表分页/关键词搜索/地域行业筛选正常
- [ ] 股票日线/周线/月线数据查询正常
- [ ] 选股列表查询 → 空数据触发异步选股 → 再次查询有数据 完整流程正常
- [ ] 数据补录提交 → 异步下载任务启动正常
- [ ] 成交量线数据查询正常
- [ ] 定时任务线程正常初始化，不阻塞主进程
- [ ] `pytest backend/tests/ -v` 全部通过
- [ ] 旧 `stock/stock/` 下 backend/moduledir/db/utils/data/test 目录已清理
