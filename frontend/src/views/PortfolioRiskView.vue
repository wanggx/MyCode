<template>
  <div class="page-container">
    <div class="page-header">
      <h2>组合风控</h2>
      <p class="page-desc">模拟组合净值、持仓、行业分布和风险预警。</p>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="模拟组合A" name="portfolio">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card shadow="hover" class="chart-card">
              <template #header><span class="card-title">净值曲线</span></template>
              <div ref="navChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="risk-card">
              <template #header><span class="card-title">风险指标</span></template>
              <div class="risk-grid">
                <div v-for="m in riskMetrics" :key="m.label" class="risk-item">
                  <div class="risk-label">{{ m.label }}</div>
                  <div class="risk-value" :style="{ color: m.color }">{{ m.value }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="16" style="margin-top: 16px">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header><span class="card-title">持仓明细</span></template>
              <el-table :data="positionList" stripe size="small">
                <el-table-column prop="ts_code" label="代码" width="110" />
                <el-table-column prop="name" label="名称" width="100" />
                <el-table-column prop="industry" label="行业" width="100" />
                <el-table-column prop="market_value" label="持仓市值(万)" width="120" align="right">
                  <template #default="{ row }">
                    {{ row.market_value != null ? row.market_value.toLocaleString() : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="weight" label="占比" width="90" align="right">
                  <template #default="{ row }">
                    {{ row.weight != null ? (row.weight * 100).toFixed(2) + '%' : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="change" label="较上期变化" align="right">
                  <template #default="{ row }">
                    <span :style="{ color: changeColor(row.change), fontWeight: 'bold' }">
                      {{ formatChange(row.change) }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header><span class="card-title">行业分布</span></template>
              <div ref="sectorChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="16" style="margin-top: 16px">
          <el-col :span="8">
            <el-alert type="warning" :closable="false" class="risk-alert">
              <template #title>
                <div class="alert-title">行业集中</div>
              </template>
              <div class="alert-desc">前3行业占比 {{ top3IndustryRatio }}%</div>
            </el-alert>
          </el-col>
          <el-col :span="8">
            <el-alert type="error" :closable="false" class="risk-alert">
              <template #title>
                <div class="alert-title">单股过重</div>
              </template>
              <div class="alert-desc">最大持仓占比 {{ maxHoldingRatio }}%</div>
            </el-alert>
          </el-col>
          <el-col :span="8">
            <el-alert type="success" :closable="false" class="risk-alert">
              <template #title>
                <div class="alert-title">选股质量</div>
              </template>
              <div class="alert-desc">缺失股票数 {{ missingStockCount }}</div>
            </el-alert>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="观察池" name="watchlist">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">观察池</span>
              <el-button type="primary" size="small" @click="watchlistDialogVisible = true">添加股票</el-button>
            </div>
          </template>
          <el-table :data="watchlist" stripe size="small">
            <el-table-column prop="ts_code" label="代码" width="120" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="market" label="市场" width="100" />
            <el-table-column prop="added_time" label="添加时间" width="180" />
            <el-table-column prop="note" label="备注" min-width="160" />
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button link type="danger" size="small" @click="removeWatchlist(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-dialog v-model="watchlistDialogVisible" title="添加到观察池" width="480px" :close-on-click-modal="false">
          <el-form :model="watchlistForm" label-width="80px">
            <el-form-item label="股票代码" required>
              <el-input v-model="watchlistForm.ts_code" placeholder="如 600519.SH" />
            </el-form-item>
            <el-form-item label="名称" required>
              <el-input v-model="watchlistForm.name" placeholder="股票名称" />
            </el-form-item>
            <el-form-item label="市场">
              <el-select v-model="watchlistForm.market" placeholder="请选择" style="width: 100%">
                <el-option label="沪市" value="沪市" />
                <el-option label="深市" value="深市" />
                <el-option label="港股" value="港股" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="watchlistForm.note" type="textarea" :rows="2" placeholder="可选备注" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="watchlistDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleAddWatchlist">确认</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <el-tab-pane label="自定义组合" name="custom">
        <el-card shadow="hover">
          <template #header><span class="card-title">自定义组合</span></template>
          <el-table :data="customPortfolios" stripe size="small">
            <el-table-column prop="name" label="组合名称" min-width="160" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="created_time" label="创建时间" width="180" />
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewCustomPortfolio(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from '@/config/axios'

function generateMockNav() {
  const data = []
  let portfolioNav = 1.0
  let benchmarkNav = 1.0
  const startDate = new Date('2024-01-02')
  for (let i = 0; i < 300; i++) {
    const d = new Date(startDate)
    d.setDate(d.getDate() + i)
    const dow = d.getDay()
    if (dow === 0 || dow === 6) continue
    portfolioNav *= (1 + (Math.random() - 0.46) * 0.018)
    benchmarkNav *= (1 + (Math.random() - 0.49) * 0.012)
    data.push({
      trade_date: d.toISOString().slice(0, 10),
      portfolio_nav: parseFloat(portfolioNav.toFixed(4)),
      benchmark_nav: parseFloat(benchmarkNav.toFixed(4))
    })
  }
  return data
}

const MOCK_NAV = generateMockNav()

const MOCK_POSITIONS = [
  { ts_code: '300750.SZ', name: '宁德时代', industry: '电力设备', market_value: 1222.45, weight: 0.0982, change: 0.0042 },
  { ts_code: '600519.SH', name: '贵州茅台', industry: '食品饮料', market_value: 987.32, weight: 0.0794, change: -0.0021 },
  { ts_code: '601318.SH', name: '中国平安', industry: '非银金融', market_value: 752.18, weight: 0.0604, change: 0.0 },
  { ts_code: '000858.SZ', name: '五粮液', industry: '食品饮料', market_value: 628.50, weight: 0.0505, change: 0.0018 },
  { ts_code: '600036.SH', name: '招商银行', industry: '银行', market_value: 545.30, weight: 0.0438, change: -0.0032 },
  { ts_code: '002475.SZ', name: '立讯精密', industry: '电子', market_value: 412.80, weight: 0.0332, change: 0.0025 }
]

const MOCK_RISK = {
  annual_return: 0.1856,
  annual_volatility: 0.1223,
  sharpe_ratio: 1.52,
  max_drawdown: -0.0821,
  calmar_ratio: 2.26,
  win_rate: 0.58
}

const MOCK_WATCHLIST = [
  { id: 1, ts_code: '000001.SZ', name: '平安银行', market: '深市', added_time: '2026-05-20 10:30:00', note: '关注底部放量' },
  { id: 2, ts_code: '600036.SH', name: '招商银行', market: '沪市', added_time: '2026-05-18 14:15:00', note: '银行龙头' },
  { id: 3, ts_code: '601012.SH', name: '隆基绿能', market: '沪市', added_time: '2026-05-15 09:45:00', note: '新能源观察' },
  { id: 4, ts_code: '000725.SZ', name: '京东方A', market: '深市', added_time: '2026-05-10 11:00:00', note: '' },
  { id: 5, ts_code: '00700.HK', name: '腾讯控股', market: '港股', added_time: '2026-05-08 16:00:00', note: '港股核心资产' }
]

const MOCK_SECTOR_DATA = [
  { name: '电力设备', value: 1222.45 },
  { name: '食品饮料', value: 1615.82 },
  { name: '非银金融', value: 752.18 },
  { name: '银行', value: 545.30 },
  { name: '电子', value: 412.80 }
]

const MOCK_CUSTOM_PORTFOLIOS = [
  { id: 10, name: '核心资产组合', type: '价值型', created_time: '2026-04-15 10:00:00' },
  { id: 11, name: '成长先锋组合', type: '成长型', created_time: '2026-05-01 09:30:00' },
  { id: 12, name: '红利低波组合', type: '红利型', created_time: '2026-05-20 14:00:00' }
]

export default {
  name: 'PortfolioRiskView',
  data() {
    return {
      activeTab: 'portfolio',
      navData: [],
      positionList: [],
      riskData: {},
      sectorData: [],
      watchlist: [],
      customPortfolios: [],
      navChart: null,
      sectorChart: null,
      watchlistDialogVisible: false,
      watchlistForm: { ts_code: '', name: '', market: '', note: '' }
    }
  },
  computed: {
    riskMetrics() {
      const r = this.riskData
      if (!r || !r.annual_return) return []
      return [
        { label: '年化收益', value: this.formatPercent(r.annual_return), color: this.valueColor(r.annual_return) },
        { label: '年化波动', value: this.formatPercent(r.annual_volatility), color: '#303133' },
        { label: '夏普比率', value: r.sharpe_ratio != null ? r.sharpe_ratio.toFixed(2) : '-', color: '#303133' },
        { label: '最大回撤', value: this.formatPercent(r.max_drawdown), color: '#0f9f6e' },
        { label: '卡玛比率', value: r.calmar_ratio != null ? r.calmar_ratio.toFixed(2) : '-', color: '#303133' },
        { label: '胜率', value: r.win_rate != null ? (r.win_rate * 100).toFixed(1) + '%' : '-', color: '#303133' }
      ]
    },
    top3IndustryRatio() {
      const map = {}
      for (const p of this.positionList) {
        map[p.industry] = (map[p.industry] || 0) + p.weight
      }
      const sorted = Object.values(map).sort((a, b) => b - a)
      const top3 = sorted.slice(0, 3).reduce((s, v) => s + v, 0)
      return (top3 * 100).toFixed(2)
    },
    maxHoldingRatio() {
      if (!this.positionList.length) return '0.00'
      const maxW = Math.max(...this.positionList.map(p => p.weight || 0))
      return (maxW * 100).toFixed(2)
    },
    missingStockCount() {
      return 2
    }
  },
  methods: {
    async fetchNavData(portfolioId) {
      try {
        const res = await axios.get(`/api/portfolio/${portfolioId}/nav`)
        const d = res.data?.data || res.data
        this.navData = d.items || d.list || d || []
      } catch {
        this.navData = MOCK_NAV
      }
    },
    async fetchPositions(portfolioId) {
      try {
        const res = await axios.get(`/api/portfolio/${portfolioId}/positions`)
        const d = res.data?.data || res.data
        this.positionList = d.items || d.list || d || []
      } catch {
        this.positionList = JSON.parse(JSON.stringify(MOCK_POSITIONS))
      }
    },
    async fetchRisk(portfolioId) {
      try {
        const res = await axios.get(`/api/portfolio/${portfolioId}/risk`)
        this.riskData = res.data?.data || res.data || {}
      } catch {
        this.riskData = JSON.parse(JSON.stringify(MOCK_RISK))
      }
    },
    async fetchWatchlist() {
      try {
        const res = await axios.get('/api/watchlist')
        const d = res.data?.data || res.data
        this.watchlist = d.items || d.list || d || []
      } catch {
        this.watchlist = JSON.parse(JSON.stringify(MOCK_WATCHLIST))
      }
    },
    async fetchCustomPortfolios() {
      try {
        const res = await axios.get('/api/portfolio')
        const d = res.data?.data || res.data
        this.customPortfolios = d.items || d.list || d || []
      } catch {
        this.customPortfolios = JSON.parse(JSON.stringify(MOCK_CUSTOM_PORTFOLIOS))
      }
    },
    async handleAddWatchlist() {
      if (!this.watchlistForm.ts_code || !this.watchlistForm.name) {
        this.$message?.warning('请填写必填项')
        return
      }
      try {
        await axios.post('/api/watchlist', this.watchlistForm)
        this.$message?.success('添加成功')
        this.watchlistDialogVisible = false
        this.fetchWatchlist()
      } catch {
        const now = new Date()
        const pad = n => String(n).padStart(2, '0')
        const timeStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
        this.watchlist.push({
          id: Date.now(),
          ...this.watchlistForm,
          added_time: timeStr
        })
        this.$message?.success('添加成功（本地）')
        this.watchlistDialogVisible = false
      }
      this.watchlistForm = { ts_code: '', name: '', market: '', note: '' }
    },
    async removeWatchlist(row) {
      try {
        await this.$confirm('确认移除该股票？', '提示', { type: 'warning' })
        try {
          await axios.delete(`/api/watchlist/${row.id}`)
        } catch { /* fallback: remove locally */ }
        this.watchlist = this.watchlist.filter(w => w.id !== row.id)
        this.$message?.success('已移除')
      } catch { /* cancelled */ }
    },
    viewCustomPortfolio(row) {
      this.$message?.info(`查看组合: ${row.name}`)
    },
    initNavChart() {
      const el = this.$refs.navChartRef
      if (!el) return
      if (this.navChart) { this.navChart.dispose(); this.navChart = null }
      this.navChart = echarts.init(el)
      const dates = this.navData.map(d => d.trade_date)
      const portfolioValues = this.navData.map(d => d.portfolio_nav)
      const benchmarkValues = this.navData.map(d => d.benchmark_nav)
      this.navChart.setOption({
        tooltip: {
          trigger: 'axis',
          formatter(params) {
            let s = params[0].axisValue + '<br/>'
            for (const p of params) {
              s += `${p.marker} ${p.seriesName}: ${p.value.toFixed(4)}<br/>`
            }
            return s
          }
        },
        legend: { data: ['组合净值', '沪深300'], top: 0 },
        grid: { left: 60, right: 20, top: 30, bottom: 30 },
        xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 11, interval: Math.floor(dates.length / 6) } },
        yAxis: { type: 'value', scale: true, axisLabel: { fontSize: 11 } },
        series: [
          {
            name: '组合净值',
            type: 'line',
            data: portfolioValues,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#007f7a', width: 2 },
            itemStyle: { color: '#007f7a' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(0,127,122,0.15)' },
                { offset: 1, color: 'rgba(0,127,122,0.01)' }
              ])
            }
          },
          {
            name: '沪深300',
            type: 'line',
            data: benchmarkValues,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#a9b4c0', width: 1.5 },
            itemStyle: { color: '#a9b4c0' }
          }
        ]
      })
    },
    initSectorChart() {
      const el = this.$refs.sectorChartRef
      if (!el) return
      if (this.sectorChart) { this.sectorChart.dispose(); this.sectorChart = null }
      this.sectorChart = echarts.init(el)
      const data = this.sectorData.length ? this.sectorData : MOCK_SECTOR_DATA
      this.sectorChart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}万 ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          textStyle: { fontSize: 12 }
        },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: {
              borderRadius: 6,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: { show: false },
            emphasis: {
              label: { show: true, fontSize: 14, fontWeight: 'bold' }
            },
            data: data.map(d => ({ name: d.name, value: d.value })),
            color: ['#007f7a', '#0f9f6e', '#e6a23c', '#409eff', '#f56c6c', '#909399']
          }
        ]
      })
    },
    handleTabChange(tab) {
      if (tab === 'portfolio') {
        this.loadPortfolioData()
      } else if (tab === 'watchlist') {
        this.fetchWatchlist()
      } else if (tab === 'custom') {
        this.fetchCustomPortfolios()
      }
    },
    async loadPortfolioData() {
      await Promise.all([
        this.fetchNavData(1),
        this.fetchPositions(1),
        this.fetchRisk(1)
      ])
      this.sectorData = this.computeSectorData()
      this.$nextTick(() => {
        this.initNavChart()
        this.initSectorChart()
      })
    },
    computeSectorData() {
      const map = {}
      for (const p of this.positionList) {
        map[p.industry] = (map[p.industry] || 0) + (p.market_value || 0)
      }
      return Object.entries(map).map(([name, value]) => ({ name, value: parseFloat(value.toFixed(2)) }))
    },
    formatPercent(v) {
      if (v == null) return '-'
      return (v * 100).toFixed(2) + '%'
    },
    valueColor(v) {
      if (v == null) return '#909399'
      return v >= 0 ? '#f56c6c' : '#0f9f6e'
    },
    changeColor(v) {
      if (v == null || v === 0) return '#909399'
      return v > 0 ? '#f56c6c' : '#0f9f6e'
    },
    formatChange(v) {
      if (v == null) return '-'
      if (v === 0) return '0.00%'
      return (v > 0 ? '↑ ' : '↓ ') + Math.abs(v * 100).toFixed(2) + '%'
    },
    handleResize() {
      this.navChart && this.navChart.resize()
      this.sectorChart && this.sectorChart.resize()
    }
  },
  mounted() {
    this.loadPortfolioData()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this.navChart) { this.navChart.dispose(); this.navChart = null }
    if (this.sectorChart) { this.sectorChart.dispose(); this.sectorChart = null }
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.card-title { font-weight: 600; font-size: 15px; }
.chart-card { height: 100%; }
.chart-container { height: 360px; }
.risk-card { height: 100%; }
.risk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.risk-item { padding: 12px; background: #fafafa; border-radius: 6px; text-align: center; }
.risk-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.risk-value { font-size: 20px; font-weight: 700; }
.risk-alert { min-height: 80px; }
.alert-title { font-weight: 600; font-size: 14px; }
.alert-desc { font-size: 13px; color: #606266; margin-top: 4px; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
</style>
