# 任务执行工作流

## 角色分工

| 角色 | 职责 |
|------|------|
| **claude (主控)** | 拆分任务、审核代码、决策问题回退 |
| **OpenCode** | 按任务文件编写代码、自测 |

## 执行流程

```
claude 拆分任务 → 写入 docs/tasks/*.md
       ↓
OpenCode 读取任务编号 N
       ↓
OpenCode 编写代码 + 自测
       ↓
OpenCode 通知 claude review（在对话中说明"任务N已完成"）
       ↓
claude review 代码 
  ├── 通过 → 标记完成，进入任务 N+1
  └── 不通过 → 描述问题，OpenCode 修复 → 回到 review
```

## 任务顺序

按编号顺序执行：

| 编号 | 文件 | 内容 | 依赖 |
|------|------|------|------|
| P1-T1 | [P1-task-center.md](P1-task-center.md) | 任务中心 DB + 后端 | 无 |
| P1-T2 | [P1-task-center-frontend.md](P1-task-center-frontend.md) | 任务中心前端 + 导航改造 | P1-T1 |
| P2-T1 | [P2-data-health.md](P2-data-health.md) | 数据健康中心 DB + 后端 | P1-T1 |
| P2-T2 | [P2-data-health-frontend.md](P2-data-health-frontend.md) | 数据健康中心前端 | P1-T2, P2-T1 |
| P3-T1 | [P3-strategy-signal.md](P3-strategy-signal.md) | 策略+信号 DB + 后端 | P1-T1 |
| P3-T2 | [P3-strategy-signal-frontend.md](P3-strategy-signal-frontend.md) | 策略+信号前端 | P1-T2, P3-T1 |
| P4-T1 | [P4-backtest.md](P4-backtest.md) | 回测中心全栈 | P1-T1, P3-T1 |
| P5-T1 | [P5-portfolio-watchlist.md](P5-portfolio-watchlist.md) | 组合风控全栈 | P3-T1 |
| P6-T1 | [P6-factor-lab.md](P6-factor-lab.md) | 因子实验室全栈 | P2-T1 |

## 代码规范

### 后端
- 单文件 ≤1000 行，单函数 ≤150 行
- `api/` 只能调 `services/`，不能直调 `repositories/`
- 导入前缀以 `backend/` 为根，如 `from app.core.config import settings`
- API 返回格式：`{"success": true, "data": {}, "message": ""}`
- 分页返回格式：`{"items":[], "total":N, "page":P, "page_size":S, "total_pages":T}`
- 数据库连接使用 `app.core.database.get_db_connection()`
- 分页查询使用 `app.repositories.base.paginate_sql()`

### 前端
- Vue 3 + Element Plus + ECharts + Vuex + Vue Router
- 使用 Composition API 或 Options API 均可
- API 调用通过 `frontend/src/config/axios.js` 的 axios 实例

## 自测要求

**每个任务完成后必须自测，自测通过后才能通知 claude review。**

自测内容包括但不限于：
1. **后端任务**：启动服务不报错，API 返回正确状态码和数据格式
2. **前端任务**：`npm run serve` 不报错，页面能正常渲染和交互
3. **DB 任务**：检查表结构是否正确创建
