<template>
  <div class="trading-center">
    <div class="ticker-bar">
      <span class="ticker-item" v-for="idx in marketIndices" :key="idx.code">
        <span class="ticker-name">{{ idx.name }}</span>
        <span class="ticker-price" :style="{ color: idx.change_pct >= 0 ? '#ff4d4f' : '#52c41a' }">{{ idx.price.toFixed(2) }}</span>
        <span class="ticker-change" :style="{ color: idx.change_pct >= 0 ? '#ff4d4f' : '#52c41a' }">{{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct.toFixed(2) }}%</span>
      </span>
    </div>

    <el-card shadow="never" class="tc-card">
      <el-tabs v-model="activeTab" @tab-click="onTabClick">
        <!-- Tab 1: 实盘交易列表 -->
        <el-tab-pane name="runs">
          <template #label>
            <span>📋 实盘交易列表 <el-tag type="danger" size="small" effect="dark">实盘</el-tag></span>
          </template>
          <div class="runs-layout">
            <div class="run-list-panel">
              <div class="panel-header"><span>实盘运行中</span><span class="text-muted">{{ liveRuns.length }} 个</span></div>
              <div class="run-items" v-loading="runsLoading">
                <div v-for="run in liveRuns" :key="run.id" class="run-item live-run" :class="{ active: selectedRun && selectedRun.id === run.id }" @click="selectRun(run)">
                  <div class="run-mode-row"><el-tag type="danger" size="small" effect="dark">🔴 实盘</el-tag><span class="broker-tag">{{ run.broker }}</span></div>
                  <div class="run-name">{{ run.strategy_name }} <el-tag type="success" size="small" effect="plain">{{ run.strategy_version }}</el-tag></div>
                  <div class="run-meta"><span>初始 ¥{{ (run.initial_capital || 0).toLocaleString() }}</span><span>· {{ run.start_date ? run.start_date.slice(0, 10) : '—' }} 起</span></div>
                  <div class="run-stats">
                    <span class="stat"><span class="val" :class="(run.pnl_pct || 0) >= 0 ? 'text-success' : 'text-danger'">{{ (run.pnl_pct || 0) >= 0 ? '+' : '' }}{{ (run.pnl_pct || 0).toFixed(2) }}%</span><span class="lbl">累计收益</span></span>
                    <span class="stat"><span class="val">{{ run.position_count || 0 }}</span><span class="lbl">持仓</span></span>
                    <span class="stat"><span class="val">{{ run.win_rate || 0 }}%</span><span class="lbl">胜率</span></span>
                    <span class="stat"><span class="val">{{ (run.sharpe || 0).toFixed(1) }}</span><span class="lbl">夏普</span></span>
                  </div>
                </div>
                <el-empty v-if="!runsLoading && liveRuns.length === 0" description="暂无实盘运行，请先在「模拟交易」中验证策略后再升级" />
              </div>
            </div>

            <div class="run-detail-panel" v-if="selectedRun">
              <div class="detail-header live-header">
                <div class="detail-header-left"><span class="detail-mode-badge live">🔴 实盘运行详情</span><span class="detail-title">{{ selectedRun.strategy_name }} <el-tag type="danger" size="small" effect="dark">{{ selectedRun.strategy_version }}</el-tag></span></div>
                <div class="detail-header-right"><span class="text-muted" style="font-size:12px;">{{ selectedRun.broker }} · 初始 ¥{{ (selectedRun.initial_capital || 0).toLocaleString() }} · {{ selectedRun.start_date?.slice(0, 10) || '—' }} 起</span></div>
              </div>
              <div class="metrics-row live-metrics">
                <div class="m-item green"><div class="m-val">{{ (runDetail.pnl_pct || 0) >= 0 ? '+' : '' }}{{ (runDetail.pnl_pct || 0).toFixed(2) }}%</div><div class="m-lbl">累计收益</div></div>
                <div class="m-item green"><div class="m-val">¥{{ ((runDetail.pnl || 0)).toFixed(0) }}</div><div class="m-lbl">累计盈亏</div></div>
                <div class="m-item green"><div class="m-val">{{ (runDetail.annual_return || 0).toFixed(2) }}%</div><div class="m-lbl">年化收益</div></div>
                <div class="m-item red"><div class="m-val">{{ (runDetail.max_drawdown || 0).toFixed(2) }}%</div><div class="m-lbl">最大回撤</div></div>
                <div class="m-item blue"><div class="m-val">{{ (runDetail.sharpe || 0).toFixed(2) }}</div><div class="m-lbl">夏普</div></div>
                <div class="m-item green"><div class="m-val">{{ (runDetail.win_rate || 0).toFixed(1) }}%</div><div class="m-lbl">胜率</div></div>
                <div class="m-item blue"><div class="m-val">{{ runDetail.position_count || 0 }}</div><div class="m-lbl">持仓数</div></div>
                <div class="m-item blue"><div class="m-val">{{ runDetail.total_trades || 0 }}</div><div class="m-lbl">交易笔数</div></div>
              </div>
              <el-tabs v-model="detailTab" @tab-click="onDetailTabClick">
                <el-tab-pane label="📊 概览" name="overview"><div class="chart-box" ref="navChart" style="height:320px;"></div></el-tab-pane>
                <el-tab-pane label="📋 交易记录" name="trades">
                  <el-table :data="trades" stripe size="small" v-loading="tradesLoading" max-height="300">
                    <el-table-column prop="trade_time" label="成交时间" width="160" /><el-table-column prop="symbol" label="股票" width="120" />
                    <el-table-column prop="name" label="名称" width="100" /><el-table-column prop="direction" label="方向" width="70"><template #default="{ row }"><span :class="row.direction === 'buy' ? 'text-danger' : 'text-success'">{{ row.direction === 'buy' ? '买入' : '卖出' }}</span></template></el-table-column>
                    <el-table-column prop="price" label="价格" width="80" /><el-table-column prop="quantity" label="数量" width="80" /><el-table-column prop="reason" label="原因" min-width="150" />
                  </el-table>
                </el-tab-pane>
                <el-tab-pane label="📈 当前持仓" name="positions">
                  <el-table :data="positions" stripe size="small" v-loading="posLoading" max-height="300">
                    <el-table-column prop="symbol" label="股票" width="120" /><el-table-column prop="name" label="名称" width="100" />
                    <el-table-column prop="quantity" label="数量" width="80" /><el-table-column prop="cost_price" label="成本价" width="80" /><el-table-column prop="current_price" label="现价" width="80" />
                    <el-table-column prop="market_value" label="市值" width="100" /><el-table-column prop="pnl" label="浮盈" width="100"><template #default="{ row }"><span :class="row.pnl >= 0 ? 'text-success' : 'text-danger'">¥{{ row.pnl }}</span></template></el-table-column>
                    <el-table-column prop="weight" label="占比" width="70"><template #default="{ row }">{{ (row.weight || 0).toFixed(1) }}%</template></el-table-column>
                  </el-table>
                </el-tab-pane>
                <el-tab-pane label="📝 日志" name="logs">
                  <div class="log-viewer"><div class="log-header"><span>📄 logs/live/run_{{ selectedRun.id }}.log</span></div>
                    <div class="log-body"><div v-for="(l, i) in logs" :key="i" class="log-line"><span class="log-time">{{ l.time }}</span><span :class="'log-' + (l.level || 'info').toLowerCase()">[{{ l.level || 'INFO' }}]</span><span>{{ l.message }}</span></div></div>
                  </div>
                </el-tab-pane>
                <el-tab-pane label="💻 策略代码" name="code">
                  <div class="code-header"><span>{{ selectedRun.strategy_name }}_{{ selectedRun.strategy_version }}.py</span><span class="text-muted" style="font-size:11px;">实盘运行中 · 只读</span></div>
                  <el-input type="textarea" :rows="18" readonly :value="strategyCode" class="code-textarea" />
                </el-tab-pane>
                <el-tab-pane label="📐 风控指标" name="metrics">
                  <el-descriptions :column="2" border size="small" v-if="metrics">
                    <el-descriptions-item v-for="item in metricItems" :key="item.label" :label="item.label"><span :class="item.css">{{ item.value }}</span></el-descriptions-item>
                  </el-descriptions>
                </el-tab-pane>
              </el-tabs>
            </div>
            <div class="run-detail-panel empty-detail" v-else><el-empty description="选择一个实盘运行查看详情" /></div>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 交易信号 -->
        <el-tab-pane name="signals">
          <template #label><span>📡 交易信号 <el-tag type="warning" size="small">{{ signalsTotal }}</el-tag></span></template>
          <el-table :data="signals" stripe size="small" v-loading="signalsLoading" max-height="520">
            <el-table-column prop="time" label="时间" width="160" /><el-table-column prop="strategy_name" label="策略" width="140" />
            <el-table-column prop="symbol" label="股票" width="120" /><el-table-column prop="name" label="名称" width="100" />
            <el-table-column prop="direction" label="方向" width="80"><template #default="{ row }"><el-tag :type="row.direction === 'buy' ? 'danger' : 'success'" size="small" effect="dark">{{ row.direction === 'buy' ? '买入' : '卖出' }}</el-tag></template></el-table-column>
            <el-table-column prop="reason" label="信号原因" min-width="180" />
            <el-table-column prop="status" label="状态" width="90"><template #default="{ row }"><el-tag :type="row.status === 'executed' ? 'success' : 'warning'" size="small">{{ row.status === 'executed' ? '✅ 已执行' : '⏳ 待确认' }}</el-tag></template></el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Tab 3: 风控概览 -->
        <el-tab-pane name="risk">
          <template #label><span>🛡 风控概览</span></template>
          <div class="risk-layout" v-loading="riskLoading">
            <el-row :gutter="20">
              <el-col :span="12"><el-card shadow="never"><template #header>全局风控指标</template>
                <div class="risk-bar" v-for="bar in riskBars" :key="bar.label"><div class="risk-bar-label"><span>{{ bar.label }}</span><span :class="bar.warn ? 'text-warning' : 'text-success'">{{ bar.current }}{{ bar.suffix }}</span></div><el-progress :percentage="bar.percentage" :color="bar.warn ? '#faad14' : '#52c41a'" :stroke-width="8" /></div>
              </el-card></el-col>
              <el-col :span="12"><el-card shadow="never"><template #header>各策略风控状态</template>
                <el-table :data="riskOverview.strategy_risks || []" stripe size="small">
                  <el-table-column prop="strategy_name" label="策略" width="140" /><el-table-column prop="position_ratio" label="仓位" width="80"><template #default="{ row }">{{ row.position_ratio }}%</template></el-table-column>
                  <el-table-column prop="daily_pnl" label="今日盈亏" width="100"><template #default="{ row }"><span :class="row.daily_pnl >= 0 ? 'text-success' : 'text-danger'">¥{{ row.daily_pnl }}</span></template></el-table-column>
                  <el-table-column prop="max_drawdown" label="最大回撤" width="90"><template #default="{ row }">{{ row.max_drawdown }}%</template></el-table-column>
                  <el-table-column prop="stop_loss_triggered" label="止损触发" width="80" />
                  <el-table-column prop="status" label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === 'normal' ? 'success' : 'warning'" size="small">{{ row.status === 'normal' ? '✅ 正常' : '⚠ 预警' }}</el-tag></template></el-table-column>
                </el-table>
              </el-card></el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getMarketIndices, getLiveRuns, getLiveRunDetail, getLiveRunTrades, getLiveRunPositions, getLiveRunLogs, getLiveRunMetrics, getTradingSignals, getRiskOverview } from '@/api/trading'
