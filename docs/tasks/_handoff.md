# 当前任务: UI 原型差异修复 — 批次 4（最终）

## 执行者
OpenCode

## 任务
修复 FactorLabView.vue 和 TaskCenterView.vue 与原型之间的剩余差异。

## 参考原型
`d:/kproject/OpenSource/stock/prototype/quant-prototype-v2.html`

---

### 1. 修改 `frontend/src/views/FactorLabView.vue`

原型参考：第 516-529 行。

差异：
- 原型 page-head 有"分析"和"重置"按钮作为 toolbar；当前实现在 filter 卡片内部
- 原型 filters 行包含：因子 select / **市场 select（沪深A股/港股通）** / 日期范围 / **IC周期 select（20日/60日）** / 分组数 select
- 当前缺少"市场"和"IC周期"过滤器

改动：
1. 在 filterForm 中新增 `market` 和 `ic_period` 字段
2. 在 filter 行中插入两个新 el-form-item：
   - 市场：el-select，选项"沪深A股"/"港股通"，v-model="filterForm.market"
   - IC周期：el-select，选项"20日"/"60日"，v-model="filterForm.ic_period"
3. handleReset() 中重置这两个新字段
4. 无需实际 API 改动（后端已忽略这些过滤参数，mock 数据保底）

### 2. 修改 `frontend/src/views/TaskCenterView.vue`

原型参考：第 571-573 行。

差异：
- 原型 page-head 右侧有"立即执行"按钮（`<button class="btn primary">立即执行</button>`）
- 当前 page-header 只有标题和描述，没有按钮

改动：
1. 在 page-header 的标题右侧添加 el-button type="primary" @click="handleRunTaskNow"
2. 添加 handleRunTaskNow 方法：
   - 调用 `axios.post('/api/tasks/run-now')`
   - catch 保底：在 taskList 开头插入一条模拟运行中的任务
   - ElMessage.success('任务已开始执行')
3. 保持现有表格和日志抽屉不变

Mock 数据新增（在 handleRunTaskNow 的 catch 中使用）：
```javascript
const now = new Date()
const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
this.taskList.unshift({
  id: Date.now(),
  task_name: '手动任务',
  task_type: '策略',
  schedule: '立即',
  last_run_at: timeStr,
  status: 'running',
  duration: null
})
```

### 自测
```bash
cd frontend && NODE_OPTIONS="--max-old-space-size=6144" npx vue-cli-service build
```
不报错。
