# Change Proposal: Backend Refactoring

## Why

The backend code has evolved from a rapid prototype into a functional but structurally disorganized codebase. The current `stock/stock/` directory nests backend code two levels deep, uses an inconsistently named `moduledir/` package, scatters database credentials across three separate files, and mixes HTTP routing, business logic, and SQL queries within single functions. This makes the code difficult to navigate, risky to modify, and prevents onboarding new contributors. The refactoring aims to establish a maintainable layered architecture without altering any system behavior.

## What (and what NOT)

**本次重构范围**：仅限于后端 Python 代码的目录重组和分层重构。

**前端代码完全不动**：本次重构不修改 `frontend/` 目录下的任何文件（.vue、.js、.css、.html 等）。后端 API 的路径、参数、响应格式全部保持不变，因此前端在重构前后看到的所有页面、交互、样式、数据展示都完全一致。

1. Migrate backend code from `stock/stock/` to `backend/` at project root
2. Restructure into three-layer architecture: `api/` (routes) → `services/` (business logic) → `repositories/` (data access)
3. Extract pure computation into `analysis/` module (MACD/KDJ, MA, volume, aggregation)
4. Centralize all configuration and secrets into `.env` + `core/config.py`
5. Rename `moduledir/chatutil.py` to `utils/notify.py` and `moduledir/dateutil.py` to `utils/dateutil.py`
6. Move HK module (`hk/`) into `backend/hk/`
7. Remove old `stock/stock/` directories after migration

## Impact

- **Behavioral change**: None. All 15 API endpoints maintain identical paths, methods, parameters, and response formats.
- **Code removal**: `stock/stock/backend/`, `stock/stock/moduledir/`, `stock/stock/db/`, `stock/stock/utils/`, `stock/stock/test/`, `stock/stock/backend/data/` — all deleted after migration.
- **New files**: ~35 files in `backend/` tree.
- **Dependencies**: Add `python-dotenv` (only new dependency).
- **CI/CD**: Update paths in `.github/workflows/backend-deploy.yml`.

## Risks

- Python import path breakage during migration: mitigated by phased verification after each layer.
- Hardcoded secrets may be missed during grep: mitigated by scanning for password/token/key patterns before and after.
- Global `_running_select_tasks` set must be preserved as module-level state in `services/select_service.py`.
