# 量化平台开发任务

本文档拆分了基于原型和技术方案的各阶段任务。每轮 OpenCode 按编号顺序执行任务。

## 执行流程

1. 一次只做一个编号的任务
2. 修改代码后必须自测（启动后端验证 API / 启动前端验证页面）
3. 自测完成后通知 claude review
4. claude review 通过后继续下一任务
5. claude review 不通过则回传问题给 OpenCode 修复

## 阶段总览

| 阶段 | 内容 | 负责人 |
|------|------|--------|
| Phase 1 | 任务中心（Task Center） | OpenCode |
| Phase 2 | 数据健康中心（Data Health Center） | OpenCode |
| Phase 3 | 策略参数化与信号解释 | OpenCode |
| Phase 4 | 日频回测 | OpenCode |
| Phase 5 | 模拟组合与观察池 | OpenCode |
| Phase 6 | 因子实验室 | OpenCode |

## 数据结构约定

- 日期字段统一使用 `YYYYMMDD` 字符串
- 股票代码统一使用 `ts_code`
- JSON 字段用于保存参数快照和解释快照
- 分页返回格式：`{"items":[], "total":N, "page":P, "page_size":S, "total_pages":T}`
- API 返回格式：`{"success": true/false, "data": {}, "message": ""}`

## 参考文档

- UI 原型: `prototype/quant-prototype-v2.html`
- 架构设计: `docs/quant-platform/architecture.md`
- 功能模块: `docs/quant-platform/modules.md`
- 数据健康: `docs/quant-platform/data-health.md`
- 数据库设计: `docs/quant-platform/database-draft.md`
- 实施路线: `docs/quant-platform/implementation-roadmap.md`

## 任务编号

- [P1-T1](P1-task-center.md) — 任务中心：DB + 后端（task_job, task_step 建表 + TaskService + Task API + Worker）
- [P1-T2](P1-task-center-frontend.md) — 任务中心：前端页面（TaskCenterView + 侧边栏改造）
- [P2-T1](P2-data-health.md) — 数据健康中心：DB + 后端（建表 + 检查+修复服务 + API）
- [P2-T2](P2-data-health-frontend.md) — 数据健康中心：前端页面
- [P3-T1](P3-strategy-signal.md) — 策略+信号：DB + 后端（建表 + 策略/信号服务 + API）
- [P3-T2](P3-strategy-signal-frontend.md) — 策略工作台+选股信号：前端页面
- [P4-T1](P4-backtest.md) — 回测中心：DB + 后端 + 前端
- [P5-T1](P5-portfolio-watchlist.md) — 组合风控：DB + 后端 + 前端
- [P6-T1](P6-factor-lab.md) — 因子实验室：DB + 后端 + 前端
