# QT 量化平台 — 总体设计 V1

> 目标：对标米筐（RiceQuant），首期聚焦回测中心。
> 技术栈：后端 Python Flask + rqalpha 6.x，前端 Vue 3 + Element Plus + ECharts，数据库 MySQL (qt_dev)。
> 参考项目：rqalpha (/Users/gxwang/QT/rqalpha)，QTrade (/Users/gxwang/QT/QTrade)。

---

## 一、平台功能蓝图

```
┌──────────────────────────────────────────────────────────────────┐
│  QT 量化平台                                                      │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│  策略研究  │ ★回测中心 │  模拟交易  │  数据中心  │  因子研究  │  组合管理  │
│  (二期)   │  (一期)  │  (二期)   │ (一期支撑) │  (二期)   │  (三期)   │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

**一期范围（本次设计）：**
- ★ **回测中心**：策略编写 → 回测配置 → 执行 → 结果分析（全流程）
- **数据中心**（支撑）：行情数据管理、数据源配置
- **策略管理**（支撑）：策略 CRUD、版本管理、代码编辑器
- **系统框架**：用户认证、导航布局

---

## 二、UI 设计

### 2.1 整体布局

沿用现有 MainLayout 侧边栏 + 顶栏 + 内容区结构，但重新设计菜单和路由：

```
┌─────────────────────────────────────────────────────────┐
│  QT 量化平台                        [数据日期] [用户▾]    │ ← 顶栏 56px
├──────────┬──────────────────────────────────────────────┤
│ 📊 工作台  │                                              │
│ 📝 策略研究 │          <router-view />                     │
│ ⚡ 回测中心 │         # 三、API 设计                       │
│ 📈 数据中心 │                                              │
│ 🔬 因子研究 │                                              │
│ 💼 组合管理 │                                              │
│ ⚙️ 系统设置 │                                              │
├──────────┴──────────────────────────────────────────────┤
│  v1.0.0  |  rqalpha 6.x  |  MySQL qt_dev                │ ← 状态栏 24px
└─────────────────────────────────────────────────────────┘
```

**侧边栏菜单设计（6 项，一期）：**

| 图标 | 菜单名 | 路由 | 说明 |
|------|--------|------|------|
| 📊 | 工作台 | `/workspace` | 首页概览：今日回测统计、最近策略、系统状态 |
| 📝 | 策略研究 | `/strategies` | 策略列表 + 代码编辑器 + 版本管理 |
| ⚡ | 回测中心 | `/backtest` | 回测配置 → 进度 → 结果分析（核心页面） |
| 📈 | 数据中心 | `/data` | 行情数据概览、数据下载、质量监控 |
| 🔬 | 因子研究 | `/factors` | 因子列表、IC 分析、分组收益（二期重点） |
| 💼 | 组合管理 | `/portfolio` | 组合构建、风险监控（三期） |

### 2.2 页面详细设计

#### 2.2.1 工作台（Workspace）

```
┌──────────────────────────────────────────────────────────────┐
│  工作台                                         2026-06-19    │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ 回测总数   │ │ 运行中    │ │ 策略总数   │ │ 数据覆盖   │        │
│  │   128     │ │   3      │ │   24     │ │ 2010-2026 │        │
│  │  ↑12 本月 │ │  2 排队   │ │  ↑3 本周  │ │ 99.2%    │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│                                                              │
│  ┌─────────────────────────────┐ ┌──────────────────────────┐│
│  │  最近回测 (5条)              │ │  系统状态                 ││
│  │  · 双均线策略 v3  完成 2分钟前│ │  · rqalpha 6.1.4 ✓      ││
│  │  · RSI策略 v2     运行中     │ │  · MySQL qt_dev   ✓    ││
│  │  · 布林带策略 v1  失败 10分钟 │ │  · 数据源 Tushare  ✓    ││
│  │  · ...                     │ │  · Worker 运行中   ✓    ││
│  └─────────────────────────────┘ └──────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  回测成功率趋势 (ECharts 折线图)                          ││
│  │  ▓▓▓▓▓▓▓▓▓▓▓░░░ 最近7天                                 ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

#### 2.2.2 策略研究（Strategy Research）— 对标米筐"策略研究"

```
┌──────────────────────────────────────────────────────────────┐
│  策略研究                            [+ 新建策略] [导入]       │
├──────────────────────────────────────────────────────────────┤
│  筛选：[全部类型▾] [全部状态▾]  🔍 搜索...                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  策略列表 (左侧 320px)        │  策略详情 (右侧)           ││
│  │  ┌────────────────────────┐  │  ┌──────────────────────┐ ││
│  │  │ ● 双均线趋势跟踪       │  │  │ 双均线趋势跟踪       │ ││
│  │  │   v3 · 2026-06-18     │  │  │ 创建: 2026-05-01     │ ││
│  │  │   最近回测: ✅ 收益+32% │  │  │ 最近修改: 2026-06-18 │ ││
│  │  ├────────────────────────┤  │  │ 状态: ✅ 已启用      │ ││
│  │  │ ● RSI 超买超卖         │  │  │                      │ ││
│  │  │   v2 · 2026-06-15     │  │  │ [编辑代码] [回测]     │ ││
│  │  │   最近回测: ⚠ 运行中   │  │  │ [版本历史] [删除]    │ ││
│  │  ├────────────────────────┤  │  │                      │ ││
│  │  │ ● 布林带策略           │  │  │ 版本列表:            │ ││
│  │  │   v1 · 2026-06-10     │  │  │  v3 · 增加止损逻辑   │ ││
│  │  │   最近回测: ❌ 失败    │  │  │  v2 · 调整参数       │ ││
│  │  ├────────────────────────┤  │  │  v1 · 初始版本      │ ││
│  │  │ ...                   │  │  │                      │ ││
│  │  └────────────────────────┘  │  └──────────────────────┘ ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

**策略代码编辑器页面（点击"编辑代码"进入全屏编辑器）：**

```
┌──────────────────────────────────────────────────────────────┐
│  ← 返回      双均线趋势跟踪 v3    [保存] [保存为新版本] [回测]  │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────┐ ┌────────────────────────────┐│
│  │  代码编辑器 (Monaco Editor) │ │  策略配置 (右侧面板 280px)  ││
│  │                            │ │                            ││
│  │  def init(context):        │ │  回测参数                  ││
│  │      context.fast = 5      │ │  起始资金: [100,000]       ││
│  │      context.slow = 20     │ │  基准: [000300.XSHG  ▾]    ││
│  │      context.s1 = \        │ │  手续费: [0.0003]          ││
│  │        "000001.XSHE"       │ │  滑点: [0.01]              ││
│  │                            │ │                            ││
│  │  def handle_bar(ctx, bar): │ │  运行设置                  ││
│  │      fast_ma = ma(         │ │  频率: [日线 ▾]            ││
│  │        ctx.s1, ctx.fast)   │ │  开始: [2024-01-01]        ││
│  │      slow_ma = ma(         │ │  结束: [2024-12-31]        ││
│  │        ctx.s1, ctx.slow)   │ │                            ││
│  │      if cross_above(       │ │                            ││
│  │        fast_ma, slow_ma):  │ │                            ││
│  │          order_target_     │ │                            ││
│  │            percent(...)    │ │                            ││
│  │      ...                  │ │                            ││
│  └────────────────────────────┘ └────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  快速回测结果 (可折叠)                                    ││
│  │  年化收益: 32.5%  |  最大回撤: -12.3%  |  夏普: 1.85     ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

