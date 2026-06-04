<template>
  <div class="page-container">
    <div class="page-header">
      <h2>选股信号</h2>
      <p class="page-desc">展示今日信号、策略来源、指标拆解和单股解释。</p>
    </div>

    <el-card shadow="hover">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="今日信号" name="today" />
        <el-tab-pane label="放量信号" name="volume_breakout" />
        <el-tab-pane label="趋势信号" name="ma_trend" />
        <el-tab-pane label="港股信号" name="hk" />
        <el-tab-pane label="信号解释" name="all" />
      </el-tabs>

      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="市场">
          <el-select v-model="filterForm.market" placeholder="全部" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="沪市" value="sh" />
            <el-option label="深市" value="sz" />
            <el-option label="港股" value="hk" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略">
          <el-select v-model="filterForm.strategy_id" placeholder="全部" clearable style="width: 180px">
            <el-option label="放量突破" value="volume_breakout" />
            <el-option label="均线趋势" value="ma_trend" />
            <el-option label="港股趋势" value="hk_trend" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="filterForm.trade_date"
            type="date"
            placeholder="选择日期"
            style="width: 160px"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="信号分">
          <el-select v-model="filterForm.min_score" style="width: 100px">
            <el-option label="≥0" :value="0" />
            <el-option label="≥80" :value="80" />
            <el-option label="≥90" :value="90" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="signalList" stripe size="small" v-loading="tableLoading" :default-sort="{ prop: 'score', order: 'descending' }">
        <el-table-column prop="trade_date" label="日期" width="110" />
        <el-table-column prop="ts_code" label="代码" width="110" />
        <el-table-column prop="name" label="名称" width="90" />
        <el-table-column prop="market" label="市场" width="70">
          <template #default="{ row }">
            {{ marketLabel(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="strategy_id" label="策略" width="120">
          <template #default="{ row }">
            {{ strategyMap[row.strategy_id] || row.strategy_id }}
          </template>
        </el-table-column>
        <el-table-column prop="score" label="信号分" width="80" align="center" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.score >= 80 ? '#f56c6c' : row.score >= 60 ? '#e6a23c' : '#67c23a', fontWeight: 'bold' }">
              {{ row.score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume_score" label="量能" width="70" align="center" />
        <el-table-column prop="trend_score" label="趋势" width="70" align="center" />
        <el-table-column prop="macd_score" label="MACD" width="70" align="center" />
        <el-table-column prop="kdj_score" label="KDJ" width="70" align="center" />
        <el-table-column prop="reason_text" label="入选原因" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetail(row)">详情</el-button>
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
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" title="信号详情" size="520px" :destroy-on-close="true">
      <div v-if="currentSignal" class="detail-content">
        <el-descriptions :column="2" border size="small" class="detail-desc">
          <el-descriptions-item label="交易日期">{{ currentSignal.trade_date }}</el-descriptions-item>
          <el-descriptions-item label="股票代码">{{ currentSignal.ts_code }}</el-descriptions-item>
          <el-descriptions-item label="名称">{{ currentSignal.name }}</el-descriptions-item>
          <el-descriptions-item label="市场">{{ marketLabel(currentSignal) }}</el-descriptions-item>
          <el-descriptions-item label="策略">{{ strategyMap[currentSignal.strategy_id] || currentSignal.strategy_id }}</el-descriptions-item>
          <el-descriptions-item label="信号分">
            <span :style="{ color: currentSignal.score >= 80 ? '#f56c6c' : currentSignal.score >= 60 ? '#e6a23c' : '#67c23a', fontWeight: 'bold' }">
              {{ currentSignal.score }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="量能">{{ currentSignal.volume_score }}</el-descriptions-item>
          <el-descriptions-item label="趋势">{{ currentSignal.trend_score }}</el-descriptions-item>
          <el-descriptions-item label="MACD">{{ currentSignal.macd_score }}</el-descriptions-item>
          <el-descriptions-item label="KDJ">{{ currentSignal.kdj_score }}</el-descriptions-item>
          <el-descriptions-item label="入选原因" :span="2">{{ currentSignal.reason_text }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="detail-section-title">因子快照</h4>
        <div class="chart-placeholder">
          <el-icon :size="32" color="#c0c4cc"><TrendCharts /></el-icon>
          <p>因子快照图表（待接入）</p>
        </div>

        <h4 class="detail-section-title">风险快照</h4>
        <div class="chart-placeholder">
          <el-icon :size="32" color="#c0c4cc"><Warning /></el-icon>
          <p>风险快照信息（待接入）</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import axios from '@/config/axios'
import { TrendCharts, Warning } from '@element-plus/icons-vue'

const API_BASE = '/api/signals'

const MOCK_SIGNALS = [
  { id: 1, trade_date: '2025-06-03', ts_code: '000001.SZ', name: '平安银行', market: 'a', strategy_id: 'volume_breakout', score: 85, volume_score: 92, trend_score: 58, macd_score: 76, kdj_score: 65, reason_text: '成交量突破20日均量2倍，MACD金叉确认', status: 'active' },
  { id: 2, trade_date: '2025-06-03', ts_code: '600519.SH', name: '贵州茅台', market: 'a', strategy_id: 'ma_trend', score: 72, volume_score: 45, trend_score: 88, macd_score: 52, kdj_score: 61, reason_text: '5日均线上穿20日均线，趋势走强', status: 'active' },
  { id: 3, trade_date: '2025-06-02', ts_code: '00700.HK', name: '腾讯控股', market: 'hk', strategy_id: 'hk_trend', score: 90, volume_score: 78, trend_score: 95, macd_score: 82, kdj_score: 70, reason_text: '港股趋势信号触发，量价齐升', status: 'expired' },
  { id: 4, trade_date: '2025-06-02', ts_code: '300750.SZ', name: '宁德时代', market: 'a', strategy_id: 'macd_kdj_resonance', score: 68, volume_score: 55, trend_score: 42, macd_score: 90, kdj_score: 88, reason_text: 'MACD与KDJ同时金叉共振', status: 'active' },
  { id: 5, trade_date: '2025-06-01', ts_code: '002415.SZ', name: '海康威视', market: 'a', strategy_id: 'volume_breakout', score: 55, volume_score: 80, trend_score: 30, macd_score: 45, kdj_score: 38, reason_text: '放量上涨但未突破关键压力位', status: 'dismissed' },
  { id: 6, trade_date: '2025-06-01', ts_code: '00941.HK', name: '中国移动', market: 'hk', strategy_id: 'hk_trend', score: 78, volume_score: 60, trend_score: 82, macd_score: 55, kdj_score: 48, reason_text: '港股均线多头排列', status: 'active' },
  { id: 7, trade_date: '2025-05-30', ts_code: '601318.SH', name: '中国平安', market: 'a', strategy_id: 'ma_trend', score: 62, volume_score: 35, trend_score: 75, macd_score: 40, kdj_score: 55, reason_text: '均线趋势信号触发，短期走强', status: 'expired' },
  { id: 8, trade_date: '2025-05-30', ts_code: '000858.SZ', name: '五粮液', market: 'a', strategy_id: 'macd_kdj_resonance', score: 88, volume_score: 70, trend_score: 65, macd_score: 92, kdj_score: 85, reason_text: 'MACD零轴上方金叉，KDJ超卖回升', status: 'active' }
]

const MOCK_DETAIL = {
  id: 1, trade_date: '2025-06-03', ts_code: '000001.SZ', name: '平安银行', market: 'a',
  strategy_id: 'volume_breakout', score: 85, volume_score: 92, trend_score: 58, macd_score: 76, kdj_score: 65,
  reason_text: '成交量突破20日均量2倍，MACD金叉确认',
  status: 'active',
  factor_snapshot: { volume_ratio: 2.1, macd_diff: 0.35, ma5: 12.5, ma20: 11.8 },
  risk_snapshot: { volatility: 0.023, max_drawdown: -0.05, sharpe: 1.2 }
}

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export default {
  name: 'StockSignalsView',
  components: { TrendCharts, Warning },
  data() {
    return {
      activeTab: 'today',
      filterForm: {
        market: '',
        strategy_id: '',
        trade_date: '',
        min_score: 0
      },
      signalList: [],
      tableLoading: false,
      pagination: { page: 1, pageSize: 10, total: 0 },
      detailVisible: false,
      currentSignal: null,
      strategyMap: {
        volume_breakout: '放量突破',
        ma_trend: '均线趋势',
        macd_kdj_resonance: 'MACD KDJ 共振',
        hk_trend: '港股趋势'
      }
    }
  },
  methods: {
    marketLabel(row) {
      if (row.market === 'hk') return '港股'
      const code = row.ts_code || ''
      if (code.endsWith('.SH')) return '沪市'
      if (code.endsWith('.SZ')) return '深市'
      return row.market === 'a' ? 'A股' : row.market
    },
    applyTabFilter(list) {
      if (this.activeTab === 'today') {
        return list.filter(s => s.trade_date === todayStr())
      }
      if (this.activeTab === 'volume_breakout') {
        return list.filter(s => s.strategy_id === 'volume_breakout')
      }
      if (this.activeTab === 'ma_trend') {
        return list.filter(s => s.strategy_id === 'ma_trend')
      }
      if (this.activeTab === 'hk') {
        return list.filter(s => s.market === 'hk')
      }
      return list
    },
    async fetchSignals() {
      this.tableLoading = true
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.pageSize
        }
        if (this.filterForm.market) params.market = this.filterForm.market
        if (this.filterForm.strategy_id) params.strategy_id = this.filterForm.strategy_id
        if (this.filterForm.trade_date) params.trade_date = this.filterForm.trade_date
        if (this.filterForm.min_score) params.min_score = this.filterForm.min_score

        const res = await axios.get(API_BASE, { params })
        const data = res.data?.data
        if (data) {
          this.signalList = this.applyTabFilter(data.items || data.list || [])
          this.pagination.total = data.total || this.signalList.length
        } else {
          throw new Error('no data')
        }
      } catch {
        let filtered = [...MOCK_SIGNALS]
        if (this.filterForm.market) {
          if (this.filterForm.market === 'sh') {
            filtered = filtered.filter(s => (s.ts_code || '').endsWith('.SH'))
          } else if (this.filterForm.market === 'sz') {
            filtered = filtered.filter(s => (s.ts_code || '').endsWith('.SZ'))
          } else {
            filtered = filtered.filter(s => s.market === this.filterForm.market)
          }
        }
        if (this.filterForm.strategy_id) filtered = filtered.filter(s => s.strategy_id === this.filterForm.strategy_id)
        if (this.filterForm.trade_date) filtered = filtered.filter(s => s.trade_date === this.filterForm.trade_date)
        if (this.filterForm.min_score) filtered = filtered.filter(s => s.score >= this.filterForm.min_score)
        filtered = this.applyTabFilter(filtered)
        filtered.sort((a, b) => b.score - a.score)
        this.pagination.total = filtered.length
        const start = (this.pagination.page - 1) * this.pagination.pageSize
        this.signalList = filtered.slice(start, start + this.pagination.pageSize)
      } finally {
        this.tableLoading = false
      }
    },
    async fetchSignalDetail(id) {
      try {
        const res = await axios.get(`${API_BASE}/${id}`)
        const data = res.data?.data
        if (data) {
          this.currentSignal = data
        } else {
          throw new Error('no data')
        }
      } catch {
        this.currentSignal = MOCK_DETAIL.id === id ? { ...MOCK_DETAIL } : { ...MOCK_DETAIL, id }
      }
    },
    handleTabChange() {
      this.pagination.page = 1
      this.fetchSignals()
    },
    handleQuery() {
      this.pagination.page = 1
      this.fetchSignals()
    },
    handleReset() {
      this.filterForm = { market: '', strategy_id: '', trade_date: '', min_score: 0 }
      this.pagination.page = 1
      this.fetchSignals()
    },
    openDetail(row) {
      this.fetchSignalDetail(row.id)
      this.detailVisible = true
    }
  },
  mounted() {
    this.fetchSignals()
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.filter-form { margin-bottom: 12px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 12px; }
.detail-content { padding: 0 8px; }
.detail-desc { margin-bottom: 20px; }
.detail-section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 20px 0 10px; }
.chart-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 120px; background: #fafafa; border: 1px dashed #dcdfe6; border-radius: 4px; color: #c0c4cc; }
.chart-placeholder p { margin: 8px 0 0; font-size: 13px; color: #909399; }
</style>
