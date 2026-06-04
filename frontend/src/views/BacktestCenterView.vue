<template>
  <div class="page-container">
    <div class="page-header">
      <h2>回测中心</h2>
      <p class="page-desc">回测任务、净值曲线、风险指标、持仓和交易明细集中查看。</p>
    </div>

    <!-- Filter Card -->
    <el-card class="filter-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="回测任务" name="tasks" />
        <el-tab-pane label="回测报告库" name="reports" />
      </el-tabs>
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="filterForm.start_date"
            type="date"
            placeholder="开始日期"
            style="width: 160px"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filterForm.end_date"
            type="date"
            placeholder="结束日期"
            style="width: 160px"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="策略">
          <el-select v-model="filterForm.strategy_id" placeholder="全部" clearable style="width: 180px">
            <el-option
              v-for="s in strategyOptions"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="Pending" value="pending" />
            <el-option label="Running" value="running" />
            <el-option label="Success" value="success" />
            <el-option label="Failed" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button type="success" @click="openCreateDialog">新建回测</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Backtest Table -->
    <el-card shadow="hover">
      <template #header><span class="card-title">回测任务列表</span></template>
      <el-table :data="backtestList" stripe size="small" v-loading="tableLoading" highlight-current-row @current-change="handleRowSelect">
        <el-table-column prop="strategy_id" label="策略名" width="160">
          <template #default="{ row }">
            {{ strategyNameMap[row.strategy_id] || row.strategy_id }}
          </template>
        </el-table-column>
        <el-table-column label="回测区间" width="200">
          <template #default="{ row }">
            {{ row.start_date }} ~ {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="annual_return" label="年化收益" width="110" align="right">
          <template #default="{ row }">
            <span :style="{ color: valueColor(row.annual_return), fontWeight: 'bold' }">
              {{ formatPercent(row.annual_return) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="sharpe_ratio" label="夏普" width="90" align="right">
          <template #default="{ row }">
            {{ row.sharpe_ratio != null ? row.sharpe_ratio.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="max_drawdown" label="最大回撤" width="110" align="right">
          <template #default="{ row }">
            <span style="color: #0f9f6e; font-weight: bold">
              {{ formatPercent(row.max_drawdown) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="selectBacktest(row)">查看</el-button>
            <el-button link type="info" size="small" @click="openDetailDrawer(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchBacktests"
          @current-change="fetchBacktests"
        />
      </div>
    </el-card>

    <!-- Detail Area (selected backtest) -->
    <div v-if="selectedBacktest" class="detail-section">
      <el-row :gutter="16">
        <!-- NAV Chart (2/3) -->
        <el-col :span="16">
          <el-card shadow="hover" class="chart-card">
            <template #header><span class="card-title">净值曲线</span></template>
            <div ref="navChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <!-- Risk Metrics (1/3) -->
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

      <!-- Positions Table -->
      <el-card shadow="hover" style="margin-top: 16px">
        <template #header><span class="card-title">持仓明细</span></template>
        <el-table :data="positionList" stripe size="small" v-loading="positionsLoading">
          <el-table-column prop="ts_code" label="股票代码" width="120" />
          <el-table-column prop="name" label="名称" width="100" />
          <el-table-column prop="trade_date" label="日期" width="110" />
          <el-table-column prop="weight" label="权重" width="100" align="right">
            <template #default="{ row }">
              {{ row.weight != null ? (row.weight * 100).toFixed(1) + '%' : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="shares" label="持仓数量" width="100" align="right" />
          <el-table-column prop="market_value" label="市值" width="120" align="right">
            <template #default="{ row }">
              {{ row.market_value != null ? row.market_value.toLocaleString() : '-' }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- Trades Table -->
      <el-card shadow="hover" style="margin-top: 16px">
        <template #header><span class="card-title">交易明细</span></template>
        <el-table :data="tradeList" stripe size="small" v-loading="tradesLoading">
          <el-table-column prop="trade_date" label="日期" width="110" />
          <el-table-column prop="ts_code" label="股票代码" width="120" />
          <el-table-column prop="name" label="名称" width="100" />
          <el-table-column prop="direction" label="方向" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="row.direction === 'buy' ? 'danger' : 'success'" effect="plain">
                {{ row.direction === 'buy' ? '买入' : '卖出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="100" align="right">
            <template #default="{ row }">
              {{ row.price != null ? row.price.toFixed(2) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="shares" label="数量" width="80" align="right" />
          <el-table-column prop="amount" label="金额" width="120" align="right">
            <template #default="{ row }">
              {{ row.amount != null ? row.amount.toLocaleString() : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="commission" label="手续费" width="100" align="right">
            <template #default="{ row }">
              {{ row.commission != null ? row.commission.toFixed(2) : '-' }}
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="tradePagination.page"
            v-model:page-size="tradePagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="tradePagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="fetchTrades"
            @current-change="fetchTrades"
          />
        </div>
      </el-card>
    </div>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailDrawerVisible" title="回测详情" size="520px" :destroy-on-close="true">
      <div v-if="detailBacktest" class="detail-content">
        <el-descriptions :column="2" border size="small" class="detail-desc">
          <el-descriptions-item label="策略">{{ strategyNameMap[detailBacktest.strategy_id] || detailBacktest.strategy_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag size="small" :type="statusType(detailBacktest.status)">{{ statusLabel(detailBacktest.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ detailBacktest.start_date }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ detailBacktest.end_date }}</el-descriptions-item>
          <el-descriptions-item label="年化收益">
            <span :style="{ color: valueColor(detailBacktest.annual_return), fontWeight: 'bold' }">
              {{ formatPercent(detailBacktest.annual_return) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="夏普比率">
            {{ detailBacktest.sharpe_ratio != null ? detailBacktest.sharpe_ratio.toFixed(2) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="最大回撤">
            <span style="color: #0f9f6e; font-weight: bold">{{ formatPercent(detailBacktest.max_drawdown) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="卡玛比率">
            {{ detailBacktest.calmar_ratio != null ? detailBacktest.calmar_ratio.toFixed(2) : '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>

    <!-- Create Dialog -->
    <el-dialog v-model="createDialogVisible" title="新建回测任务" width="600px" :close-on-click-modal="false">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="策略" required>
          <el-select v-model="createForm.strategy_id" placeholder="选择策略" style="width: 100%">
            <el-option
              v-for="s in strategyOptions"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="策略版本号">
          <el-input-number v-model="createForm.version_id" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="createForm.start_date"
            type="date"
            placeholder="开始日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker
            v-model="createForm.end_date"
            type="date"
            placeholder="结束日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="参数">
          <el-input v-model="createForm.params" placeholder='可选，JSON 格式，如 {"threshold": 0.05}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateBacktest" :loading="createLoading">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from '@/config/axios'

const API_BASE = '/api/backtests'

const MOCK_STRATEGIES = [
  { id: 'volume_breakout', name: '放量突破' },
  { id: 'ma_trend', name: '均线趋势' },
  { id: 'macd_kdj_resonance', name: 'MACD KDJ 共振' },
  { id: 'mean_reversion', name: '均值回归' }
]

const MOCK_BACKTESTS = [
  { id: 1, strategy_id: 'volume_breakout', start_date: '2024-01-01', end_date: '2024-12-31', status: 'success', annual_return: 0.185, sharpe_ratio: 1.52, max_drawdown: -0.082, calmar_ratio: 2.26, annual_volatility: 0.122, win_rate: 0.58 },
  { id: 2, strategy_id: 'ma_trend', start_date: '2024-03-01', end_date: '2024-12-31', status: 'success', annual_return: 0.097, sharpe_ratio: 0.89, max_drawdown: -0.126, calmar_ratio: 0.77, annual_volatility: 0.109, win_rate: 0.52 },
  { id: 3, strategy_id: 'macd_kdj_resonance', start_date: '2024-02-01', end_date: '2024-11-30', status: 'success', annual_return: -0.034, sharpe_ratio: -0.31, max_drawdown: -0.198, calmar_ratio: -0.17, annual_volatility: 0.148, win_rate: 0.44 },
  { id: 4, strategy_id: 'mean_reversion', start_date: '2024-01-15', end_date: '2024-10-31', status: 'running', annual_return: 0.062, sharpe_ratio: 0.55, max_drawdown: -0.045, calmar_ratio: 1.38, annual_volatility: 0.088, win_rate: 0.55 },
  { id: 5, strategy_id: 'volume_breakout', start_date: '2024-06-01', end_date: '2024-12-31', status: 'pending', annual_return: null, sharpe_ratio: null, max_drawdown: null, calmar_ratio: null, annual_volatility: null, win_rate: null },
  { id: 6, strategy_id: 'ma_trend', start_date: '2023-06-01', end_date: '2024-05-31', status: 'failed', annual_return: null, sharpe_ratio: null, max_drawdown: null, calmar_ratio: null, annual_volatility: null, win_rate: null },
  { id: 7, strategy_id: 'macd_kdj_resonance', start_date: '2024-04-01', end_date: '2024-12-31', status: 'success', annual_return: 0.142, sharpe_ratio: 1.18, max_drawdown: -0.095, calmar_ratio: 1.49, annual_volatility: 0.115, win_rate: 0.56 }
]

function generateMockNav() {
  const data = []
  let strategyNav = 1.0
  let benchmarkNav = 1.0
  const startDate = new Date('2024-01-02')
  for (let i = 0; i < 250; i++) {
    const d = new Date(startDate)
    d.setDate(d.getDate() + i)
    const dateStr = d.toISOString().slice(0, 10)
    const dow = d.getDay()
    if (dow === 0 || dow === 6) continue
    strategyNav *= (1 + (Math.random() - 0.47) * 0.02)
    benchmarkNav *= (1 + (Math.random() - 0.49) * 0.012)
    data.push({
      trade_date: dateStr,
      strategy_nav: parseFloat(strategyNav.toFixed(4)),
      benchmark_nav: parseFloat(benchmarkNav.toFixed(4))
    })
  }
  return data
}

const MOCK_NAV = generateMockNav()

const MOCK_POSITIONS = [
  { ts_code: '000001.SZ', name: '平安银行', trade_date: '2024-12-31', weight: 0.15, shares: 5000, market_value: 52500 },
  { ts_code: '600519.SH', name: '贵州茅台', trade_date: '2024-12-31', weight: 0.25, shares: 100, market_value: 172600 },
  { ts_code: '300750.SZ', name: '宁德时代', trade_date: '2024-12-31', weight: 0.20, shares: 300, market_value: 59700 },
  { ts_code: '601318.SH', name: '中国平安', trade_date: '2024-12-31', weight: 0.20, shares: 800, market_value: 36800 },
  { ts_code: '000858.SZ', name: '五粮液', trade_date: '2024-12-31', weight: 0.20, shares: 400, market_value: 55200 }
]

const MOCK_TRADES = [
  { id: 1, trade_date: '2024-01-15', ts_code: '000001.SZ', name: '平安银行', direction: 'buy', price: 10.50, shares: 5000, amount: 52500, commission: 26.25 },
  { id: 2, trade_date: '2024-01-15', ts_code: '600519.SH', name: '贵州茅台', direction: 'buy', price: 1726.00, shares: 100, amount: 172600, commission: 86.30 },
  { id: 3, trade_date: '2024-02-05', ts_code: '300750.SZ', name: '宁德时代', direction: 'buy', price: 199.00, shares: 300, amount: 59700, commission: 29.85 },
  { id: 4, trade_date: '2024-03-12', ts_code: '601318.SH', name: '中国平安', direction: 'buy', price: 46.00, shares: 800, amount: 36800, commission: 18.40 },
  { id: 5, trade_date: '2024-03-28', ts_code: '000858.SZ', name: '五粮液', direction: 'buy', price: 138.00, shares: 400, amount: 55200, commission: 27.60 },
  { id: 6, trade_date: '2024-05-10', ts_code: '000001.SZ', name: '平安银行', direction: 'sell', price: 11.20, shares: 2000, amount: 22400, commission: 11.20 },
  { id: 7, trade_date: '2024-06-03', ts_code: '600519.SH', name: '贵州茅台', direction: 'sell', price: 1698.00, shares: 50, amount: 84900, commission: 42.45 },
  { id: 8, trade_date: '2024-07-15', ts_code: '300750.SZ', name: '宁德时代', direction: 'sell', price: 185.00, shares: 150, amount: 27750, commission: 13.88 },
  { id: 9, trade_date: '2024-08-01', ts_code: '601318.SH', name: '中国平安', direction: 'sell', price: 42.50, shares: 400, amount: 17000, commission: 8.50 },
  { id: 10, trade_date: '2024-08-20', ts_code: '000858.SZ', name: '五粮液', direction: 'sell', price: 125.00, shares: 200, amount: 25000, commission: 12.50 },
  { id: 11, trade_date: '2024-09-05', ts_code: '000001.SZ', name: '平安银行', direction: 'buy', price: 10.80, shares: 3000, amount: 32400, commission: 16.20 },
  { id: 12, trade_date: '2024-10-10', ts_code: '600519.SH', name: '贵州茅台', direction: 'buy', price: 1710.00, shares: 50, amount: 85500, commission: 42.75 },
  { id: 13, trade_date: '2024-10-25', ts_code: '300750.SZ', name: '宁德时代', direction: 'buy', price: 195.00, shares: 200, amount: 39000, commission: 19.50 },
  { id: 14, trade_date: '2024-11-08', ts_code: '601318.SH', name: '中国平安', direction: 'buy', price: 48.00, shares: 500, amount: 24000, commission: 12.00 },
  { id: 15, trade_date: '2024-11-20', ts_code: '000858.SZ', name: '五粮液', direction: 'buy', price: 135.00, shares: 200, amount: 27000, commission: 13.50 },
  { id: 16, trade_date: '2024-12-05', ts_code: '000001.SZ', name: '平安银行', direction: 'sell', price: 11.50, shares: 1000, amount: 11500, commission: 5.75 },
  { id: 17, trade_date: '2024-12-12', ts_code: '300750.SZ', name: '宁德时代', direction: 'sell', price: 210.00, shares: 100, amount: 21000, commission: 10.50 },
  { id: 18, trade_date: '2024-12-20', ts_code: '601318.SH', name: '中国平安', direction: 'sell', price: 50.00, shares: 300, amount: 15000, commission: 7.50 },
  { id: 19, trade_date: '2024-12-26', ts_code: '600519.SH', name: '贵州茅台', direction: 'sell', price: 1735.00, shares: 30, amount: 52050, commission: 26.03 },
  { id: 20, trade_date: '2024-12-30', ts_code: '000858.SZ', name: '五粮液', direction: 'sell', price: 140.00, shares: 100, amount: 14000, commission: 7.00 }
]

export default {
  name: 'BacktestCenterView',
  data() {
    return {
      activeTab: 'tasks',
      filterForm: {
        start_date: '',
        end_date: '',
        strategy_id: '',
        status: ''
      },
      strategyOptions: [],
      backtestList: [],
      tableLoading: false,
      pagination: { page: 1, pageSize: 10, total: 0 },
      selectedBacktest: null,
      navChart: null,
      navData: [],
      positionList: [],
      positionsLoading: false,
      tradeList: [],
      tradesLoading: false,
      tradePagination: { page: 1, pageSize: 10, total: 0 },
      detailDrawerVisible: false,
      detailBacktest: null,
      createDialogVisible: false,
      createLoading: false,
      createForm: {
        strategy_id: '',
        version_id: 1,
        start_date: '',
        end_date: '',
        params: ''
      }
    }
  },
  computed: {
    strategyNameMap() {
      const map = {}
      for (const s of this.strategyOptions) {
        map[s.id] = s.name
      }
      return map
    },
    riskMetrics() {
      const b = this.selectedBacktest
      if (!b) return []
      return [
        { label: '年化收益', value: this.formatPercent(b.annual_return), color: this.valueColor(b.annual_return) },
        { label: '年化波动', value: this.formatPercent(b.annual_volatility), color: '#303133' },
        { label: '夏普比率', value: b.sharpe_ratio != null ? b.sharpe_ratio.toFixed(2) : '-', color: '#303133' },
        { label: '卡玛比率', value: b.calmar_ratio != null ? b.calmar_ratio.toFixed(2) : '-', color: '#303133' },
        { label: '胜率', value: b.win_rate != null ? (b.win_rate * 100).toFixed(1) + '%' : '-', color: '#303133' },
        { label: '最大回撤', value: this.formatPercent(b.max_drawdown), color: '#0f9f6e' }
      ]
    }
  },
  methods: {
    async fetchStrategies() {
      try {
        const res = await axios.get('/api/strategies', { params: { page: 1, page_size: 100 } })
        const d = res.data?.data || res.data
        this.strategyOptions = d.items || d.list || d || []
      } catch {
        this.strategyOptions = MOCK_STRATEGIES
      }
    },
    async fetchBacktests() {
      this.tableLoading = true
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.pageSize
        }
        if (this.filterForm.strategy_id) params.strategy_id = this.filterForm.strategy_id
        if (this.filterForm.status) params.status = this.filterForm.status
        const res = await axios.get(API_BASE, { params })
        const d = res.data?.data || res.data || {}
        this.backtestList = d.items || d.list || []
        this.pagination.total = d.total || this.backtestList.length
      } catch {
        let filtered = [...MOCK_BACKTESTS]
        if (this.filterForm.strategy_id) filtered = filtered.filter(b => b.strategy_id === this.filterForm.strategy_id)
        if (this.filterForm.status) filtered = filtered.filter(b => b.status === this.filterForm.status)
        if (this.filterForm.start_date) filtered = filtered.filter(b => b.start_date >= this.filterForm.start_date)
        if (this.filterForm.end_date) filtered = filtered.filter(b => b.end_date <= this.filterForm.end_date)
        this.pagination.total = filtered.length
        const start = (this.pagination.page - 1) * this.pagination.pageSize
        this.backtestList = filtered.slice(start, start + this.pagination.pageSize)
      } finally {
        this.tableLoading = false
      }
    },
    async fetchNavData(backtestId) {
      try {
        const res = await axios.get(`${API_BASE}/${backtestId}/nav`)
        const d = res.data?.data || res.data
        this.navData = d.items || d.list || d || []
      } catch {
        this.navData = MOCK_NAV
      }
    },
    async fetchPositions(backtestId) {
      this.positionsLoading = true
      try {
        const res = await axios.get(`${API_BASE}/${backtestId}/positions`)
        const d = res.data?.data || res.data
        this.positionList = d.items || d.list || d || []
      } catch {
        this.positionList = MOCK_POSITIONS
      } finally {
        this.positionsLoading = false
      }
    },
    async fetchTrades() {
      if (!this.selectedBacktest) return
      this.tradesLoading = true
      try {
        const params = {
          page: this.tradePagination.page,
          page_size: this.tradePagination.pageSize
        }
        const res = await axios.get(`${API_BASE}/${this.selectedBacktest.id}/trades`, { params })
        const d = res.data?.data || res.data || {}
        this.tradeList = d.items || d.list || []
        this.tradePagination.total = d.total || this.tradeList.length
      } catch {
        const start = (this.tradePagination.page - 1) * this.tradePagination.pageSize
        this.tradePagination.total = MOCK_TRADES.length
        this.tradeList = MOCK_TRADES.slice(start, start + this.tradePagination.pageSize)
      } finally {
        this.tradesLoading = false
      }
    },
    async fetchBacktestDetail(backtestId) {
      try {
        const res = await axios.get(`${API_BASE}/${backtestId}`)
        return res.data?.data || res.data || null
      } catch {
        const found = MOCK_BACKTESTS.find(b => b.id === backtestId)
        return found || null
      }
    },
    initNavChart() {
      const el = this.$refs.navChartRef
      if (!el) return
      if (this.navChart) { this.navChart.dispose(); this.navChart = null }
      this.navChart = echarts.init(el)
      const dates = this.navData.map(d => d.trade_date)
      const strategyValues = this.navData.map(d => d.strategy_nav)
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
        legend: { data: ['策略净值', '基准净值'], top: 0 },
        grid: { left: 60, right: 20, top: 30, bottom: 30 },
        xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 11, interval: Math.floor(dates.length / 6) } },
        yAxis: { type: 'value', scale: true, axisLabel: { fontSize: 11 } },
        series: [
          {
            name: '策略净值',
            type: 'line',
            data: strategyValues,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#007f7a', width: 2 },
            itemStyle: { color: '#007f7a' }
          },
          {
            name: '基准净值',
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
    handleQuery() {
      this.pagination.page = 1
      this.fetchBacktests()
    },
    handleTabChange() {
      this.pagination.page = 1
      this.fetchBacktests()
    },
    async selectBacktest(row) {
      const detail = await this.fetchBacktestDetail(row.id)
      this.selectedBacktest = detail || row
      this.tradePagination.page = 1
      await this.fetchNavData(row.id)
      this.$nextTick(() => { this.initNavChart() })
      this.fetchPositions(row.id)
      this.fetchTrades()
    },
    handleRowSelect(row) {
      if (row) this.selectBacktest(row)
    },
    async openDetailDrawer(row) {
      const detail = await this.fetchBacktestDetail(row.id)
      this.detailBacktest = detail || row
      this.detailDrawerVisible = true
    },
    openCreateDialog() {
      this.createForm = { strategy_id: '', version_id: 1, start_date: '', end_date: '', params: '' }
      this.createDialogVisible = true
    },
    async handleCreateBacktest() {
      if (!this.createForm.strategy_id || !this.createForm.start_date || !this.createForm.end_date) {
        this.$message?.warning('请填写必填项')
        return
      }
      this.createLoading = true
      const body = {
        strategy_id: this.createForm.strategy_id,
        version_id: this.createForm.version_id,
        start_date: this.createForm.start_date,
        end_date: this.createForm.end_date
      }
      if (this.createForm.params) {
        try {
          body.params = JSON.parse(this.createForm.params)
        } catch {
          body.params = this.createForm.params
        }
      }
      try {
        await axios.post(API_BASE, body)
        this.$message?.success('回测任务已创建')
        this.createDialogVisible = false
        this.fetchBacktests()
      } catch {
        this.$message?.warning('API 不可用，模拟创建成功')
        this.createDialogVisible = false
      } finally {
        this.createLoading = false
      }
    },
    statusType(s) {
      const map = { pending: 'warning', running: '', success: 'success', failed: 'danger' }
      return map[s] || 'info'
    },
    statusLabel(s) {
      const map = { pending: 'Pending', running: 'Running', success: 'Success', failed: 'Failed' }
      return map[s] || s
    },
    valueColor(v) {
      if (v == null) return '#909399'
      return v >= 0 ? '#f56c6c' : '#0f9f6e'
    },
    formatPercent(v) {
      if (v == null) return '-'
      return (v * 100).toFixed(2) + '%'
    },
    handleResize() {
      this.navChart && this.navChart.resize()
    }
  },
  mounted() {
    this.fetchStrategies()
    this.fetchBacktests()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this.navChart) { this.navChart.dispose(); this.navChart = null }
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.filter-card { margin-bottom: 16px; }
.card-title { font-weight: 600; font-size: 15px; }
.pagination-wrap { display: flex; justify-content: flex-end; padding: 16px 0 0; }
.detail-section { margin-top: 16px; }
.chart-card { height: 100%; }
.chart-container { height: 360px; }
.risk-card { height: 100%; }
.risk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.risk-item { padding: 12px; background: #fafafa; border-radius: 6px; text-align: center; }
.risk-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.risk-value { font-size: 20px; font-weight: 700; }
.detail-content { padding: 0 4px; }
.detail-desc { margin-bottom: 16px; }
</style>
