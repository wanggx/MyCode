# P3-T2: 策略工作台 + 选股信号 — 前端页面

## 目标

实现策略工作台和选股信号两个前端页面。

## 前提

P1-T2 已完成（骨架页面存在），P3-T1 已完成（后端 API 可用）。

## 需要修改的文件

### 1. 重写 frontend/src/views/StrategyWorkspaceView.vue

对应原型 `prototype/quant-prototype-v2.html` 第 532-544 行。

包含部分：

#### a. 策略列表（左侧）
- 展示所有策略卡片：名称、状态标签（运行中/已停止）、版本号
- 点击切换选中的策略
- 新建策略按钮

#### b. 策略设置（右侧）
- 策略名称
- 股票池选择（沪深A股剔除ST/港股通）
- 调仓周期（日/周）
- 最大持仓数
- 手续费、滑点
- 买入条件展示（规则盒）
- 卖出条件展示（规则盒）
- 操作按钮：保存草稿、保存并运行、回测

#### c. 最近运行（右侧底部卡片）
- 表格：运行时间、状态、收益率、最大回撤

#### d. 参数版本（右侧底部卡片）
- 版本列表：版本号、更新时间、备注
- 当前版本高亮

API 调用：
- `GET /api/strategies` — 策略列表
- `GET /api/strategies/{id}` — 策略详情
- `POST /api/strategies` — 新建策略
- `PUT /api/strategies/{id}` — 更新策略
- `POST /api/strategies/{id}/versions` — 创建版本
- `POST /api/strategies/{id}/run` — 运行策略
- `GET /api/strategies/{id}/runs` — 获取运行记录

### 2. 重写 frontend/src/views/StockSignalsView.vue

对应原型 `prototype/quant-prototype-v2.html` 第 552-555 行。

包含：

#### a. 过滤器
- 市场选择（全部/沪市/深市/港股）
- 策略选择（全部/放量突破/均线趋势/...）
- 日期选择
- 最低信号分筛选
- 查询/重置按钮

#### b. 信号表格
- 日期、代码、名称、市场、策略、信号分、量能、趋势、MACD、KDJ、入选原因、操作
- 信号分高的标红
- 操作按钮：详情（打开抽屉）

#### c. 信号详情抽屉
- 股票名称和代码
- 价格信息
- 信号解释（列表形式展示入选原因）
- 综合评分

API 调用：
- `GET /api/signals?trade_date=&strategy_id=&market=&min_score=&page=&page_size=`
- `GET /api/signals/{id}`
- `POST /api/signals/{id}/status`

## 自测步骤

1. 策略工作台页面能显示策略列表
2. 能切换查看不同策略
3. 能创建新策略和版本
4. 能提交策略运行
5. 选股信号页面能筛选和展示信号
6. 点击信号详情能显示解释信息
