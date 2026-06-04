# P1-T2: 任务中心 — 前端页面

## 目标

创建任务中心前端页面，并重构现有侧边栏导航系统，从简单菜单切换升级为 Vue Router 路由系统，支持9个页面的导航。

## 前提

P1-T1 已完成（任务中心后端 API 可用）。

## 需要修改/创建的文件

### 1. frontend/src/views/TaskCenterView.vue（新建）

对应原型中的任务中心页面（`prototype/quant-prototype-v2.html` 第 571-574 行，id="tasks"）。

功能：
- 页面标题"任务中心"，描述"统一查看数据同步、策略运行、回测和通知任务。"
- 表格展示任务列表：任务名、类型、计划时间、最近运行、状态、耗时、操作
- 操作按钮：日志（查看步骤详情）
- "立即执行"按钮（创建手动任务）
- 状态用不同颜色标签显示（tag green/amber/red）
- 点击"日志"弹出抽屉/对话框展示 task_step 列表

API 调用：
- `GET /api/tasks?page=1&page_size=20` — 获取任务列表
- `GET /api/tasks/{id}` — 获取任务详情
- `POST /api/tasks/{id}/retry` — 重试任务
- `POST /api/tasks/{id}/cancel` — 取消任务

### 2. frontend/src/views/DashboardView.vue（新建）

对应原型总览页面（id="dashboard"），展示 KPI 卡片、策略收益曲线、今日信号排行、任务状态、系统提示。

全部数据目前使用 mock 数据填充，等待后续阶段接入真实 API。

### 3. frontend/src/views/DataCenterView.vue（新建）

对应原型数据中心页面（id="data"），先创建空白页面骨架：
- 页面标题"数据中心"和描述
- 过滤器区域（市场、数据类型、日期范围、股票代码）
- 数据完整率趋势图区域（占位）
- 后续 Phase 2 填充实际内容

### 4. frontend/src/views/FactorLabView.vue（新建）

空白页面骨架，对应原型因子实验室页面（id="factor"）。

### 5. frontend/src/views/StrategyWorkspaceView.vue（新建）

空白页面骨架，对应原型策略工作台页面（id="strategy"）。

### 6. frontend/src/views/BacktestCenterView.vue（新建）

空白页面骨架，对应原型回测中心页面（id="backtest"）。

### 7. frontend/src/views/StockSignalsView.vue（新建）

空白页面骨架，对应原型选股信号页面（id="signals"）。

### 8. frontend/src/views/PortfolioRiskView.vue（新建）

空白页面骨架，对应原型组合风控页面（id="portfolio"）。

### 9. frontend/src/views/SystemSettingsView.vue（新建）

空白页面骨架，对应原型系统设置页面（id="settings"）。

### 10. 修改 frontend/src/router/index.js

替换为完整的9页面路由配置：

```javascript
const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { 
    path: '/dashboard', 
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'dashboard-view' } },
      { path: 'overview', name: 'dashboard-view', component: DashboardView },
      { path: 'data', component: DataCenterView },
      { path: 'factors', component: FactorLabView },
      { path: 'strategies', component: StrategyWorkspaceView },
      { path: 'backtest', component: BacktestCenterView },
      { path: 'signals', component: StockSignalsView },
      { path: 'portfolio', component: PortfolioRiskView },
      { path: 'tasks', component: TaskCenterView },
      { path: 'settings', component: SystemSettingsView },
    ]
  },
]
```

### 11. 重写 frontend/src/views/MainLayout.vue

从简单菜单切换改为：
- 左侧导航栏包含9个菜单项（按原型顺序）：总览、数据中心、因子实验室、策略工作台、回测中心、选股信号、组合风控、任务中心、系统设置
- 使用 `<router-view>` 渲染子页面
- 菜单高亮跟随当前路由
- 顶部栏显示数据日期、用户名、退出按钮
- 保留修改密码对话框功能

### 12. frontend/src/views/StockList.vue、StockSelect.vue 等旧页面

保持不动，后续阶段再决定是否整合。可以通过路由保留访问 `/old/table` 等。

## 导航设计

对照原型 `prototype/quant-prototype-v2.html` 第 458-468 行的侧边栏：

```
⌂  总览      ›
▣  数据中心   ›
△  因子实验室  ›
◇  策略工作台  ›
◎  回测中心   ›
▤  选股信号   ›
♡  组合风控   ›
▧  任务中心   ›
⚙  系统设置   ›
```

## 现有代码参考

- `frontend/src/views/MainLayout.vue` — 现有布局组件，参考其结构
- `frontend/src/router/index.js` — 现有路由配置
- `frontend/src/store/index.js` — Vuex store
- `frontend/src/config/axios.js` — Axios 实例

## 自测步骤

1. 启动前端：`cd frontend && npm run serve`
2. 登录后能看到新的9菜单侧边栏
3. 点击各菜单能正确切换页面
4. 任务中心页面能调用后端 API 显示任务列表
5. 总览页面有 mock 数据展示

## 样式要求

- 使用 Element Plus 组件库（el-table, el-menu, el-button, el-tag, el-dialog 等）
- 配色参考原型 CSS 变量：
  - 主题色: #007f7a (teal)
  - 成功: #0f9f6e (green)
  - 危险: #d84a57 (red)
  - 警告: #d28a17 (amber)
  - 蓝色: #2764d9
- 页面布局紧凑，适合宽屏展示
