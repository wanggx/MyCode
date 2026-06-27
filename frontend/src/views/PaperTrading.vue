<template>
  <div class="paper-trading">
    <!-- Header Banner -->
    <div class="paper-banner">
      <div class="banner-left">
        <span class="banner-icon">📝</span>
        <div>
          <div class="banner-title">模拟交易</div>
          <div class="banner-desc">回测验证通过后，部署到模拟盘运行，零风险验证策略在真实市场环境的表现</div>
        </div>
      </div>
      <el-button type="primary" @click="showDeployDialog">🚀 部署策略</el-button>
    </div>

    <!-- Stats -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">运行中</div>
          <div class="stat-val blue">{{ runningCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">已停止</div>
          <div class="stat-val">{{ stoppedCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">今日浮盈</div>
          <div class="stat-val green">¥{{ dailyPnL.toFixed(0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-label">已升级实盘</div>
          <div class="stat-val red">{{ promotedCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Paper Run Cards Grid -->
    <el-row :gutter="16" v-loading="loading">
      <el-col :span="8" v-for="run in paperRuns" :key="run.id" style="margin-bottom:16px;">
        <el-card shadow="hover" class="run-card" :class="{ stopped: run.status !== 'running' }">
          <!-- Header -->
          <div class="card-header">
            <div class="card-title">
              <span class="strat-name">{{ run.strategy_name }}</span>
              <el-tag type="success" size="small">{{ run.strategy_version }}</el-tag>
            </div>
            <el-switch
              :model-value="run.status === 'running'"
              active-color="#1890ff"
              @change="toggleRun(run)"
            />
          </div>

          <!-- Metrics -->
          <div class="card-metrics">
            <div class="cm-item">
              <div class="cm-val" :class="(run.pnl_pct || 0) >= 0 ? 'text-success' : 'text-danger'">
                {{ (run.pnl_pct || 0) >= 0 ? '+' : '' }}{{ (run.pnl_pct || 0).toFixed(2) }}%
              </div>
              <div class="cm-lbl">累计收益</div>
            </div>
            <div class="cm-item">
              <div class="cm-val">¥{{ ((run.pnl || 0)).toFixed(0) }}</div>
              <div class="cm-lbl">累计盈亏</div>
            </div>
            <div class="cm-item">
              <div class="cm-val">{{ run.position_count || 0 }}</div>
              <div class="cm-lbl">持仓</div>
            </div>
            <div class="cm-item">
              <div class="cm-val">{{ (run.win_rate || 0).toFixed(0) }}%</div>
              <div class="cm-lbl">胜率</div>
            </div>
          </div>

          <!-- Meta -->
          <div class="card-meta">
            <span>模拟撮合引擎</span>
            <span>初始 ¥{{ (run.initial_capital || 0).toLocaleString() }}</span>
            <span>{{ run.start_date?.slice(0, 10) || '—' }} 起</span>
          </div>

          <!-- Actions -->
          <div class="card-actions">
            <el-button size="small" @click="viewDetail(run)">📊 详情</el-button>
            <el-button size="small" type="warning" @click="promoteToLive(run)">⬆ 升级实盘</el-button>
            <el-button size="small" type="danger" text @click="deleteRun(run)">🗑</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- Empty -->
      <el-col :span="24" v-if="!loading && paperRuns.length === 0">
        <el-empty description="暂无模拟盘运行，从回测中心验证策略后部署到这里">
          <el-button type="primary" @click="showDeployDialog">🚀 部署第一个策略</el-button>
        </el-empty>
      </el-col>
    </el-row>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" :title="detailTitle" size="60%" direction="rtl">
      <el-tabs v-model="detailTab">
        <el-tab-pane label="📊 概览" name="overview">
          <div class="metrics-row">
            <div class="m-item green"><div class="m-val">{{ (detail.pnl_pct || 0) >= 0 ? '+' : '' }}{{ (detail.pnl_pct || 0).toFixed(2) }}%</div><div class="m-lbl">累计收益</div></div>
            <div class="m-item green"><div class="m-val">¥{{ ((detail.pnl || 0)).toFixed(0) }}</div><div class="m-lbl">累计盈亏</div></div>
            <div class="m-item green"><div class="m-val">{{ (detail.annual_return || 0).toFixed(2) }}%</div><div class="m-lbl">年化收益</div></div>
            <div class="m-item red"><div class="m-val">{{ (detail.max_drawdown || 0).toFixed(2) }}%</div><div class="m-lbl">最大回撤</div></div>
            <div class="m-item blue"><div class="m-val">{{ (detail.sharpe || 0).toFixed(2) }}</div><div class="m-lbl">夏普</div></div>
            <div class="m-item green"><div class="m-val">{{ (detail.win_rate || 0).toFixed(1) }}%</div><div class="m-lbl">胜率</div></div>
          </div>
          <div class="chart-box" ref="paperNavChart" style="height:320px;"></div>
        </el-tab-pane>
        <el-tab-pane label="📋 交易记录" name="trades">
          <el-table :data="detailTrades" stripe size="small" max-height="400">
            <el-table-column prop="trade_time" label="成交时间" width="160" />
            <el-table-column prop="symbol" label="股票" width="120" />
            <el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="direction" label="方向" width="70">
              <template #default="{ row }"><span :class="row.direction === 'buy' ? 'text-danger' : 'text-success'">{{ row.direction === 'buy' ? '买入' : '卖出' }}</span></template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" min-width="150" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="📝 日志" name="logs">
          <div class="log-viewer">
            <div class="log-body">
              <div v-for="(l, i) in detailLogs" :key="i" class="log-line">
                <span class="log-time">{{ l.time }}</span>
                <span :class="'log-' + (l.level || 'info').toLowerCase()">[{{ l.level || 'INFO' }}]</span>
                <span>{{ l.message }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-drawer>

    <!-- Deploy Dialog -->
    <el-dialog v-model="deployVisible" title="🚀 部署策略到模拟盘" width="520px">
      <div class="deploy-strategy-list">
        <div
          v-for="s in deployStrategies" :key="s.id"
          class="deploy-item" :class="{ selected: deploySelected?.id === s.id }"
          @click="deploySelected = s"
        >
          <div class="ds-left">
            <div class="ds-name">{{ s.name }} <el-tag size="small">{{ s.version || 'v1' }}</el-tag></div>
            <div class="ds-meta" v-if="s.last_backtest">
              最近回测：收益 <b :class="(s.last_backtest.return_pct || 0) >= 0 ? 'text-success' : 'text-danger'">{{ (s.last_backtest.return_pct || 0) >= 0 ? '+' : '' }}{{ (s.last_backtest.return_pct || 0).toFixed(2) }}%</b>
              · 夏普 <b>{{ (s.last_backtest.sharpe || 0).toFixed(2) }}</b>
            </div>
          </div>
          <el-tag v-if="s.last_backtest && (s.last_backtest.return_pct || 0) > 15" type="success" size="small">✅ 推荐</el-tag>
        </div>
        <el-empty v-if="deployStrategies.length === 0" description="暂无可部署策略，请先在回测中心验证策略" />
      </div>
      <el-form label-width="80px" size="small" style="margin-top:16px;">
        <el-form-item label="初始资金"><el-input-number v-model="deployCapital" :min="10000" :step="10000" /></el-form-item>
        <el-form-item label="自动启动"><el-switch v-model="deployAutoStart" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deployVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDeploy" :disabled="!deploySelected">🚀 部署到模拟盘</el-button>
      </template>
    </el-dialog>

    <!-- Promote Confirm Dialog -->
    <el-dialog v-model="promoteVisible" title="⬆ 升级为实盘交易" width="460px">
      <el-alert type="warning" :closable="false" show-icon style="margin-bottom:16px;">
        <template #title>升级前请确认：策略已在模拟盘充分验证、已配置券商接入、已设置风控参数</template>
      </el-alert>
      <el-descriptions :column="1" border size="small" style="margin-bottom:16px;">
        <el-descriptions-item label="策略">{{ promoteTarget?.strategy_name || '—' }}</el-descriptions-item>
        <el-descriptions-item label="模拟盘收益">
          <span :class="(promoteTarget?.pnl_pct || 0) >= 0 ? 'text-success' : 'text-danger'">{{ (promoteTarget?.pnl_pct || 0) >= 0 ? '+' : '' }}{{ (promoteTarget?.pnl_pct || 0).toFixed(2) }}%</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form label-width="80px" size="small">
        <el-form-item label="实盘资金"><el-input-number v-model="promoteCapital" :min="10000" :step="10000" /></el-form-item>
        <el-form-item label="券商"><el-select v-model="promoteBroker" style="width:100%"><el-option label="国金证券 (miniQMT)" value="国金证券 miniQMT" /><el-option label="华泰证券" value="华泰证券" /></el-select></el-form-item>
        <el-form-item label="风险确认"><el-checkbox v-model="promoteConfirmed">我已阅读并理解实盘交易风险</el-checkbox></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="promoteVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmPromote" :disabled="!promoteConfirmed">🔴 确认升级</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getLiveRuns, getLiveRunDetail, getLiveRunTrades, getLiveRunLogs, createPaperRun, startPaperRun, stopPaperRun, deletePaperRun, promotePaperRun } from '@/api/trading'
import { fetchStrategies } from '@/api/strategy'

export default {
  name: 'PaperTrading',
  data() {
    return {
      loading: false,
      paperRuns: [],
      // Detail
      detailVisible: false, detailTab: 'overview',
      detailRunId: null, detail: {}, detailTrades: [], detailLogs: [],
      // Deploy
      deployVisible: false, deployStrategies: [], deploySelected: null, deployCapital: 100000, deployAutoStart: true,
      // Promote
      promoteVisible: false, promoteTarget: null, promoteCapital: 50000, promoteBroker: '国金证券 miniQMT', promoteConfirmed: false,
    }
  },
  computed: {
    runningCount() { return this.paperRuns.filter(r => r.status === 'running').length },
    stoppedCount() { return this.paperRuns.filter(r => r.status !== 'running').length },
    dailyPnL() { return this.paperRuns.reduce((s, r) => s + (r.pnl || 0), 0) },
    promotedCount() { return this.paperRuns.filter(r => r._promoted).length },
    detailTitle() { const d = this.detail; return `📝 ${d.strategy_name || ''} — 模拟盘详情` },
  },
  mounted() { this.fetchRuns() },
  methods: {
    async fetchRuns() {
      this.loading = true
      try { const r = await getLiveRuns(1, 50, 'paper'); this.paperRuns = ((r.data.data || {}).items || []) }
      catch (e) { console.error(e) }
      finally { this.loading = false }
    },
    async toggleRun(run) {
      try {
        if (run.status === 'running') {
          await stopPaperRun(run.id); run.status = 'stopped'
        } else {
          await startPaperRun(run.id); run.status = 'running'
        }
        this.$message.success(run.status === 'running' ? `▶ 「${run.strategy_name}」已启动` : `⏸ 「${run.strategy_name}」已停止`)
      } catch (e) { this.$message.error('操作失败') }
    },
    async deleteRun(run) {
      try {
        await this.$confirm(`确定删除「${run.strategy_name}」的模拟盘运行吗？`, '确认', { type: 'warning' })
        await deletePaperRun(run.id)
        this.paperRuns = this.paperRuns.filter(r => r.id !== run.id)
        this.$message.success('已删除')
      } catch (e) { if (e !== 'cancel') console.error(e) }
    },
    async viewDetail(run) {
      this.detailRunId = run.id; this.detailVisible = true; this.detailTab = 'overview'; this.detail = run
      try { const r = await getLiveRunDetail(run.id); this.detail = r.data.data || run } catch (e) { console.error(e) }
      this.fetchDetailTrades(run.id)
      this.fetchDetailLogs(run.id)
      this.$nextTick(() => this.renderChart())
    },
    async fetchDetailTrades(id) { try { const r = await getLiveRunTrades(id); this.detailTrades = (r.data.data || {}).items || [] } catch (e) { console.error(e) } },
    async fetchDetailLogs(id) { try { const r = await getLiveRunLogs(id); this.detailLogs = (r.data.data || {}).items || [] } catch (e) { console.error(e) } },

    // Deploy
    async showDeployDialog() {
      this.deployVisible = true; this.deploySelected = null
      try {
        const r = await fetchStrategies({ page_size: 50 })
        this.deployStrategies = ((r.data.data || {}).items || []).map(s => ({
          id: s.id, name: s.name, version: s.version || 'v1',
          last_backtest: s.last_backtest || null,
        }))
      } catch (e) { console.error(e) }
    },
    async confirmDeploy() {
      if (!this.deploySelected) return
      try {
        await createPaperRun(this.deploySelected.id, this.deployCapital, this.deployAutoStart)
        this.deployVisible = false
        this.$message.success(`✅ 「${this.deploySelected.name}」已部署到模拟盘 · 初始资金 ¥${this.deployCapital.toLocaleString()}`)
        await this.fetchRuns()
      } catch (e) { this.$message.error('部署失败'); console.error(e) }
    },

    // Promote
    promoteToLive(run) {
      this.promoteTarget = run; this.promoteCapital = run.initial_capital || 50000
      this.promoteBroker = '国金证券 miniQMT'; this.promoteConfirmed = false
      this.promoteVisible = true
    },
    async confirmPromote() {
      if (!this.promoteTarget) return
      try {
        await promotePaperRun(this.promoteTarget.id, this.promoteBroker, this.promoteCapital)
        this.promoteVisible = false
        this.$message.success(`🔴 「${this.promoteTarget.strategy_name}」已升级为实盘交易 — ${this.promoteBroker}`)
        await this.fetchRuns()
      } catch (e) { this.$message.error('升级失败'); console.error(e) }
    },

    // Chart
    renderChart() {
      const el = this.$refs.paperNavChart; if (!el) return
      if (this._chart) this._chart.dispose()
      const chart = echarts.init(el); this._chart = chart
      const dates = [], nav = [], bench = []
      const sd = new Date('2026-06-01'); let n = this.detail.initial_capital || 100000, b = 100000
      for (let i = 0; i < 20; i++) {
        const d = new Date(sd); d.setDate(d.getDate() + i)
        if (d.getDay() === 0 || d.getDay() === 6) continue
        dates.push(d.toISOString().slice(0, 10))
        n *= (1 + (Math.random() - 0.45) * 0.015); b *= (1 + (Math.random() - 0.48) * 0.012)
        nav.push((n / 1000).toFixed(2)); bench.push((b / 1000).toFixed(2))
      }
      chart.setOption({
        tooltip: { trigger: 'axis' }, legend: { data: ['策略权益', '沪深300'], top: 5 },
        grid: { left: 55, right: 15, top: 35, bottom: 45 },
        xAxis: { type: 'category', data: dates, boundaryGap: false, axisLabel: { rotate: 30 } },
        yAxis: { type: 'value', axisLabel: { formatter: '¥{value}k' } }, dataZoom: [{ type: 'inside' }],
        series: [
          { name: '策略权益', type: 'line', data: nav, smooth: true, lineStyle: { color: '#1890ff', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(24,144,255,0.25)'},{offset:1,color:'rgba(24,144,255,0.02)'}]) }, symbol: 'none' },
          { name: '沪深300', type: 'line', data: bench, smooth: true, lineStyle: { color: '#faad14', width: 1.5, type: 'dashed' }, symbol: 'none' }
        ]
      })
      chart.resize()
    },
  }
}
</script>

<style scoped>
.paper-trading { padding: 16px; }

/* Banner */
.paper-banner { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; background: linear-gradient(135deg, #e6f7ff, #f0f5ff); border: 1px solid #91d5ff; border-radius: 8px; margin-bottom: 16px; }
.banner-left { display: flex; align-items: center; gap: 12px; }
.banner-icon { font-size: 36px; }
.banner-title { font-size: 16px; font-weight: 700; }
.banner-desc { font-size: 12px; color: #666; margin-top: 4px; }

/* Stats */
.stats-row { margin-bottom: 16px; }
.stat-card { text-align: center; }
.stat-card .stat-label { font-size: 12px; color: #999; }
.stat-card .stat-val { font-size: 24px; font-weight: 700; margin-top: 4px; }
.stat-card .stat-val.blue { color: #1890ff; }
.stat-card .stat-val.green { color: #52c41a; }
.stat-card .stat-val.red { color: #ff4d4f; }

/* Run Cards */
.run-card.stopped { opacity: 0.6; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-title { display: flex; align-items: center; gap: 6px; }
.strat-name { font-weight: 600; font-size: 14px; }

.card-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px; }
.cm-item { text-align: center; }
.cm-val { font-weight: 700; font-size: 15px; }
.cm-lbl { font-size: 10px; color: #999; margin-top: 2px; }

.card-meta { font-size: 11px; color: #999; display: flex; gap: 12px; margin-bottom: 10px; }
.card-actions { display: flex; gap: 6px; padding-top: 10px; border-top: 1px solid #f0f0f0; }

/* Detail */
.metrics-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; padding: 8px 0 16px; }
.m-item { text-align: center; padding: 8px; background: #fafafa; border-radius: 6px; }
.m-item .m-val { font-size: 16px; font-weight: 700; }
.m-item .m-lbl { font-size: 10px; color: #999; margin-top: 2px; }
.m-item.green .m-val { color: #52c41a; }
.m-item.red .m-val { color: #ff4d4f; }
.m-item.blue .m-val { color: #1890ff; }

/* Deploy List */
.deploy-strategy-list { max-height: 280px; overflow-y: auto; border: 1px solid #e8e8e8; border-radius: 6px; }
.deploy-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.deploy-item:hover { background: #fafafa; }
.deploy-item.selected { background: #e6f7ff; }
.ds-name { font-weight: 600; font-size: 14px; }
.ds-meta { font-size: 12px; color: #999; margin-top: 2px; }

/* Chart */
.chart-box { width: 100%; }

/* Log */
.log-viewer { background: #1e1e1e; border-radius: 4px; font-family: monospace; font-size: 12px; line-height: 1.7; }
.log-body { padding: 8px 14px; max-height: 400px; overflow-y: auto; color: #d4d4d4; }
.log-time { color: #6a9955; }
.log-info { color: #4fc3f7; }
.log-warn { color: #ffd54f; }
.log-error { color: #ef5350; }

.text-success { color: #52c41a; }
.text-danger { color: #ff4d4f; }
</style>