**技术选型说明：代码编辑器使用 Monaco Editor（VS Code 内核），通过 `monaco-editor` npm 包集成。**

#### 2.2.3 回测中心（Backtest Center）— 核心页面 ⚡

这是本次设计的核心页面，对标米筐回测的完整流程：**配置 → 运行 → 结果分析**。

**页面布局：左侧回测列表 + 右侧详情面板（类米筐布局）：**

```
┌──────────────────────────────────────────────────────────────┐
│  ⚡ 回测中心                              [+ 新建回测]         │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┐ ┌───────────────────────────┐│
│  │  回测列表 (320px)            │ │  回测详情 (右侧)          ││
│  │  搜索：[___] 状态：[全部▾]    │ │                           ││
│  │  ┌─────────────────────────┐ │ │  ┌─────────────────────┐ ││
│  │  │ ✅ 双均线 v3             │ │ │  │ 回测 #128            │ ││
│  │  │    2026-06-19 14:32     │ │ │  │ 策略: 双均线趋势 v3  │ ││
│  │  │    收益 +32.5% ⚡1.85    │ │ │  │ 时间: 2024-01-01 ~   │ ││
│  │  │    ──────────────────── │ │ │  │       2024-12-31     │ ││
│  │  │  ⚡ 双均线 v2             │ │ │  │ 状态: ✅ 已完成      │ ││
│  │  │    2026-06-19 14:30     │ │ │  │ 耗时: 12.3 秒        │ ││
│  │  │    运行中 ··· 67%       │ │ │  │                       │ ││
│  │  │    ──────────────────── │ │ │  │ [查看详情] [重新运行] │ ││
│  │  │  ❌ RSI v1               │ │ │  │ [删除] [导出报告]    │ ││
│  │  │    2026-06-19 13:15     │ │ │  └─────────────────────┘ ││
│  │  │    失败: 数据不足       │ │ │                           ││
│  │  │    ──────────────────── │ │ │  ┌─ 绩效摘要 ──────────┐ ││
│  │  │  ...                   │ │ │  │ 总收益    32.50%    │ ││
│  │  └─────────────────────────┘ │ │  │ 年化收益  28.30%    │ ││
│  └─────────────────────────────┘ │ │  │ 最大回撤  -12.30%   │ ││
│                                  │ │  │ 夏普比率  1.85      │ ││
│                                  │ │  │ 索提诺    2.41      │ ││
│                                  │ │  │ 胜率      58.3%     │ ││
│                                  │ │  │ 盈亏比    2.15      │ ││
│                                  │ │  │ 年化波动  15.2%     │ ││
│                                  │ │  │ Alpha     8.5%     │ ││
│                                  │ │  │ Beta      0.85     │ ││
│                                  │ │  │ 最终净值  1.3250    │ ││
│                                  │ │  └─────────────────────┘ ││
│                                  │ └───────────────────────────┘│
│  └─────────────────────────────┘                              │
│                                                              │
│  ============== 点击"查看详情"后的完整分析面板 ==============  │
│                                                              │
│  ┌─ Tab 导航 ──────────────────────────────────────────────┐ │
│  │  [📊 净值曲线] [📋 交易记录] [📈 持仓分析] [📉 风险分析]   │ │
│  │  [📊 收益分布] [🔄 归因分析] [📝 日志]                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                              │
│  -- Tab 1: 净值曲线 --                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  策略 vs 基准 累计收益率曲线 (ECharts)                     ││
│  │   ▓▓▓▓ 策略 (+32.5%)                                     ││
│  │   ░░░░ 基准 沪深300 (+8.2%)                               ││
│  │   ──── 超额收益 (+24.3%)                                  ││
│  │                                                          ││
│  │  ════════════════════════════════════════════════════     ││
│  │  ▏         ▏          ▏         ▏          ▏             ││
│  │  2024-01   2024-03    2024-06   2024-09    2024-12        ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  -- Tab 2: 交易记录 --                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  共 47 笔交易  买入:23  卖出:24                           ││
│  │  日期      股票         方向  价格    数量    盈亏    原因  ││
│  │  2024-01-15 000001.SZ   买入  12.50   8000    -     信号  ││
│  │  2024-03-22 000001.SZ   卖出  15.20   8000   +21,600 止损 ││
│  │  2024-04-10 000002.SZ   买入  8.30   12000    -     信号  ││
│  │  ...                                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  -- Tab 3: 持仓分析 --                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  持仓集中度饼图 (ECharts)    行业分布柱状图 (ECharts)      ││
│  │   [pie chart]                [bar chart]                  ││
│  │                                                          ││
│  │  股票        总交易次数  盈利次数  胜率    累计盈亏         ││
│  │  000001.SZ   12         8        66.7%   +45,200         ││
│  │  000002.SZ   8          5        62.5%   +18,900         ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  -- Tab 4: 风险分析 --                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  回撤曲线 (ECharts)                                       ││
│  │  ▓▓▓▓▓▓▓░░░░░░▓▓▓▓▓░░░░░░░▓▓▓▓▓▓▓▓▓                     ││
│  │  最大回撤: -12.3% (2024-06-15 ~ 2024-08-22)              ││
│  │                                                          ││
│  │  风险指标表格                                             ││
│  │  年化波动  15.2%     VaR(95%)   -2.1%                    ││
│  │  下行波动  10.8%     CVaR(95%)  -3.5%                    ││
│  │  最大回撤  -12.3%    最大回撤恢复期  45天                  ││
│  │  Calmar    2.30      信息比率   1.42                     ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  -- Tab 5: 收益分布 --                                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  日收益分布直方图 (ECharts)   周收益热力图 (ECharts)       ││
│  │  [histogram]                 [calendar heatmap]           ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  -- Tab 6: 归因分析 --                                       ││
│  ┌──────────────────────────────────────────────────────────┐│
│  │  Brinson 归因 / 因子归因 (ECharts waterfall)              ││
│  │  行业配置贡献  +5.2%                                      ││
│  │  个股选择贡献  +18.2%                                     ││
│  │  交互效应      +2.1%                                      ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  -- Tab 7: 日志 --                                           ││
│  ┌──────────────────────────────────────────────────────────┐│
│  │  📄 logs/double_ma/128.log              [📥 下载] [⬇ 底部] ││
│  │  ─────────────────────────────────────────────────────── ││
│  │  14:32:00.123 │ [INFO ] QT Backtest Engine Starting      ││
│  │  14:32:00.450 │ [INFO ] Loaded 5,286 instruments         ││
│  │  14:32:00.825 │ [INFO ] [2024-01-15] SIGNAL: 金叉买入     ││
│  │  14:32:01.125 │ [WARN ] [2024-03-22] 死叉卖出             ││
│  │  14:32:02.345 │ [WARN ] [2024-05-05] STOP_LOSS triggered ││
│  │  14:32:05.600 │ [INFO ] Backtest #128 completed in 12.3s ││
│  │  ─────────────────────────────────────────────────────── ││
│  │  日志目录规则：logs/{strategy_key}/{backtest_id}.log       ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

**新建回测对话框：**

```
┌──────────────────────────────────────────────────┐
│  新建回测                                    [✕]  │
├──────────────────────────────────────────────────┤
│  策略：[双均线趋势跟踪 v3 ▾]                      │
│  起始日期：[2024-01-01]  结束日期：[2024-12-31]   │
│  起始资金：[100,000    ]  基准：[沪深300 ▾]       │
│  频率：[日线 ▾]  (1d / 1m / tick)                │
│  手续费：[0.0003]  滑点：[0.01]                  │
│  分红再投资：[✓]                                  │
│                                                  │
│  [取消]  [开始回测]                               │
└──────────────────────────────────────────────────┘
```

**回测运行中（实时进度）：**

```
┌──────────────────────────────────────────────────┐
│  ⚡ 回测运行中...                                 │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  76%                    │
│  运行至 2024-09-15，已处理 184/242 个交易日        │
│  当前收益 +28.5%（实时预览）                      │
│  [取消]                                          │
└──────────────────────────────────────────────────┘
```

#### 2.2.4 数据中心（Data Center）

```
┌──────────────────────────────────────────────────────────────┐
│  📈 数据中心                                                 │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ A股总数   │ │ 今日更新   │ │ 数据起始   │ │ 数据完整度 │        │
│  │  5,286   │ │  5,286   │ │  2010-01  │ │  99.8%    │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  数据源管理                                               ││
│  │  ┌──────────┬────────┬──────────┬────────┬──────────────┐││
│  │  │ 数据源    │ 状态     │ 最新数据   │ 频率    │ 操作          │││
│  │  ├──────────┼────────┼──────────┼────────┼──────────────┤││
│  │  │ Tushare  │ ✅ 正常 │ 2026-06-19│ 日     │ [同步] [配置] │││
│  │  │ AKShare  │ ✅ 正常 │ 2026-06-19│ 日     │ [同步] [配置] │││
│  │  └──────────┴────────┴──────────┴────────┴──────────────┘││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  数据下载任务 (Task Queue)                                ││
│  │  ID   类型      状态    进度    详情                      ││
│  │  T128 daily     完成    100%    2026-06-19 数据下载完成   ││
│  │  T127 weekly    完成    100%    周线数据聚合完成          ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