import { fetchStrategy } from '@/api/strategy'

export default {
  name: 'TradingCenter',
  data() {
    return {
      activeTab: 'runs', detailTab: 'overview',
      marketIndices: [],
      allRuns: [], liveRuns: [], runsLoading: false,
      selectedRun: null, runDetail: {},
      trades: [], tradesLoading: false,
      positions: [], posLoading: false,
      logs: [], metrics: null, strategyCode: '',
      signals: [], signalsTotal: 0, signalsLoading: false,
      riskOverview: { strategy_risks: [] }, riskLoading: false,
    }
  },
  computed: {
    riskBars() {
      const r = this.riskOverview
      return [
        { label: `总仓位上限 (${r.position_limit || 80}%)`, current: r.position_ratio || 0, suffix: '%', percentage: Math.min(100, (r.position_ratio || 0) / (r.position_limit || 80) * 100), warn: (r.position_ratio || 0) > 60 },
        { label: `单票集中度 (${r.concentration_limit || 25}%)`, current: r.max_single_concentration || 0, suffix: '%', percentage: Math.min(100, (r.max_single_concentration || 0) / (r.concentration_limit || 25) * 100), warn: (r.max_single_concentration || 0) > 20 },
        { label: `日内亏损上限 (${r.daily_loss_limit || 5}%)`, current: r.daily_pnl_pct || 0, suffix: '%', percentage: Math.min(100, Math.abs(r.daily_pnl_pct || 0) / (r.daily_loss_limit || 5) * 100), warn: (r.daily_pnl_pct || 0) < 0 },
        { label: `最大回撤限制 (${r.drawdown_limit || 20}%)`, current: r.max_drawdown || 0, suffix: '%', percentage: Math.min(100, Math.abs(r.max_drawdown || 0) / (r.drawdown_limit || 20) * 100), warn: false },
      ]
    },
    metricItems() {
      const m = this.metrics || {}
      return [
        { label: '年化波动率', value: (m.annual_volatility || 0).toFixed(2) + '%' },
        { label: '下行波动率', value: (m.downside_volatility || 0).toFixed(2) + '%' },
        { label: 'VaR (95%)', value: (m.var_95 || 0).toFixed(2) + '%', css: 'text-danger' },
        { label: 'CVaR (95%)', value: (m.cvar_95 || 0).toFixed(2) + '%', css: 'text-danger' },
        { label: 'Calmar 比率', value: (m.calmar_ratio || 0).toFixed(2) },
        { label: '信息比率', value: (m.information_ratio || 0).toFixed(2) },
        { label: '跟踪误差', value: (m.tracking_error || 0).toFixed(2) + '%' },
        { label: 'Alpha', value: (m.alpha || 0).toFixed(2) + '%', css: (m.alpha || 0) >= 0 ? 'text-success' : 'text-danger' },
        { label: 'Beta', value: (m.beta || 0).toFixed(2) },
        { label: '最长连盈', value: (m.max_consecutive_wins || 0) + ' 次' },
      ]
    },
  },
  mounted() { this.fetchAll() },
  methods: {
    fetchAll() { this.fetchMarketIndices(); this.fetchLiveRuns(); this.fetchSignals(); this.fetchRiskOverview() },
    async fetchMarketIndices() { try { const r = await getMarketIndices(); this.marketIndices = r.data.data || [] } catch (e) { console.error(e) } },
    async fetchLiveRuns() { this.runsLoading = true; try { const r = await getLiveRuns(1, 20, 'live'); this.liveRuns = (r.data.data || {}).items || [] } catch (e) { console.error(e) } finally { this.runsLoading = false } },
    async selectRun(run) { this.selectedRun = run; this.detailTab = 'overview'; try { const r = await getLiveRunDetail(run.id); this.runDetail = r.data.data || run } catch (e) { console.error(e); this.runDetail = { ...run } } this.fetchTrades(run.id); this.fetchPositions(run.id); this.fetchLogs(run.id); this.fetchMetrics(run.id); this.fetchStrategyCode(run.strategy_id); this.$nextTick(() => this.renderNavChart()) },
    async fetchTrades(id) { this.tradesLoading = true; try { const r = await getLiveRunTrades(id); this.trades = (r.data.data || {}).items || [] } catch (e) { console.error(e) } finally { this.tradesLoading = false } },
    async fetchPositions(id) { this.posLoading = true; try { const r = await getLiveRunPositions(id); this.positions = r.data.data || [] } catch (e) { console.error(e) } finally { this.posLoading = false } },
    async fetchLogs(id) { try { const r = await getLiveRunLogs(id); this.logs = (r.data.data || {}).items || [] } catch (e) { console.error(e) } },
    async fetchMetrics(id) { try { const r = await getLiveRunMetrics(id); this.metrics = r.data.data || null } catch (e) { console.error(e) } },
    async fetchStrategyCode(sid) { if (!sid) { this.strategyCode = '# 策略代码加载中...'; return } try { const r = await fetchStrategy(sid); const s = r.data.data || {}; const versions = s.versions || []; const latest = versions.length > 0 ? versions[versions.length - 1] : {}; this.strategyCode = latest.source_code || s.source_code || '# 暂无策略代码' } catch (e) { this.strategyCode = '# 策略代码加载失败' } },
    async fetchSignals() { this.signalsLoading = true; try { const r = await getTradingSignals(); const d = r.data.data || {}; this.signals = d.items || []; this.signalsTotal = d.total || 0 } catch (e) { console.error(e) } finally { this.signalsLoading = false } },
    async fetchRiskOverview() { this.riskLoading = true; try { const r = await getRiskOverview(); this.riskOverview = r.data.data || { strategy_risks: [] } } catch (e) { console.error(e) } finally { this.riskLoading = false } },
    onTabClick() { if (this.activeTab === 'signals') this.fetchSignals(); if (this.activeTab === 'risk') this.fetchRiskOverview() },
    onDetailTabClick(tab) { if (tab.paneName === 'overview') this.$nextTick(() => this.renderNavChart()) },
    renderNavChart() {
      const el = this.$refs.navChart; if (!el) return
      if (this._tcChart) this._tcChart.dispose()
      const chart = echarts.init(el); this._tcChart = chart
      const dates = [], nav = [], bench = []; const sd = new Date('2026-06-01'); let n = this.runDetail.initial_capital || 100000, b = 100000
      for (let i = 0; i < 20; i++) { const d = new Date(sd); d.setDate(d.getDate() + i); if (d.getDay() === 0 || d.getDay() === 6) continue; dates.push(d.toISOString().slice(0, 10)); n *= (1 + (Math.random() - 0.45) * 0.015); b *= (1 + (Math.random() - 0.48) * 0.012); nav.push((n / 1000).toFixed(2)); bench.push((b / 1000).toFixed(2)) }
      chart.setOption({ tooltip: { trigger: 'axis' }, legend: { data: ['策略权益', '沪深300'], top: 5 }, grid: { left: 55, right: 15, top: 35, bottom: 45 }, xAxis: { type: 'category', data: dates, boundaryGap: false }, yAxis: { type: 'value', axisLabel: { formatter: '¥{value}k' } }, dataZoom: [{ type: 'inside' }], series: [{ name: '策略权益', type: 'line', data: nav, smooth: true, lineStyle: { color: '#ff4d4f', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(255,77,79,0.25)'},{offset:1,color:'rgba(255,77,79,0.02)'}]) }, symbol: 'none' }, { name: '沪深300', type: 'line', data: bench, smooth: true, lineStyle: { color: '#faad14', width: 1.5, type: 'dashed' }, symbol: 'none' }] })
      chart.resize()
    },
  },
}
</script>

<style scoped>
.trading-center { padding: 0; }
.tc-card { border-radius: 0; margin: 0; }
.tc-card :deep(.el-card__body) { padding: 0; }

.ticker-bar { display: flex; gap: 24px; padding: 8px 20px; background: #fff; border-bottom: 1px solid #e8e8e8; overflow-x: auto; font-size: 12px; flex-shrink: 0; }
.ticker-item { display: flex; align-items: center; gap: 6px; white-space: nowrap; cursor: pointer; padding: 2px 6px; border-radius: 3px; }
.ticker-item:hover { background: #f5f5f5; }
.ticker-name { font-weight: 500; color: #666; }
.ticker-price { font-weight: 600; }
.ticker-change { font-weight: 500; }

.runs-layout { display: flex; height: calc(100vh - 200px); }
.run-list-panel { width: 360px; border-right: 1px solid #e8e8e8; display: flex; flex-direction: column; flex-shrink: 0; }
.panel-header { padding: 12px 16px; border-bottom: 1px solid #e8e8e8; font-weight: 600; font-size: 14px; display: flex; justify-content: space-between; }
.run-items { flex: 1; overflow-y: auto; }
.run-item { padding: 12px 14px; border-bottom: 1px solid #f5f5f5; cursor: pointer; transition: all 0.2s; border-left: 3px solid transparent; }
.run-item:hover { background: #fafafa; }
.run-item.live-run.active { border-left-color: #ff4d4f; background: #fff2f0; }
.run-mode-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.broker-tag { font-size: 11px; color: #ff4d4f; font-weight: 500; }
.run-name { font-weight: 600; font-size: 14px; margin-bottom: 3px; display: flex; align-items: center; gap: 6px; }
.run-meta { font-size: 12px; color: #999; margin-bottom: 6px; }
.run-stats { display: flex; gap: 14px; font-size: 12px; }
.run-stats .stat { display: flex; flex-direction: column; }
.run-stats .stat .val { font-weight: 600; font-size: 13px; }
.run-stats .stat .lbl { color: #999; font-size: 10px; }

.run-detail-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.run-detail-panel.empty-detail { justify-content: center; align-items: center; }
.detail-header { padding: 12px 20px; border-bottom: 1px solid #e8e8e8; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
.detail-header.live-header { background: #fff2f0; }
.detail-header-left { display: flex; align-items: center; gap: 10px; }
.detail-mode-badge { font-size: 14px; font-weight: 600; }
.detail-mode-badge.live { color: #ff4d4f; }
.detail-title { font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 6px; }
.detail-header-right { display: flex; align-items: center; gap: 12px; }

.metrics-row { display: grid; grid-template-columns: repeat(8, 1fr); gap: 8px; padding: 12px 16px; background: #fff; }
.metrics-row.live-metrics { background: #fffbfb; }
.m-item { text-align: center; padding: 8px; background: #fafafa; border-radius: 6px; }
.m-item .m-val { font-size: 16px; font-weight: 700; }
.m-item .m-lbl { font-size: 10px; color: #999; margin-top: 2px; }
.m-item.green .m-val { color: #52c41a; }
.m-item.red .m-val { color: #ff4d4f; }
.m-item.blue .m-val { color: #1890ff; }

.chart-box { width: 100%; }
.log-viewer { background: #1e1e1e; border-radius: 4px; overflow: hidden; font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 12px; line-height: 1.7; }
.log-header { padding: 6px 14px; background: #2d2d2d; color: #999; font-size: 11px; }
.log-body { padding: 8px 14px; max-height: 300px; overflow-y: auto; color: #d4d4d4; }
.log-time { color: #6a9955; }
.log-info { color: #4fc3f7; }
.log-warn { color: #ffd54f; }
.log-error { color: #ef5350; }

.code-header { padding: 8px 16px; background: #2d2d2d; color: #ccc; font-size: 12px; border-radius: 4px 4px 0 0; display: flex; justify-content: space-between; }
.code-textarea :deep(textarea) { background: #1e1e1e; color: #d4d4d4; font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 13px; line-height: 1.6; border: none; border-radius: 0 0 4px 4px; }

.risk-layout { padding: 0; }
.risk-bar { margin-bottom: 16px; }
.risk-bar-label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; }

.text-success { color: #52c41a; }
.text-danger { color: #ff4d4f; }
.text-warning { color: #faad14; }
.text-muted { color: #999; }
</style>
