<template>
  <div class="bt-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <div class="panel-header"><span>回测列表</span><el-button type="primary" size="small" @click="showCreateDialog">+ 新建</el-button></div>
      <el-select v-model="statusFilter" placeholder="状态" size="small" clearable style="margin:8px 12px" @change="loadList">
        <el-option label="全部" value="" /><el-option label="运行中" value="running" /><el-option label="已完成" value="completed" /><el-option label="失败" value="failed" />
      </el-select>
      <div class="bt-list">
        <div v-for="bt in backtests" :key="bt.id" class="bt-item" :class="{ active: selected?.id === bt.id }" @click="selectBacktest(bt)">
          <div class="item-title">
            <span :class="statusIcon(bt.status)">{{ statusIcon(bt.status) }}</span>
            <span>{{ bt.strategy_name || 'BT#'+bt.id }}</span>
            <el-tag v-if="bt.status==='running'" type="warning" size="small" effect="dark">运行中</el-tag>
            <el-tag v-else-if="bt.status==='completed'" type="success" size="small">完成</el-tag>
            <el-tag v-else-if="bt.status==='failed'" type="danger" size="small">失败</el-tag>
          </div>
          <div class="item-meta">{{ bt.created_at?.slice(0,16) }}</div>
          <div class="item-stats" v-if="bt.status==='completed'">
            <span :class="bt.total_return>0?'green':'red'">{{ bt.total_return ? (bt.total_return*100).toFixed(1)+'%' : '-' }}</span>
            <span>夏普 {{ bt.sharpe_ratio?.toFixed(2) || '-' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel" v-if="selected">
      <!-- Progress Bar -->
      <div class="progress-bar" v-if="selected.status==='running'">
        <div class="progress-fill" :style="{width: (selected.progress||0)+'%'}"></div>
        <span class="progress-text">{{ selected.progress?.toFixed(0) || 0 }}% · {{ selected.current_date || '运行中...' }}</span>
        <el-button type="danger" size="small" @click="handleCancel" style="margin-left:12px">取消</el-button>
      </div>
      <!-- Summary -->
      <div class="summary-card">
        <div><h3>{{ selected.strategy_name || '回测 #'+selected.id }}</h3><span class="meta">{{ selected.created_at?.slice(0,16) }} · 初始 ¥{{ selected.config?.initial_capital || 100000 }}</span></div>
        <el-button size="small" @click="handleRerun">🔄 重新运行</el-button>
      </div>
      <!-- Metrics -->
      <div class="metrics" v-if="selected.status==='completed'">
        <div class="m-item"><div class="m-val green">{{ (selected.total_return*100).toFixed(2) }}%</div><div class="m-label">总收益</div></div>
        <div class="m-item"><div class="m-val">{{ (selected.annualized_return*100).toFixed(2) }}%</div><div class="m-label">年化收益</div></div>
        <div class="m-item"><div class="m-val red">{{ (selected.max_drawdown*100).toFixed(2) }}%</div><div class="m-label">最大回撤</div></div>
        <div class="m-item"><div class="m-val">{{ selected.sharpe_ratio?.toFixed(2) }}</div><div class="m-label">夏普比率</div></div>
        <div class="m-item"><div class="m-val">{{ (selected.win_rate*100).toFixed(1) }}%</div><div class="m-label">胜率</div></div>
        <div class="m-item"><div class="m-val">¥{{ selected.final_value?.toLocaleString() }}</div><div class="m-label">最终资产</div></div>
      </div>
      <!-- Tabs -->
      <el-tabs v-model="activeTab" class="tabs">
        <el-tab-pane label="📊 净值曲线" name="nav"><div ref="navChart" class="chart-box"></div></el-tab-pane>
        <el-tab-pane label="📋 交易记录" name="trades"><el-table :data="trades?.items||[]" size="small" max-height="300"><el-table-column prop="ts_code" label="股票" /><el-table-column prop="buy_date" label="买入日" /><el-table-column prop="sell_date" label="卖出日" /><el-table-column prop="pnl" label="盈亏" /></el-table></el-tab-pane>
        <el-tab-pane label="📉 风险指标" name="risk"><div v-if="risk" class="risk-table"><table><tr v-for="(v,k) in risk" :key="k"><td>{{ k }}</td><td>{{ v }}</td></tr></table></div></el-tab-pane>
        <el-tab-pane label="📝 日志" name="logs"><pre class="log-view" v-if="logs">{{ logs.lines?.join('') }}</pre></el-tab-pane>
      </el-tabs>
    </div>
    <div class="right-panel empty" v-else><el-empty description="选择一个回测查看详情" /></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { mapState, mapActions } from 'vuex'
export default {
  name: 'BacktestCenter',
  data() { return { statusFilter: '', selected: null, activeTab: 'nav', trades: null, risk: null, logs: null } },
  computed: { ...mapState('backtest', ['list']), backtests() { return this.list } },
  methods: {
    ...mapActions('backtest', ['loadList', 'loadDetail', 'cancel', 'loadTrades', 'loadRiskMetrics', 'loadLogs', 'loadNav']),
    statusIcon(s) { return s==='completed'?'✅':s==='running'?'⚡':s==='failed'?'❌':'⏳' },
    async loadListData() { await this.loadList({ status: this.statusFilter || undefined }) },
    async selectBacktest(bt) {
      this.selected = bt; this.activeTab = 'nav'
      if (bt.status === 'completed') {
        const [nav, trades, risk, logs] = await Promise.all([this.loadNav(bt.id), this.loadTrades({ id: bt.id }), this.loadRiskMetrics(bt.id), this.loadLogs(bt.id)])
        this.trades = trades; this.risk = risk; this.logs = logs
        this.$nextTick(() => { if (nav) this.renderNavChart(nav) })
      }
    },
    renderNavChart(nav) {
      const el = this.$refs.navChart; if (!el) return
      const chart = echarts.init(el)
      const dates = nav.dates || []; const navVals = nav.nav || []; const benchVals = nav.benchmark_nav || []
      chart.setOption({
        tooltip: { trigger: 'axis' }, legend: { data: ['策略','基准'], top: 5 },
        grid: { left: 50, right: 20, top: 40, bottom: 50 },
        xAxis: { type: 'category', data: dates, axisLabel: { interval: Math.max(1, Math.floor(dates.length/6)), formatter: v => v?.slice(5) } },
        yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
        dataZoom: [{ type: 'slider', bottom: 10 }],
        series: [
          { name: '策略', type: 'line', data: navVals.map(v => ((v-1)*100).toFixed(2)), smooth: true, lineStyle: { color: '#1890ff', width: 2 }, areaStyle: { color: 'rgba(24,144,255,.15)' }, symbol: 'none' },
          { name: '基准', type: 'line', data: benchVals.map(v => ((v-1)*100).toFixed(2)), smooth: true, lineStyle: { color: '#faad14', width: 2, type: 'dashed' }, symbol: 'none' }
        ]
      }); chart.resize()
    },
    async handleCancel() { if (this.selected) { await this.cancel(this.selected.id); this.$message.info('已取消'); this.loadListData() } },
    handleRerun() { this.$router.push('/strategies') },
    showCreateDialog() { this.$router.push('/strategies') }
  },
  mounted() { this.loadListData() }
}
</script>

<style scoped>
.bt-page { display: flex; height: calc(100vh - 96px); gap: 16px; }
.left-panel { width: 320px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); display: flex; flex-direction: column; overflow: hidden; }
.panel-header { padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; font-weight: 600; }
.bt-list { flex: 1; overflow-y: auto; }
.bt-item { padding: 12px 16px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.bt-item:hover { background: #fafafa; }
.bt-item.active { background: #e6f7ff; border-left: 3px solid #1890ff; padding-left: 13px; }
.item-title { display: flex; align-items: center; gap: 6px; font-weight: 500; }
.item-meta { font-size: 12px; color: #999; margin-top: 4px; }
.item-stats { margin-top: 4px; font-size: 13px; display: flex; gap: 12px; }
.green { color: #52c41a; font-weight: 600; } .red { color: #ff4d4f; font-weight: 600; }
.right-panel { flex: 1; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); display: flex; flex-direction: column; overflow: hidden; }
.right-panel.empty { align-items: center; justify-content: center; }
.progress-bar { display: flex; align-items: center; padding: 8px 16px; background: #f0f5ff; border-bottom: 1px solid #d6e4ff; }
.progress-fill { height: 6px; background: linear-gradient(90deg,#1890ff,#6f42c1); border-radius: 3px; transition: width .5s; }
.progress-text { font-size: 12px; color: #666; margin-left: 8px; white-space: nowrap; flex: 1; }
.summary-card { padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; }
.summary-card h3 { margin: 0; font-size: 15px; }
.meta { font-size: 12px; color: #999; }
.metrics { display: grid; grid-template-columns: repeat(6,1fr); gap: 8px; padding: 12px 16px; border-bottom: 1px solid #eee; }
.m-item { text-align: center; }
.m-val { font-size: 18px; font-weight: 700; }
.m-label { font-size: 11px; color: #999; }
.tabs { flex: 1; padding: 0 16px; }
.chart-box { width: 100%; height: 350px; }
.risk-table { font-size: 13px; } .risk-table td { padding: 4px 8px; }
.log-view { background: #1e1e1e; color: #d4d4d4; padding: 12px; font-size: 11px; max-height: 350px; overflow-y: auto; border-radius: 6px; white-space: pre-wrap; }
</style>