#### 2.2.5 因子研究（Factor Lab）— 二期重点，简略设计

```
┌──────────────────────────────────────────────────────────────┐
│  🔬 因子研究                            [+ 新建因子]         │
├──────────────────────────────────────────────────────────────┤
│  因子列表 (左侧)          │  因子详情 (右侧)                  │
│  ┌─────────────────────┐ │  ┌────────────────────────────┐  │
│  │ 📊 动量因子          │ │  │ IC 曲线 (ECharts)          │  │
│  │    IC均值: 0.045    │ │  │ ▓▓▓▓▓░░░▓▓░▓▓░░           │  │
│  │    IR: 0.82         │ │  │                            │  │
│  │ 📊 价值因子          │ │  │ 分层收益 (ECharts bar)      │  │
│  │    IC均值: 0.032    │ │  │ Q1 ▓▓▓▓  Q5 ░░░░          │  │
│  │ ...                │ │  │                            │  │
│  └─────────────────────┘ │  └────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、数据库表结构设计

数据库：MySQL `qt_dev`（在现有 MySQL 地址上新建库）

### 3.1 表结构总览

```
qt_dev
├── users                    用户表（一期改造）
├── stock_basic              股票基础信息（一期改造）
├── stock_daily              日线行情（一期改造）
├── strategy                 策略主表（新设计）
├── strategy_version         策略版本表（新设计）
├── backtest_job             回测任务表（新设计）
├── backtest_nav             回测净值表（新设计）
├── backtest_trade           回测交易记录表（新设计）
├── backtest_position        回测定点持仓表（新设计）
├── backtest_daily_metrics   回测日度指标表（新设计）
├── backtest_risk_metrics    回测风险指标表（新设计）
├── data_source              数据源配置表（新设计）
├── data_sync_log            数据同步日志表（新设计）
├── factor_def               因子定义表（一期改造）
├── factor_value             因子值表（一期改造）
├── task_job                 任务队列表（一期改造）
└── task_step                任务步骤表（一期改造）
```

### 3.2 详细字段设计

#### 3.2.1 users — 用户表

```sql
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(64)  NOT NULL UNIQUE COMMENT '用户名',
    password    VARCHAR(256) NOT NULL COMMENT '密码（bcrypt hash）',
    email       VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    role        VARCHAR(32)  DEFAULT 'user' COMMENT '角色：admin / user',
    status      VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active / disabled',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

#### 3.2.2 stock_basic — 股票基础信息

```sql
-- 对标 rqalpha instrument，存储所有可交易标的
CREATE TABLE stock_basic (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ts_code         VARCHAR(16)  NOT NULL UNIQUE COMMENT '代码（000001.SZ）',
    symbol          VARCHAR(8)   NOT NULL COMMENT '简写（000001）',
    name            VARCHAR(64)  NOT NULL COMMENT '名称（平安银行）',
    area            VARCHAR(32)  DEFAULT NULL COMMENT '地区（深圳）',
    industry        VARCHAR(64)  DEFAULT NULL COMMENT '行业（银行）',
    market          VARCHAR(16)  NOT NULL COMMENT '市场（SZ/SE/HK）',
    list_date       DATE         DEFAULT NULL COMMENT '上市日期',
    delist_date     DATE         DEFAULT NULL COMMENT '退市日期',
    exchange        VARCHAR(16)  DEFAULT 'SZSE' COMMENT '交易所（SZSE/SSE）',
    board_type      VARCHAR(32)  DEFAULT 'MainBoard' COMMENT '板块（MainBoard/GEM/KSH）',
    status          VARCHAR(16)  DEFAULT 'active' COMMENT '状态',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ts_code (ts_code),
    INDEX idx_market (market),
    INDEX idx_industry (industry),
    INDEX idx_board_type (board_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基础信息';
```

#### 3.2.3 stock_daily — 日线行情

