<template>
  <div class="strategy-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <div class="panel-header">
        <span>策略列表</span>
        <el-button type="primary" size="small" @click="showCreateDialog">+ 新建</el-button>
      </div>
      <el-input v-model="keyword" placeholder="搜索策略..." size="small" clearable class="search-input" @input="loadList" />
      <div class="strategy-list">
        <div v-for="s in strategies" :key="s.id" class="strategy-item" :class="{ active: current?.id === s.id }" @click="selectStrategy(s)">
          <div class="item-title">
            <span>{{ s.name }}</span>
            <el-tag :type="s.status==='active'?'success':s.status==='draft'?'info':'warning'" size="small">{{ s.latest_version ? 'v'+s.latest_version : 'new' }}</el-tag>
          </div>
          <div class="item-meta">{{ s.strategy_type }} · {{ s.updated_at?.slice(0,10) }}</div>
          <div class="item-stats" v-if="s.last_backtest_return != null">
            <span :class="s.last_backtest_return>0?'green':'red'">{{ (s.last_backtest_return*100).toFixed(1) }}%</span>
            <span class="label">最近回测</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel" v-if="current">
      <div class="detail-header">
        <div>
          <h3>{{ current.name }}</h3>
          <span class="meta">{{ current.strategy_type }} · 版本 v{{ current.latest_version }} · {{ current.updated_at?.slice(0,10) }}</span>
        </div>
        <div class="btn-group">
          <el-button type="primary" size="small" @click="startEdit">✏️ 编辑代码</el-button>
          <el-button type="warning" size="small" @click="showBacktestDialog">⚡ 回测</el-button>
          <el-button size="small" @click="showVersions">📋 版本历史</el-button>
          <el-button type="danger" size="small" @click="handleDelete">🗑 删除</el-button>
        </div>
      </div>
      <CodeEditor ref="editorRef" v-model="code" :readOnly="!editing" :filename="current.strategy_key+'.py'" @save="saveCode" />
    </div>
    <div class="right-panel empty" v-else>
      <el-empty description="选择一个策略或新建策略" />
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="createVisible" title="新建策略" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" placeholder="策略名称" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.desc" type="textarea" placeholder="策略描述" /></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.type"><el-option label="股票" value="stock" /><el-option label="期货" value="future" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="createVisible=false">取消</el-button><el-button type="primary" @click="handleCreate">创建</el-button></template>
    </el-dialog>

    <!-- Version Dialog -->
    <el-dialog v-model="versionVisible" title="版本历史" width="600px">
      <el-table :data="versions" size="small">
        <el-table-column prop="version" label="版本" width="60" />
        <el-table-column prop="change_log" label="变更说明" />
        <el-table-column label="时间" width="150"><template #default="{row}">{{ row.created_at }}</template></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{row}">
            <el-button v-if="row.version !== current.latest_version" size="small" type="primary" @click="switchToVersion(row)">切换</el-button>
            <el-tag v-else type="success" size="small">当前</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- Backtest Dialog -->
    <el-dialog v-model="btDialogVisible" title="新建回测" width="520px">
      <div class="bt-strategy-info">
        <span>关联策略：<b>{{ current?.name }} v{{ current?.latest_version }}</b></span>
      </div>
      <el-form :model="btForm" label-width="80px" style="margin-top:12px">
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="起始日期"><el-date-picker v-model="btForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col><el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="btForm.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col></el-row>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="起始资金"><el-input-number v-model="btForm.initial_capital" :min="10000" style="width:100%" /></el-form-item></el-col><el-col :span="12"><el-form-item label="基准"><el-select v-model="btForm.benchmark" style="width:100%"><el-option label="无" value="" /><el-option label="沪深300" value="000300.XSHG" /><el-option label="中证500" value="000905.XSHG" /></el-select></el-form-item></el-col></el-row>
      </el-form>
      <template #footer><el-button @click="btDialogVisible=false">取消</el-button><el-button type="primary" @click="runBacktest">⚡ 开始回测</el-button></template>
    </el-dialog>
  </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'
