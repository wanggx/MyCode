<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据中心</h2>
      <p class="page-desc">关注行情、缺失、补录和同步质量，不把数据问题带进策略。</p>
    </div>

    <el-card shadow="hover" class="main-card">
      <div class="filters">
        <el-select v-model="filterForm.market" placeholder="全部市场" clearable style="width: 120px">
          <el-option label="A股" value="a" />
          <el-option label="港股" value="hk" />
        </el-select>
        <el-select v-model="filterForm.dataType" placeholder="行情数据" clearable style="width: 140px">
          <el-option label="行情数据" value="daily" />
          <el-option label="基础资料" value="basic" />
          <el-option label="财务数据" value="finance" />
        </el-select>
        <el-date-picker
          v-model="filterForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始"
          end-placeholder="结束"
          style="width: 240px"
          value-format="YYYY-MM-DD"
        />
        <el-input v-model="filterForm.tsCode" placeholder="输入股票代码" style="width: 150px" clearable />
        <el-button type="primary" @click="handleQuery">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <div class="grid three">
        <div class="grid-item">
          <div class="card-head">
            <span class="card-title">数据完整率趋势</span>
            <span class="tag green">{{ completenessLabel }}</span>
          </div>
          <div ref="trendChartRef" class="chart-small"></div>
        </div>

        <div class="grid-item">
          <div class="card-head">
            <span class="card-title">缺失数据日历</span>
          </div>
          <div class="calendar-area">
            <el-calendar v-model="calendarDate">
              <template #date-cell="{ data }">
                <div class="calendar-cell" :class="{ 'is-missing': isMissingDate(data.day) }">
                  {{ data.day.split('-')[2] }}
                </div>
              </template>
            </el-calendar>
          </div>
        </div>

        <div class="grid-item">
          <div class="card-head">
            <span class="card-title">最新同步记录</span>
            <el-button type="primary" size="small" @click="handleSyncStockList">同步股票列表</el-button>
          </div>
          <el-table :data="syncRecords" size="small" class="sync-table">
            <el-table-column prop="start_time" label="开始时间" width="90" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="status" label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="success">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="completeness" label="完整率" align="center">
              <template #default="{ row }">
                <span class="green">{{ row.completeness }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="issue-card">
      <template #header>
        <div class="card-head">
          <span class="card-title">数据问题列表</span>
          <el-button type="primary" :icon="Refresh" @click="handleScan" :loading="scanLoading" size="small">触发数据扫描</el-button>
        </div>
      </template>
      <el-table :data="issueList" stripe size="small" v-loading="tableLoading">
        <el-table-column prop="issue_code" label="问题编号" width="140" />
        <el-table-column prop="market" label="市场" width="80">
          <template #default="{ row }">
            {{ row.market === 'a' ? 'A股' : row.market === 'hk' ? '港股' : row.market }}
          </template>
        </el-table-column>
        <el-table-column prop="data_type" label="数据类型" width="100">
          <template #default="{ row }">
            {{ dataTypeMap[row.data_type] || row.data_type }}
          </template>
        </el-table-column>
        <el-table-column label="日期范围" width="180">
          <template #default="{ row }">
            {{ row.start_date }} ~ {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column prop="missing_count" label="缺失数量" width="90" align="center" />
        <el-table-column prop="severity" label="严重级别" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="severityType(row.severity)" effect="dark">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetail(row)">查看</el-button>
            <el-button link type="success" size="small" @click="openRepair(row)" :disabled="row.status !== 'open'">修复</el-button>
            <el-button link type="warning" size="small" @click="handleIgnore(row)" :disabled="row.status !== 'open'">跳过</el-button>
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

    <el-drawer v-model="detailVisible" title="问题详情" size="520px" :destroy-on-close="true">
      <div v-if="currentIssue" class="detail-content">
        <el-descriptions :column="2" border size="small" class="detail-desc">
          <el-descriptions-item label="问题编号">{{ currentIssue.issue_code }}</el-descriptions-item>
          <el-descriptions-item label="市场">{{ currentIssue.market === 'a' ? 'A股' : currentIssue.market === 'hk' ? '港股' : currentIssue.market }}</el-descriptions-item>
          <el-descriptions-item label="数据类型">{{ dataTypeMap[currentIssue.data_type] || currentIssue.data_type }}</el-descriptions-item>
          <el-descriptions-item label="严重级别">
            <el-tag size="small" :type="severityType(currentIssue.severity)" effect="dark">{{ currentIssue.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag size="small" :type="statusType(currentIssue.status)">{{ statusLabel(currentIssue.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="缺失数量">{{ currentIssue.missing_count }}</el-descriptions-item>
          <el-descriptions-item label="起始日期">{{ currentIssue.start_date }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ currentIssue.end_date }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="detail-section-title">缺失股票明细</h4>
        <el-table :data="detailMissingList" size="small" stripe max-height="260">
          <el-table-column prop="trade_date" label="交易日期" width="110" />
          <el-table-column prop="ts_code" label="股票代码" width="110" />
          <el-table-column prop="issue_type" label="问题类型" width="100" />
          <el-table-column prop="message" label="说明" min-width="140" show-overflow-tooltip />
        </el-table>

        <h4 class="detail-section-title">影响范围评估</h4>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="受影响策略数">{{ currentIssue.affected_strategies || 0 }}</el-descriptions-item>
          <el-descriptions-item label="受影响股票数">{{ currentIssue.missing_count }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag size="small" :type="severityType(currentIssue.severity)" effect="dark">{{ currentIssue.severity }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>

    <el-dialog v-model="repairVisible" title="修复确认" width="480px" :close-on-click-modal="false">
      <el-form label-width="100px">
        <el-form-item label="问题编号">
          <span>{{ repairIssue?.issue_code }}</span>
        </el-form-item>
        <el-form-item label="修复方式">
          <el-radio-group v-model="repairForm.repairMode">
            <el-radio value="repair_missing_only">仅补缺失</el-radio>
            <el-radio value="reload_date">覆盖重拉当日</el-radio>
            <el-radio value="ignore">忽略</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="repairVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRepair" :loading="repairLoading">确认修复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from '@/config/axios'
import { Refresh } from '@element-plus/icons-vue'

const API_BASE = '/api/data'

const MOCK_SUMMARY = {
  completeness_rate: 96.8,
  completeness_trend: 1.2,
  open_issues: 7,
  high_severity_issues: 2,
  affected_strategies: 3,
  trend: [
    { date: '05-20', rate: 94.2 }, { date: '05-21', rate: 95.1 },
    { date: '05-22', rate: 93.8 }, { date: '05-23', rate: 95.6 },
    { date: '05-24', rate: 96.0 }, { date: '05-25', rate: 95.3 },
    { date: '05-26', rate: 96.1 }, { date: '05-27', rate: 96.5 },
    { date: '05-28', rate: 95.9 }, { date: '05-29', rate: 96.8 }
  ]
}

const MOCK_ISSUES = [
  { id: 1, issue_code: 'ISS-20260528-001', market: 'a', data_type: 'daily', start_date: '2026-05-20', end_date: '2026-05-28', missing_count: 12, severity: 'high', status: 'open', affected_strategies: 2 },
  { id: 2, issue_code: 'ISS-20260528-002', market: 'a', data_type: 'finance', start_date: '2026-05-15', end_date: '2026-05-28', missing_count: 5, severity: 'medium', status: 'open', affected_strategies: 1 },
  { id: 3, issue_code: 'ISS-20260527-003', market: 'hk', data_type: 'daily', start_date: '2026-05-25', end_date: '2026-05-27', missing_count: 3, severity: 'low', status: 'open', affected_strategies: 0 },
  { id: 4, issue_code: 'ISS-20260526-004', market: 'a', data_type: 'index', start_date: '2026-05-01', end_date: '2026-05-26', missing_count: 8, severity: 'high', status: 'open', affected_strategies: 3 },
  { id: 5, issue_code: 'ISS-20260525-005', market: 'a', data_type: 'daily', start_date: '2026-05-10', end_date: '2026-05-25', missing_count: 2, severity: 'low', status: 'repaired', affected_strategies: 0 },
  { id: 6, issue_code: 'ISS-20260524-006', market: 'hk', data_type: 'daily', start_date: '2026-05-20', end_date: '2026-05-24', missing_count: 6, severity: 'medium', status: 'ignored', affected_strategies: 1 },
  { id: 7, issue_code: 'ISS-20260523-007', market: 'a', data_type: 'finance', start_date: '2026-05-15', end_date: '2026-05-23', missing_count: 1, severity: 'low', status: 'repaired', affected_strategies: 0 }
]

const MOCK_MISSING_DETAIL = [
  { trade_date: '2026-05-28', ts_code: '000001.SZ', issue_type: 'missing', message: '日线数据缺失' },
  { trade_date: '2026-05-28', ts_code: '600036.SH', issue_type: 'missing', message: '日线数据缺失' },
  { trade_date: '2026-05-27', ts_code: '000651.SZ', issue_type: 'incomplete', message: '数据不完整，缺少成交量' },
  { trade_date: '2026-05-26', ts_code: '601318.SH', issue_type: 'missing', message: '日线数据缺失' },
  { trade_date: '2026-05-25', ts_code: '000858.SZ', issue_type: 'anomaly', message: '收盘价异常偏离' }
]

const MOCK_SYNC_RECORDS = [
  { start_time: '08:45', type: '行情数据', status: '成功', completeness: '98.72%' },
  { start_time: '08:10', type: '基础资料', status: '成功', completeness: '98.41%' },
  { start_time: '07:35', type: '行情数据', status: '成功', completeness: '98.21%' }
]

const MISSING_DATES = ['2026-05-22', '2026-05-25', '2026-05-28']

export default {
  name: 'DataCenterView',
  components: {},
  data() {
    return {
      Refresh,
      summary: null,
      trendChart: null,
      filterForm: {
        market: '',
        dataType: '',
        dateRange: null,
        tsCode: ''
      },
      issueList: [],
      tableLoading: false,
      pagination: { page: 1, pageSize: 10, total: 0 },
      detailVisible: false,
      currentIssue: null,
      detailMissingList: [],
      repairVisible: false,
      repairIssue: null,
      repairForm: { repairMode: 'repair_missing_only' },
      repairLoading: false,
      scanLoading: false,
      dataTypeMap: { daily: '日线行情', finance: '财务数据', index: '指数数据', basic: '基础资料' },
      syncRecords: [],
      calendarDate: new Date()
    }
  },
  computed: {
    completenessLabel() {
      const s = this.summary || MOCK_SUMMARY
      return s.completeness_rate ? s.completeness_rate.toFixed(2) + '%' : '98.60%'
    }
  },
  methods: {
    async fetchSummary() {
      try {
        const res = await axios.get(`${API_BASE}/quality-summary`)
        this.summary = res.data?.data || res.data || null
      } catch {
        this.summary = MOCK_SUMMARY
      }
    },
    async fetchIssues() {
      this.tableLoading = true
      try {
        const params = {
          market: this.filterForm.market || undefined,
          severity: undefined,
          status: undefined,
          page: this.pagination.page,
          page_size: this.pagination.pageSize
        }
        const res = await axios.get(`${API_BASE}/issues`, { params })
        const d = res.data?.data || res.data || {}
        this.issueList = d.items || d.list || []
        this.pagination.total = d.total || this.issueList.length
      } catch {
        this.issueList = MOCK_ISSUES
        this.pagination.total = MOCK_ISSUES.length
      } finally {
        this.tableLoading = false
      }
    },
    async fetchIssueDetail(id) {
      try {
        const res = await axios.get(`${API_BASE}/issues/${id}`)
        return res.data?.data || res.data || null
      } catch {
        return null
      }
    },
    async fetchSyncRecords() {
      try {
        const res = await axios.get(`${API_BASE}/sync-records`)
        const d = res.data?.data || res.data
        this.syncRecords = d.items || d.list || d || []
      } catch {
        this.syncRecords = MOCK_SYNC_RECORDS
      }
    },
    initTrendChart() {
      const el = this.$refs.trendChartRef
      if (!el) return
      this.trendChart = echarts.init(el)
      const s = this.summary || MOCK_SUMMARY
      const trendData = s.trend || MOCK_SUMMARY.trend
      const dates = trendData.map(t => t.date)
      const values = trendData.map(t => t.rate)
      this.trendChart.setOption({
        tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
        grid: { left: 40, right: 12, top: 12, bottom: 24 },
        xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 10 } },
        yAxis: { type: 'value', min: Math.max(0, Math.floor(Math.min(...values) - 2)), max: 100, axisLabel: { fontSize: 10, formatter: '{value}%' } },
        series: [{
          data: values,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 4,
          lineStyle: { color: '#007f7a', width: 2 },
          itemStyle: { color: '#007f7a' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0,127,122,0.3)' },
              { offset: 1, color: 'rgba(0,127,122,0.02)' }
            ])
          }
        }]
      })
    },
    isMissingDate(day) {
      return MISSING_DATES.includes(day)
    },
    handleQuery() {
      this.pagination.page = 1
      this.fetchIssues()
    },
    handleReset() {
      this.filterForm = { market: '', dataType: '', dateRange: null, tsCode: '' }
      this.pagination.page = 1
      this.fetchIssues()
    },
    async openDetail(row) {
      this.currentIssue = row
      this.detailVisible = true
      const detail = await this.fetchIssueDetail(row.id)
      if (detail) {
        this.currentIssue = { ...row, ...detail }
        this.detailMissingList = detail.missing_details || []
      } else {
        this.detailMissingList = MOCK_MISSING_DETAIL
      }
    },
    openRepair(row) {
      this.repairIssue = row
      this.repairForm.repairMode = 'repair_missing_only'
      this.repairVisible = true
    },
    async handleRepair() {
      if (!this.repairIssue) return
      this.repairLoading = true
      try {
        await axios.post(`${API_BASE}/issues/${this.repairIssue.id}/repair`, {
          repair_mode: this.repairForm.repairMode,
          options: {}
        })
        this.$message?.success('修复任务已提交')
      } catch {
        this.$message?.warning('API 不可用，模拟修复成功')
      } finally {
        this.repairLoading = false
        this.repairVisible = false
        this.fetchIssues()
      }
    },
    async handleIgnore(row) {
      try {
        await axios.post(`${API_BASE}/issues/${row.id}/repair`, {
          repair_mode: 'ignore',
          options: {}
        })
        this.$message?.success('已标记为忽略')
      } catch {
        row.status = 'ignored'
        this.$message?.success('已标记为忽略（本地）')
      } finally {
        this.fetchIssues()
      }
    },
    async handleScan() {
      this.scanLoading = true
      const body = {
        market: this.filterForm.market || 'a',
        start_date: this.filterForm.dateRange?.[0] || '',
        end_date: this.filterForm.dateRange?.[1] || ''
      }
      try {
        await axios.post(`${API_BASE}/quality-scan`, body)
        this.$message?.success('数据扫描已触发')
      } catch {
        this.$message?.warning('API 不可用，模拟扫描完成')
      } finally {
        this.scanLoading = false
        this.fetchSummary()
        this.fetchIssues()
      }
    },
    handleSyncStockList() {
      this.$message?.info('同步股票列表功能触发')
    },
    severityType(s) {
      if (s === 'high') return 'danger'
      if (s === 'medium') return 'warning'
      return 'info'
    },
    statusType(s) {
      if (s === 'open') return 'danger'
      if (s === 'repaired') return 'success'
      if (s === 'ignored') return 'info'
      return 'info'
    },
    statusLabel(s) {
      if (s === 'open') return '待处理'
      if (s === 'repaired') return '已修复'
      if (s === 'ignored') return '已忽略'
      return s
    },
    handleResize() {
      this.trendChart && this.trendChart.resize()
    }
  },
  mounted() {
    this.fetchSummary().then(() => {
      this.$nextTick(() => { this.initTrendChart() })
    })
    this.fetchIssues()
    this.fetchSyncRecords()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this.trendChart) { this.trendChart.dispose(); this.trendChart = null }
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }

.main-card { margin-bottom: 16px; }
.filters { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }

.grid.three { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grid-item { background: #fafafa; border-radius: 6px; padding: 12px; }
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.card-title { font-weight: 600; font-size: 15px; }
.tag.green { color: #0f9f6e; font-weight: 600; font-size: 13px; }
.green { color: #0f9f6e; font-weight: 600; }

.chart-small { height: 170px; }

.calendar-area { height: 260px; overflow: auto; }
.calendar-area :deep(.el-calendar) { --el-calendar-border: none; }
.calendar-area :deep(.el-calendar__header) { padding: 4px 0; }
.calendar-area :deep(.el-calendar__body) { padding: 0; }
.calendar-cell { text-align: center; }
.calendar-cell.is-missing { color: #f56c6c; font-weight: 700; position: relative; }
.calendar-cell.is-missing::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 6px; height: 6px; background: #f56c6c; border-radius: 50%; }

.sync-table { width: 100%; }

.issue-card { margin-bottom: 16px; }
.pagination-wrap { display: flex; justify-content: flex-end; padding: 16px 0 0; }

.detail-content { padding: 0 4px; }
.detail-desc { margin-bottom: 16px; }
.detail-section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 20px 0 12px; }
</style>