```sql
CREATE TABLE stock_daily (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code     VARCHAR(16)  NOT NULL COMMENT '股票代码',
    trade_date  DATE         NOT NULL COMMENT '交易日期',
    open        DOUBLE       DEFAULT NULL,
    high        DOUBLE       DEFAULT NULL,
    low         DOUBLE       DEFAULT NULL,
    close       DOUBLE       DEFAULT NULL,
    pre_close   DOUBLE       DEFAULT NULL,
    change_pct  DOUBLE       DEFAULT NULL COMMENT '涨跌幅(%)',
    vol         DOUBLE       DEFAULT NULL COMMENT '成交量（手）',
    amount      DOUBLE       DEFAULT NULL COMMENT '成交额（千元）',
    turnover    DOUBLE       DEFAULT NULL COMMENT '换手率(%)',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code),
    INDEX idx_code_date (ts_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A股日线行情';
```

#### 3.2.4 strategy — 策略主表

```sql
CREATE TABLE strategy (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL COMMENT '创建用户',
    name            VARCHAR(128) NOT NULL COMMENT '策略名称',
    description     TEXT         DEFAULT NULL COMMENT '策略描述',
    strategy_type   VARCHAR(32)  DEFAULT 'stock' COMMENT '策略类型：stock / future / index',
    status          VARCHAR(16)  DEFAULT 'draft' COMMENT '状态：draft / active / archived',
    latest_version  INT          DEFAULT 0 COMMENT '最新版本号',
    default_config  JSON         DEFAULT NULL COMMENT '默认回测配置（JSON）',
    tags            JSON         DEFAULT NULL COMMENT '标签（JSON数组）',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_type (strategy_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略主表';
```

