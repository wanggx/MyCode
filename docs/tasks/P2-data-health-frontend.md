# P2-T2: 数据健康中心 — 前端页面

## 目标

实现数据中心页面的完整功能，包括质量总览、issue 列表、issue 详情和修复操作。

## 前提

P1-T2 已完成（DataCenterView.vue 骨架已创建），P2-T1 已完成（后端 API 可用）。

## 需要修改的文件

### 1. 重写 frontend/src/views/DataCenterView.vue

对应原型 `prototype/quant-prototype-v2.html` 第 504-514 行。

包含部分：

#### a. 质量总览 KPI

- 数据完整率（绿色大数字 + 趋势）
- 缺口问题数
- 异常问题数
- 受影响策略数

#### b. 过滤器

- 市场选择（全部/A股/港股）
- 数据类型（行情数据/基础资料/财务数据）
- 日期范围
- 股票代码输入
- 查询/重置按钮

#### c. 三列布局

1. 数据完整率趋势图（使用 ECharts 折线图）
2. 缺失数据日历（显示近30天，绿色=完整，黄色=部分缺失，红色=严重缺失）
3. 最新同步记录表格

#### d. Issue 列表

- issue_code、市场、数据类型、日期范围、缺失数量、严重级别、状态、操作
- 操作：查看详情、修复、忽略
- 严重级别用彩色标签显示

#### e. Issue 详情抽屉/对话框

点击"查看"打开侧边抽屉：
- 基础信息
- 缺失股票明细表格
- 影响范围
- 修复按钮

#### f. 修复确认对话框

点击"修复"弹出对话框：
- 修复方式选择（仅补缺失/覆盖重拉当日）
- 选项：自动复检（默认勾选）、重新聚合（默认勾选）、重跑策略（不勾选）
- 确认/取消按钮

#### g. 手动同步按钮

"同步股票列表"按钮触发 `POST /api/data/sync`。

## API 调用

- `GET /api/data/quality-summary` — 质量总览
- `GET /api/data/issues?market=&severity=&status=&page=&page_size=` — issue 列表
- `GET /api/data/issues/{id}` — issue 详情
- `POST /api/data/issues/{id}/repair` — 创建修复任务
- `POST /api/data/quality-scan` — 触发扫描

## 自测步骤

1. 前端启动不报错
2. 数据中心页面能显示质量总览 KPI
3. 能查看 issue 列表
4. 点击查看能展开详情
5. 能触发修复操作