import { mapState, mapActions } from 'vuex'
export default {
  name: 'StrategyResearch',
  components: { CodeEditor },
  data() {
    return {
      keyword: '', code: '', editing: false, current: null,
      createVisible: false, versionVisible: false, btDialogVisible: false,
      form: { name: '', desc: '', type: 'stock' },
      btForm: { start_date: '2024-01-01', end_date: '2024-12-31', initial_capital: 100000, benchmark: '000300.XSHG' },
      versions: []
    }
  },
  computed: { ...mapState('strategy', ['list', 'loading']), strategies() { return this.list } },
  methods: {
    ...mapActions('strategy', ['loadList', 'create', 'remove', 'loadVersions', 'saveVersion', 'loadVersionCode']),
    async loadListData() {
      await this.loadList({ keyword: this.keyword })
      if (this.strategies.length > 0 && !this.current) {
        this.selectStrategy(this.strategies[0])
      }
    },
    async selectStrategy(s) {
      this.current = s; this.editing = false
      const vers = await this.loadVersions(s.id)
      if (vers?.length) {
        const data = await this.loadVersionCode({ strategyId: s.id, version: vers[0].version })
        if (data) this.code = data.source_code || ''
      } else { this.code = '# 在此编写策略代码...\ndef init(context):\n    pass\n\ndef handle_bar(context, bar_dict):\n    pass\n' }
    },
    startEdit() { this.editing = true },
    async saveCode() {
      if (!this.current) return
      await this.saveVersion({ strategyId: this.current.id, sourceCode: this.code, changeLog: '更新代码' })
      this.editing = false; this.$message.success('代码已保存')
    },
    showCreateDialog() { this.form = { name: '', desc: '', type: 'stock' }; this.createVisible = true },
    async handleCreate() {
      if (!this.form.name) return this.$message.warning('请输入策略名称')
      const res = await this.create({ name: this.form.name, description: this.form.desc, strategy_type: this.form.type })
      if (res?.success) { this.createVisible = false; this.$message.success('策略已创建') }
    },
    async handleDelete() {
      if (!this.current) return
      try { await this.$confirm('确认删除该策略？', '提示', { type: 'warning' }); await this.remove(this.current.id); this.current = null; this.$message.success('已删除') }
      catch { /* user cancelled */ }
    },
    async showVersions() {
      if (!this.current) return
      const vers = await this.loadVersions(this.current.id)
      this.versions = (vers || []).map(v => ({ ...v, created_at: v.created_at?.slice(0, 16) || '' }))
      this.versionVisible = true
    },
    async switchToVersion(row) {
      const data = await this.loadVersionCode({ strategyId: this.current.id, version: row.version })
      if (data) {
        this.code = data.source_code || ''
        this.current.latest_version = row.version
        this.$message.success(`已切换到 v${row.version}`)
        this.versionVisible = false
      }
    },
    showBacktestDialog() { this.btDialogVisible = true },
    async runBacktest() {
      if (!this.current) return
      try {
        const res = await this.$store.dispatch('backtest/create', {
          strategy_id: this.current.id,
          version: this.current.latest_version,
          config: this.btForm
        })
        if (res?.success) {
          this.btDialogVisible = false
          this.$message.success('回测已创建')
          this.$router.push('/backtest')
        } else {
          this.$message.error(res?.message || '创建回测失败')
        }
      } catch (e) {
        const msg = e.response?.data?.message || e.response?.data?.error || '创建回测失败'
        this.$message.error(msg)
      }
    }
  },
  mounted() { this.loadListData() }
}
</script>

<style scoped>
.strategy-page { display: flex; height: calc(100vh - 96px); gap: 16px; }
.left-panel { width: 300px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); display: flex; flex-direction: column; overflow: hidden; }
.panel-header { padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; font-weight: 600; }
.search-input { margin: 8px 12px; width: auto; }
.strategy-list { flex: 1; overflow-y: auto; }
.strategy-item { padding: 12px 16px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.strategy-item:hover { background: #fafafa; }
.strategy-item.active { background: #e6f7ff; border-left: 3px solid #1890ff; padding-left: 13px; }
.item-title { display: flex; align-items: center; gap: 8px; font-weight: 500; margin-bottom: 4px; }
.item-meta { font-size: 12px; color: #999; }
.item-stats { margin-top: 4px; font-size: 13px; }
.item-stats .green { color: #52c41a; font-weight: 600; } .item-stats .red { color: #ff4d4f; font-weight: 600; }
.item-stats .label { font-size: 11px; color: #999; margin-left: 4px; }
.right-panel { flex: 1; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); display: flex; flex-direction: column; overflow: hidden; min-height: 0; }
.right-panel.empty { align-items: center; justify-content: center; }
.right-panel > :deep(.code-editor-wrap) { flex: 1; min-height: 0; }
.detail-header { padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; }
.detail-header h3 { margin: 0; font-size: 16px; }
.meta { font-size: 12px; color: #999; }
.btn-group { display: flex; gap: 6px; }
.bt-strategy-info { padding: 8px 12px; background: #fafafa; border-radius: 6px; font-size: 13px; }
</style>