**default_config JSON 示例：**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "benchmark": "000300.XSHG",
  "frequency": "1d",
  "commission": 0.0003,
  "slippage": 0.01,
  "accounts": {"stock": 100000}
}
```

#### 3.2.5 strategy_version — 策略版本表

```sql
CREATE TABLE strategy_version (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id     INT          NOT NULL COMMENT '策略ID',
    version         INT          NOT NULL COMMENT '版本号（递增）',
    source_code     MEDIUMTEXT   NOT NULL COMMENT '策略源码（Python）',
    config          JSON         DEFAULT NULL COMMENT '该版本的配置快照',
    change_log      TEXT         DEFAULT NULL COMMENT '变更说明',
    status          VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active / archived',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_strategy_version (strategy_id, version),
    INDEX idx_strategy (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略版本表';
```

#### 3.2.6 backtest_job — 回测任务表

```sql
CREATE TABLE backtest_job (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT          NOT NULL COMMENT '用户ID',
    strategy_id         INT          NOT NULL COMMENT '策略ID',
    strategy_version    INT          NOT NULL COMMENT '策略版本号',
    strategy_name       VARCHAR(128) DEFAULT NULL COMMENT '策略名称（冗余，便于查询）',
    status              VARCHAR(16)  DEFAULT 'pending' COMMENT '状态: pending / running / completed / failed / cancelled',
    config              JSON         NOT NULL COMMENT '回测配置快照（完整参数）',
    -- 进度信息
    progress            DOUBLE       DEFAULT 0 COMMENT '进度 0-100',
    current_date        DATE         DEFAULT NULL COMMENT '当前运行到的日期',
    -- 结果摘要
    total_return        DOUBLE       DEFAULT NULL COMMENT '总收益率',
    annualized_return   DOUBLE       DEFAULT NULL COMMENT '年化收益率',
    max_drawdown        DOUBLE       DEFAULT NULL COMMENT '最大回撤',
    sharpe_ratio        DOUBLE       DEFAULT NULL COMMENT '夏普比率',
    sortino_ratio       DOUBLE       DEFAULT NULL COMMENT '索提诺比率',
    win_rate            DOUBLE       DEFAULT NULL COMMENT '胜率',
    profit_loss_ratio   DOUBLE       DEFAULT NULL COMMENT '盈亏比',
    annual_volatility   DOUBLE       DEFAULT NULL COMMENT '年化波动率',
    alpha               DOUBLE       DEFAULT NULL COMMENT 'Alpha',
    beta                DOUBLE       DEFAULT NULL COMMENT 'Beta',
    final_value         DOUBLE       DEFAULT NULL COMMENT '最终资产总值',
    total_trades        INT          DEFAULT 0 COMMENT '总交易笔数',
    benchmark_return    DOUBLE       DEFAULT NULL COMMENT '基准收益率',
    excess_return       DOUBLE       DEFAULT NULL COMMENT '超额收益',
    -- 运行时信息
    start_time          DATETIME     DEFAULT NULL COMMENT '开始时间',
    end_time            DATETIME     DEFAULT NULL COMMENT '结束时间',
    duration_ms         INT          DEFAULT NULL COMMENT '耗时（毫秒）',
    error_message       TEXT         DEFAULT NULL COMMENT '错误信息（失败时）',
    -- 结果数据路径
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_strategy (strategy_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测任务表';
```

#### 3.2.7 backtest_nav — 回测净值曲线

```sql
-- 用于绘制净值曲线，按日存储
CREATE TABLE backtest_nav (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id     INT      NOT NULL COMMENT '回测任务ID',
    trade_date      DATE     NOT NULL COMMENT '交易日期',
    unit_net_value  DOUBLE   NOT NULL COMMENT '单位净值',
    daily_return    DOUBLE   DEFAULT NULL COMMENT '日收益率',
    cumulative_return DOUBLE DEFAULT NULL COMMENT '累计收益率',
    benchmark_nav   DOUBLE   DEFAULT NULL COMMENT '基准净值（对齐后）',
    excess_return   DOUBLE   DEFAULT NULL COMMENT '超额收益',
    INDEX idx_backtest (backtest_id),
    UNIQUE KEY uk_bt_date (backtest_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测净值曲线';
```

#### 3.2.8 backtest_trade — 回测交易记录

```sql
-- 每笔交易一条记录（买入/卖出匹配后的一条完整交易）
CREATE TABLE backtest_trade (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id     INT          NOT NULL COMMENT '回测任务ID',
    ts_code         VARCHAR(16)  NOT NULL COMMENT '股票代码',
    symbol          VARCHAR(8)   DEFAULT NULL COMMENT '股票简称',
    buy_date        DATE         NOT NULL COMMENT '买入日期',
    sell_date       DATE         DEFAULT NULL COMMENT '卖出日期',
    buy_price       DOUBLE       NOT NULL COMMENT '买入价',
    sell_price      DOUBLE       DEFAULT NULL COMMENT '卖出价',
    quantity        INT          NOT NULL COMMENT '交易数量（股）',
    buy_amount      DOUBLE       NOT NULL COMMENT '买入金额',
    sell_amount     DOUBLE       DEFAULT NULL COMMENT '卖出金额',
    pnl             DOUBLE       DEFAULT NULL COMMENT '盈亏金额',
    pnl_pct         DOUBLE       DEFAULT NULL COMMENT '盈亏百分比',
    holding_days    INT          DEFAULT NULL COMMENT '持仓天数',
    sell_reason     VARCHAR(64)  DEFAULT NULL COMMENT '卖出原因（signal/stop_loss/stop_profit/end）',
    INDEX idx_backtest (backtest_id),
    INDEX idx_bt_code (backtest_id, ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测交易记录';
```

#### 3.2.9 backtest_position — 回测定点持仓快照

```sql
-- 按日存储每日持仓明细（用于持仓分析）
CREATE TABLE backtest_position (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id     INT          NOT NULL COMMENT '回测任务ID',
    trade_date      DATE         NOT NULL COMMENT '交易日期',
    ts_code         VARCHAR(16)  NOT NULL COMMENT '股票代码',
    symbol          VARCHAR(8)   DEFAULT NULL COMMENT '股票简称',
    quantity        INT          NOT NULL COMMENT '持仓数量',
    market_value    DOUBLE       NOT NULL COMMENT '市值',
    weight          DOUBLE       NOT NULL COMMENT '权重(%)',
    cost            DOUBLE       NOT NULL COMMENT '成本价',
    current_price   DOUBLE       NOT NULL COMMENT '当前价',
    pnl             DOUBLE       DEFAULT NULL COMMENT '浮动盈亏',
    pnl_pct         DOUBLE       DEFAULT NULL COMMENT '浮动盈亏百分比',
    INDEX idx_backtest (backtest_id),
    INDEX idx_bt_date (backtest_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测持仓快照（按日）';
```

#### 3.2.10 backtest_daily_metrics — 回测日度指标

```sql
-- 按日存储风控指标（回撤、VaR等）
CREATE TABLE backtest_daily_metrics (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id     INT     NOT NULL COMMENT '回测任务ID',
    trade_date      DATE    NOT NULL COMMENT '交易日期',
    daily_return    DOUBLE  DEFAULT NULL COMMENT '当日收益率',
    cumulative_return DOUBLE DEFAULT NULL COMMENT '累计收益率',
    drawdown        DOUBLE  DEFAULT NULL COMMENT '当日回撤(%)',
    portfolio_value DOUBLE  DEFAULT NULL COMMENT '当日组合总值',
    cash            DOUBLE  DEFAULT NULL COMMENT '当日现金',
    leverage        DOUBLE  DEFAULT NULL COMMENT '当日杠杆',
    turnover        DOUBLE  DEFAULT NULL COMMENT '当日换手率',
    INDEX idx_backtest (backtest_id),
    UNIQUE KEY uk_bt_date (backtest_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测日度指标';
```

#### 3.2.11 backtest_risk_metrics — 回测风险指标

```sql
-- 存储回测完成后计算的整体风险指标
CREATE TABLE backtest_risk_metrics (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    backtest_id         INT     NOT NULL UNIQUE COMMENT '回测任务ID',
    max_drawdown        DOUBLE  DEFAULT NULL COMMENT '最大回撤(%)',
    max_drawdown_start  DATE    DEFAULT NULL COMMENT '最大回撤开始日期',
    max_drawdown_end    DATE    DEFAULT NULL COMMENT '最大回撤结束日期',
    max_drawdown_recovery DATE  DEFAULT NULL COMMENT '最大回撤恢复日期',
    max_drawdown_days   INT     DEFAULT NULL COMMENT '最大回撤持续天数',
    annual_volatility   DOUBLE  DEFAULT NULL COMMENT '年化波动率',
    downside_volatility DOUBLE  DEFAULT NULL COMMENT '下行波动率',
    var_95              DOUBLE  DEFAULT NULL COMMENT '95% VaR（日）',
    cvar_95             DOUBLE  DEFAULT NULL COMMENT '95% CVaR（日）',
    calmar_ratio        DOUBLE  DEFAULT NULL COMMENT 'Calmar比率',
    information_ratio   DOUBLE  DEFAULT NULL COMMENT '信息比率',
    tracking_error      DOUBLE  DEFAULT NULL COMMENT '跟踪误差',
    avg_holding_days    DOUBLE  DEFAULT NULL COMMENT '平均持仓天数',
    max_consecutive_win INT     DEFAULT NULL COMMENT '最大连续盈利次数',
    max_consecutive_lose INT    DEFAULT NULL COMMENT '最大连续亏损次数',
    INDEX idx_backtest (backtest_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测风险指标';
```

#### 3.2.12 data_source — 数据源配置

```sql
CREATE TABLE data_source (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(32)  NOT NULL UNIQUE COMMENT '数据源名称（tushare/akshare/rqdata）',
    display_name VARCHAR(64) NOT NULL COMMENT '显示名称',
    status      VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active / disabled',
    config      JSON         DEFAULT NULL COMMENT '配置（token等）',
    priority    INT          DEFAULT 0 COMMENT '优先级（数字越大越优先）',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据源配置';
```

#### 3.2.13 data_sync_log — 数据同步日志

```sql
CREATE TABLE data_sync_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    source      VARCHAR(32)  NOT NULL COMMENT '数据源',
    data_type   VARCHAR(32)  NOT NULL COMMENT '数据类型（daily/weekly/monthly/stock_basic）',
    trade_date  DATE         DEFAULT NULL COMMENT '同步日期',
    status      VARCHAR(16)  DEFAULT 'pending' COMMENT '状态：pending / running / completed / failed',
    total_count INT          DEFAULT 0 COMMENT '总条数',
    success_count INT        DEFAULT 0 COMMENT '成功条数',
    fail_count  INT          DEFAULT 0 COMMENT '失败条数',
    error_msg   TEXT         DEFAULT NULL COMMENT '错误信息',
    started_at  DATETIME     DEFAULT NULL,
    finished_at DATETIME     DEFAULT NULL,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source),
    INDEX idx_date (trade_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据同步日志';
```

#### 3.2.14 factor_def / factor_value（一期改造已有，沿用）

```sql
CREATE TABLE factor_def (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    factor_code VARCHAR(64)  NOT NULL UNIQUE COMMENT '因子编码',
    factor_name VARCHAR(128) NOT NULL COMMENT '因子名称',
    category    VARCHAR(32)  DEFAULT NULL COMMENT '分类：动量/价值/质量/成长/波动/情绪',
    description TEXT         DEFAULT NULL COMMENT '因子描述',
    params      JSON         DEFAULT NULL COMMENT '因子参数',
    status      VARCHAR(16)  DEFAULT 'active',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子定义';

CREATE TABLE factor_value (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    factor_code VARCHAR(64)  NOT NULL COMMENT '因子编码',
    ts_code     VARCHAR(16)  NOT NULL COMMENT '股票代码',
    trade_date  DATE         NOT NULL COMMENT '交易日期',
    value       DOUBLE       DEFAULT NULL COMMENT '因子值',
    UNIQUE KEY uk_factor_code_date (factor_code, ts_code, trade_date),
    INDEX idx_code (ts_code),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子值';
```

#### 3.2.15 task_job / task_step（一期改造已有，沿用）

```sql
CREATE TABLE task_job (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    task_type   VARCHAR(32)  NOT NULL COMMENT '任务类型（data_sync/data_repair/backtest/factor_calc）',
    status      VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending / running / completed / failed / cancelled',
    params      JSON         DEFAULT NULL COMMENT '任务参数',
    priority    INT          DEFAULT 0,
    progress    DOUBLE       DEFAULT 0 COMMENT '进度 0-100',
    result      JSON         DEFAULT NULL COMMENT '执行结果',
    error_msg   TEXT         DEFAULT NULL,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    started_at  DATETIME     DEFAULT NULL,
    finished_at DATETIME     DEFAULT NULL,
    INDEX idx_status (status),
    INDEX idx_type (task_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务队列表';

CREATE TABLE task_step (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    job_id      INT          NOT NULL COMMENT '任务ID',
    step_name   VARCHAR(128) NOT NULL COMMENT '步骤名称',
    status      VARCHAR(16)  DEFAULT 'pending',
    started_at  DATETIME     DEFAULT NULL,
    finished_at DATETIME     DEFAULT NULL,
    error_msg   TEXT         DEFAULT NULL,
    INDEX idx_job (job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务步骤表';
```

### 3.3 ER 关系图

```
users 1──N strategy
strategy 1──N strategy_version
strategy 1──N backtest_job
backtest_job 1──N backtest_nav
backtest_job 1──N backtest_trade
backtest_job 1──N backtest_position
backtest_job 1──N backtest_daily_metrics
backtest_job 1──1 backtest_risk_metrics
stock_basic 1──N stock_daily
stock_basic 1──N factor_value
factor_def 1──N factor_value
```

---

## 四、API 接口设计

### 4.1 接口总览（RESTful）

```
Base URL: /api

认证模块 (Auth)
  POST   /api/auth/login              登录
  POST   /api/auth/register           注册
  GET    /api/auth/me                 当前用户信息
  POST   /api/auth/change-password    修改密码

策略管理 (Strategies)
  GET    /api/strategies              策略列表（分页+筛选）
  POST   /api/strategies              创建策略
  GET    /api/strategies/:id          策略详情
  PUT    /api/strategies/:id          更新策略信息
  PATCH  /api/strategies/:id/status   修改策略状态
  DELETE /api/strategies/:id          删除策略
  # 版本
  GET    /api/strategies/:id/versions             版本列表
  POST   /api/strategies/:id/versions             创建版本（保存代码）
  GET    /api/strategies/:id/versions/:version    版本详情（含源码）
  # 快速回测
  POST   /api/strategies/:id/quick-test           快速回测（轻量级实时返回）

回测中心 (Backtests) ★ 核心
  POST   /api/backtests               创建并启动回测
  GET    /api/backtests               回测列表（分页+筛选）
  GET    /api/backtests/:id           回测详情（含摘要指标）
  POST   /api/backtests/:id/cancel    取消运行中的回测
  DELETE /api/backtests/:id           删除回测及关联数据
  # 回测结果分析
  GET    /api/backtests/:id/nav        净值曲线数据
  GET    /api/backtests/:id/trades     交易记录（分页）
  GET    /api/backtests/:id/positions  持仓快照（分页）
  GET    /api/backtests/:id/daily-metrics 日度指标
  GET    /api/backtests/:id/risk-metrics  风险指标详情
  GET    /api/backtests/:id/logs        回测日志（支持 tail/stream）
  GET    /api/backtests/:id/report     回测报告（聚合所有数据）
  # 实时进度
  WS     /ws/backtest/:id              WebSocket: 回测实时进度

数据中心 (Data)
  GET    /api/data/stocks              股票列表（分页）
  GET    /api/data/stocks/:code        股票详情
  GET    /api/data/stocks/:code/daily  日线数据
  GET    /api/data/sources             数据源列表
  POST   /api/data/sync                触发数据同步
  GET    /api/data/sync-logs           同步日志
  GET    /api/data/overview            数据概览统计

因子研究 (Factors) - 二期重点，一期基本 CRUD
  GET    /api/factors                  因子列表
  POST   /api/factors                  注册因子
  GET    /api/factors/:code            因子详情
  POST   /api/factors/analyze          因子分析
  GET    /api/factors/:code/ic         IC 时间序列
  GET    /api/factors/:code/group-return 分层收益

任务队列 (Tasks)
  GET    /api/tasks                    任务列表
  GET    /api/tasks/:id                任务详情
  POST   /api/tasks/:id/cancel         取消任务
  POST   /api/tasks/:id/retry          重试任务

组合管理 (Portfolio) - 三期
  GET    /api/portfolio                组合列表
  POST   /api/portfolio                创建组合
  GET    /api/portfolio/:id/nav        组合净值
  GET    /api/portfolio/:id/positions  组合持仓
  GET    /api/portfolio/:id/risk       组合风险

系统 (System)
  GET    /api/health                   健康检查
  GET    /api/system/info              rqalpha版本、数据状态、Worker状态
```

### 4.2 核心接口详细设计

#### 4.2.1 策略管理 API

**POST /api/strategies — 创建策略**

```json
// Request
{
  "name": "双均线趋势跟踪",
  "description": "基于快速均线和慢速均线交叉生成买卖信号",
  "strategy_type": "stock",
  "default_config": {
    "initial_capital": 100000,
    "benchmark": "000300.XSHG",
    "frequency": "1d",
    "commission": 0.0003
  }
}

// Response 201
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "双均线趋势跟踪",
    "status": "draft",
    "latest_version": 0,
    "created_at": "2026-06-19T14:30:00Z"
  }
}
```

**POST /api/strategies/:id/versions — 创建策略版本（保存代码）**

```json
// Request
{
  "source_code": "# 策略代码\n\ndef init(context):\n    ...\n\ndef handle_bar(context, bar_dict):\n    ...",
  "change_log": "初始版本：实现双均线交叉策略"
}

// Response 201
{
  "code": 0,
  "data": {
    "version": 1,
    "strategy_id": 1,
    "status": "active",
    "created_at": "2026-06-19T14:35:00Z"
  }
}
```

**GET /api/strategies — 策略列表**

```
GET /api/strategies?page=1&page_size=20&status=active&keyword=均线

Response 200:
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "双均线趋势跟踪",
        "strategy_type": "stock",
        "status": "active",
        "latest_version": 3,
        "last_backtest_status": "completed",
        "last_backtest_return": 0.325,
        "updated_at": "2026-06-18T10:00:00Z"
      }
    ],
    "total": 24,
    "page": 1,
    "page_size": 20
  }
}
```

#### 4.2.2 回测中心 API ★

**POST /api/backtests — 创建并启动回测**

```json
// Request
{
  "strategy_id": 1,
  "version": 3,
  "config": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000,
    "benchmark": "000300.XSHG",
    "frequency": "1d",
    "commission": 0.0003,
    "slippage": 0.01
  }
}

// Response 202 (Accepted, 异步执行)
{
  "code": 0,
  "data": {
    "id": 128,
    "status": "pending",
    "message": "回测任务已创建，正在排队..."
  }
}
```

**GET /api/backtests — 回测列表**

```
GET /api/backtests?page=1&page_size=20&strategy_id=1&status=completed

Response 200:
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 128,
        "strategy_id": 1,
        "strategy_name": "双均线趋势跟踪",
        "strategy_version": 3,
        "status": "completed",
        "total_return": 0.325,
        "annualized_return": 0.283,
        "max_drawdown": -0.123,
        "sharpe_ratio": 1.85,
        "duration_ms": 12300,
        "created_at": "2026-06-19T14:32:00Z"
      }
    ],
    "total": 128,
    "page": 1,
    "page_size": 20
  }
}
```

**GET /api/backtests/:id — 回测详情（摘要指标）**

```json
// Response 200
{
  "code": 0,
  "data": {
    "id": 128,
    "strategy_id": 1,
    "strategy_name": "双均线趋势跟踪",
    "strategy_version": 3,
    "status": "completed",
    "config": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "initial_capital": 100000,
      "benchmark": "000300.XSHG",
      "frequency": "1d"
    },
    "summary": {
      "total_return": 0.325,
      "annualized_return": 0.283,
      "max_drawdown": -0.123,
      "sharpe_ratio": 1.85,
      "sortino_ratio": 2.41,
      "win_rate": 0.583,
      "profit_loss_ratio": 2.15,
      "annual_volatility": 0.152,
      "alpha": 0.085,
      "beta": 0.85,
      "final_value": 132500.00,
      "total_trades": 47,
      "benchmark_return": 0.082,
      "excess_return": 0.243
    },
    "timing": {
      "start_time": "2026-06-19T14:32:00Z",
      "end_time": "2026-06-19T14:32:12Z",
      "duration_ms": 12300
    },
    "created_at": "2026-06-19T14:32:00Z"
  }
}
```

**GET /api/backtests/:id/nav — 净值曲线**

```
GET /api/backtests/:id/nav?format=full   # full: 返回全部点 / compact: 采样后返回

Response 200:
{
  "code": 0,
  "data": {
    "dates": ["2024-01-02", "2024-01-03", ...],
    "nav": [1.0, 1.002, ...],
    "benchmark_nav": [1.0, 0.998, ...],
    "excess_return": [0.0, 0.004, ...],
    "drawdown": [0.0, 0.0, -0.005, ...]
  }
}
```

**GET /api/backtests/:id/trades — 交易记录**

```
GET /api/backtests/:id/trades?page=1&page_size=50&ts_code=000001.SZ

Response 200:
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1001,
        "ts_code": "000001.SZ",
        "symbol": "平安银行",
        "buy_date": "2024-01-15",
        "sell_date": "2024-03-22",
        "buy_price": 12.50,
        "sell_price": 15.20,
        "quantity": 8000,
        "pnl": 21600.00,
        "pnl_pct": 0.216,
        "holding_days": 67,
        "sell_reason": "signal"
      }
    ],
    "total": 47,
    "page": 1,
    "page_size": 50,
    "summary": {
      "total_trades": 47,
      "win_trades": 28,
      "lose_trades": 19,
      "avg_profit": 4520.00,
      "avg_loss": -2150.00
    }
  }
}
```

**GET /api/backtests/:id/risk-metrics — 风险指标**

```json
// Response 200
{
  "code": 0,
  "data": {
    "max_drawdown": -0.123,
    "max_drawdown_start": "2024-06-15",
    "max_drawdown_end": "2024-08-22",
    "max_drawdown_recovery": "2024-10-05",
    "max_drawdown_days": 112,
    "annual_volatility": 0.152,
    "downside_volatility": 0.108,
    "var_95": -0.021,
    "cvar_95": -0.035,
    "calmar_ratio": 2.30,
    "information_ratio": 1.42,
    "tracking_error": 0.065,
    "avg_holding_days": 45.3,
    "max_consecutive_win": 8,
    "max_consecutive_lose": 4
  }
}
```

**GET /api/backtests/:id/logs — 回测日志**

日志文件按 `logs/{strategy_key}/{backtest_id}.log` 存储，支持三种读取模式：

```
GET /api/backtests/:id/logs?mode=full          # 返回完整日志
GET /api/backtests/:id/logs?mode=tail&lines=100 # 返回最后 N 行
GET /api/backtests/:id/logs?mode=stream        # SSE 流式推送（回测进行中时使用）

Response 200 (full/tail):
{
  "code": 0,
  "data": {
    "log_path": "logs/double_ma/128.log",
    "size_bytes": 8452,
    "lines": [
      "2026-06-19 14:32:00.123 │ [INFO ] QT Backtest Engine Starting",
      "2026-06-19 14:32:00.450 │ [INFO ] Loaded 5,286 instruments",
      "2026-06-19 14:32:00.825 │ [INFO ] [2024-01-15] SIGNAL: 金叉买入",
      "..."
    ]
  }
}
```

**GET /api/backtests/:id/report — 完整报告（聚合所有数据）**

```
GET /api/backtests/:id/report

Response 200:
{
  "code": 0,
  "data": {
    "summary": { ... },        // 摘要指标
    "nav": { ... },            // 净值曲线（采样到约300个点）
    "risk": { ... },           // 风险指标
    "trades_summary": { ... }, // 交易摘要
    "positions_summary": { ... } // 持仓统计摘要
  }
}
```

**WebSocket: /ws/backtest/:id — 回测实时进度**

```
// Server → Client events:

// 1. 进度更新
{
  "event": "backtest_progress",
  "data": {
    "backtest_id": 128,
    "progress": 67.5,
    "current_date": "2024-08-15",
    "total_bars": 242,
    "completed_bars": 163,
    "elapsed_seconds": 8.5,
    "estimated_remaining_seconds": 4.1
  }
}

// 2. 回测完成
{
  "event": "backtest_completed",
  "data": {
    "backtest_id": 128,
    "total_return": 0.325,
    "sharpe_ratio": 1.85,
    "duration_ms": 12300
  }
}

// 3. 回测失败
{
  "event": "backtest_failed",
  "data": {
    "backtest_id": 128,
    "error": "KeyError: 'close' - 数据不足，2024-01-01 无行情"
  }
}
```

### 4.3 rqalpha 集成方案

参考 QTrade 的集成模式，设计 `BacktestEngine` 类：

```python
# backend/app/services/backtest_engine.py (伪代码设计)

class BacktestEngine:
    """
    rqalpha 回测引擎封装

    集成方式：
    1. CustomDataSource — 从 MySQL stock_daily 加载数据，适配 rqalpha 的 AbstractDataSource
    2. 使用 rqalpha.run_func() API，传入 init/handle_bar 函数
    3. 通过 sys_analyser mod 提取回测结果
    4. 注入进度回调，通过 WebSocket 推送给前端
    """

    def run(self, backtest_id: int, config: dict, source_code: str,
            strategy_key: str):
        """
        执行回测的主入口

        Args:
            backtest_id: 回测任务ID（用于写入数据库和推送进度）
            config: 回测配置（start_date, end_date, capital, benchmark, ...）
            source_code: 策略源码字符串
            strategy_key: 策略标识（用于日志目录拼接）

        流程：
        1. 创建 CustomDataSource(backtest_id, start_date, end_date)
        2. 构建 rqalpha config dict
        3. 设置日志文件：logs/{strategy_key}/{backtest_id}.log
        4. 动态执行 source_code 获取 init/handle_bar
        5. 调用 rqalpha.run_func() 执行回测
        6. 从 sys_analyser 提取结果
        7. 写入 backtest_nav / backtest_trade / backtest_position / backtest_risk_metrics
        8. 更新 backtest_job 状态和摘要指标
        """
        pass

    def _setup_logger(self, strategy_key: str, backtest_id: int):
        """
        配置回测日志

        日志目录规则：logs/{strategy_key}/{backtest_id}.log
        例如：logs/double_ma/128.log

        每个回测独立一个日志文件，记录：
        - 引擎初始化日志（加载数据源、mod、交易日历）
        - 每个 bar 的执行日志（信号、订单、成交）
        - 性能统计日志（耗时、进度）
        - 错误和异常日志
        """
        pass

    def _create_data_source(self, start_date, end_date):
        """
        创建自定义数据源，从 MySQL stock_daily 读取行情数据
        适配 rqalpha 的 Bar/Instrument 格式
        """
        pass

    def _extract_results(self, analyser_result):
        """
        从 rqalpha sys_analyser mod 的返回值中提取：
        - summary: 收益、回撤、夏普、胜率等
        - trades: 每笔交易详情
        - positions: 每日持仓
        - daily_nav: 每日净值
        - risk: 风险指标
        """
        pass

    def _progress_callback(self, current_date, bar_count, total_bars):
        """
        进度回调：更新 backtest_job.progress，通过 WebSocket 推送
        """
        pass
```

**CustomDataSource 设计要点（参考 QTrade data_adapter.py）：**

1. 继承 `rqalpha.data.base_data_source.BaseDataSource`
2. 重写 `get_bar()`、`history_bars()`、`get_instruments()`、`available_data_range()` 等方法
3. 从 MySQL `stock_daily` 表查询数据，转为 rqalpha 的 numpy 结构数组
4. Instrument 格式：`"000001.XSHE"` (深交所)、`"600000.XSHG"` (上交所)
5. 交易日历从 `stock_daily.trade_date` DISTINCT 获取

### 4.4 后端分层架构

```
api/routes/
  auth_routes.py        → AuthService
  strategy_routes.py     → StrategyService
  backtest_routes.py     → BacktestService
  data_routes.py         → DataService
  factor_routes.py       → FactorService
  task_routes.py         → TaskService
  system_routes.py       → (直接返回状态)

services/
  auth_service.py        → user_repo
  strategy_service.py    → strategy_repo, strategy_version_repo
  backtest_service.py    → backtest_repo, BacktestEngine, websocket
  data_service.py        → stock_repo, stock_daily_repo, data_source_repo
  factor_service.py      → factor_repo
  task_service.py        → task_repo

repositories/
  user_repo.py           → users 表
  strategy_repo.py       → strategy 表
  strategy_version_repo.py → strategy_version 表
  backtest_repo.py       → backtest_job/nav/trade/position/daily_metrics/risk_metrics 表
  stock_repo.py          → stock_basic 表
  stock_daily_repo.py    → stock_daily 表
  data_source_repo.py    → data_source / data_sync_log 表
  factor_repo.py         → factor_def / factor_value 表
  task_repo.py           → task_job / task_step 表

analysis/
  indicators.py          → 技术指标纯函数（供策略代码使用）
  risk_metrics.py        → 风险指标计算（夏普、VaR、最大回撤等）

core/
  config.py              → Settings (DB_NAME=qt_dev)
  database.py            → SQLAlchemy engine (QueuePool)
  security.py            → JWT + bcrypt
  response.py            → 统一响应格式
  websocket.py           → WebSocket 管理（Flask-SocketIO）
```

---

## 五、技术关键点

### 5.1 rqalpha 集成

| 关注点 | 方案 |
|--------|------|
| 数据适配 | 自定义 DataSource 继承 BaseDataSource，从 MySQL stock_daily 读取，避免 HDF5 依赖 |
| 策略执行 | `rqalpha.run_func(config, init=..., handle_bar=...)` 或 `rqalpha.run_code(config, source_code)`, 在独立线程中执行 |
| 进度推送 | 注入 `builtins._BT_PROGRESS_FN_` 回调，通过 Flask-SocketIO 推送到前端 |
| 结果提取 | 解析 `sys_analyser` mod 返回的 summary/trades/positions/daily_nav |
| 取消回测 | 线程不强制 kill，通过 `env.event_source` 提前中断循环 |

### 5.2 前端技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 代码编辑器 | Monaco Editor (`@monaco-editor/loader` + `monaco-editor`) | VS Code 内核，Python 语法高亮 + 智能提示 |
| 图表 | ECharts 6.x | K线、净值曲线、回撤曲线、收益分布 |
| WebSocket | `socket.io-client` | 回测实时进度推送 |
| IDE 布局 | 自研 SplitPane 或使用 `splitpanes` 库 | 策略列表 + 代码编辑器 + 回测面板 三栏布局 |

### 5.3 配置变更

```env
# .env 关键变更
DB_NAME=qt_dev          # ← 改为新库
DB_HOST=xxx             # ← 不变
DB_USER=xxx             # ← 不变
DB_PASSWORD=xxx         # ← 不变

# 密码加密升级
PASSWORD_HASH=bcrypt    # ← 从 MD5 升级为 bcrypt

# rqalpha 路径
RQALPHA_PATH=/Users/gxwang/QT/rqalpha
```

---

## 六、一期实施路线图

| 阶段 | 内容 | 预估工作量 |
|------|------|------------|
| Phase 0 | 创建 qt_dev 库，迁移表结构，配置变更 | 0.5天 |
| Phase 1 | 数据层：stock_basic + stock_daily 数据同步 | 1天 |
| Phase 2 | 策略管理：CRUD + 版本管理 + Monaco 编辑器 | 2天 |
| Phase 3 | 回测引擎：CustomDataSource + rqalpha 集成 | 2天 |
| Phase 4 | 回测中心 UI：配置 → 进度 → 结果分析（5个Tab） | 3天 |
| Phase 5 | WebSocket 实时进度 + 工作台仪表盘 | 1天 |
| Phase 6 | 测试 + 联调 + Bug修复 | 1天 |
| **合计** | | **~10.5天** |

---

## 七、待讨论问题

1. **策略代码安全性**：用户提交的 Python 策略代码如何在服务端安全执行？（沙箱？进程隔离？资源限制？）
2. **数据源选择**：是否继续使用 Tushare，还是同时支持 AKShare？是否考虑引入 RQData（米筐数据源）？
3. **回测并发**：允许多个回测同时运行吗？一个用户最多同时跑几个？
4. **前端主题**：沿用现有 Element Plus 浅色主题，还是参考 QTrade 的暗色主题？
5. **历史数据迁移**：`stock` 库的现有数据是否需要迁移到 `qt_dev`？

---

> 本文档为 V1 初版，请审阅后反馈修改意见。
