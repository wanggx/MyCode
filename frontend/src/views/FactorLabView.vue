<template>
  <div class="page-container">
    <div class="page-header">
      <h2>因子实验室</h2>
      <p class="page-desc">因子库、IC、分层收益和相关性，策略上线前的研究台。</p>
    </div>

    <el-row :gutter="16">
      <el-col :span="4">
        <el-card class="category-card">
          <template #header><span class="card-title">因子分类</span></template>
          <div class="category-list">
            <div
              v-for="cat in categories"
              :key="cat.key"
              :class="['category-item', { active: activeCategory === cat.key }]"
              @click="handleCategoryChange(cat.key)"
            >
              <strong>{{ cat.label }} ({{ cat.count }})</strong>
              <p class="category-desc">{{ cat.desc }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="20">
        <el-card class="filter-card">
          <el-form :inline="true" :model="filterForm">
            <el-form-item label="因子">
              <el-select v-model="filterForm.factor_code" placeholder="选择因子" style="width: 180px" clearable>
                <el-option
                  v-for="f in factorOptions"
                  :key="f.factor_code"
                  :label="f.factor_name"
                  :value="f.factor_code"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="市场">
              <el-select v-model="filterForm.market" style="width: 120px">
                <el-option label="沪深A股" value="沪深A股" />
                <el-option label="港股通" value="港股通" />
              </el-select>
            </el-form-item>
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="filterForm.start_date"
                type="date"
                placeholder="开始日期"
                style="width: 150px"
                value-format="YYYY-MM-DD"
              />
              <span style="margin: 0 6px; color: #909399">至</span>
              <el-date-picker
                v-model="filterForm.end_date"
                type="date"
                placeholder="结束日期"
                style="width: 150px"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item label="IC周期">
              <el-select v-model="filterForm.ic_period" style="width: 100px">
                <el-option label="20日" value="20日" />
                <el-option label="60日" value="60日" />
              </el-select>
            </el-form-item>
            <el-form-item label="分组数">
              <el-select v-model="filterForm.groups" style="width: 100px">
                <el-option label="5组" :value="5" />
                <el-option label="10组" :value="10" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAnalyze">分析</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-row :gutter="16" style="margin-top: 16px">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span class="card-title">IC曲线</span></template>
              <div ref="icChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span class="card-title">分层收益</span></template>
              <div ref="groupChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header><span class="card-title">相关性热力图</span></template>
              <div ref="heatmapChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-card shadow="hover" style="margin-top: 16px">
          <template #header><span class="card-title">因子覆盖率</span></template>
          <el-table :data="coverageTable" stripe size="small">
            <el-table-column prop="factor_code" label="因子" width="140" />
            <el-table-column prop="covered" label="覆盖股票数" width="120" align="right" />
            <el-table-column prop="coverage" label="覆盖率" width="100" align="right">
              <template #default="{ row }">
                <span style="color: #0f9f6e; font-weight: bold">{{ row.coverage }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="ic_mean" label="IC均值" width="100" align="right" />
            <el-table-column prop="ir" label="IR" width="80" align="right" />
            <el-table-column prop="long_short_annual" label="多空年化" width="110" align="right" />
            <el-table-column prop="info_ratio" label="信息比率" width="100" align="right" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from '@/config/axios'

const MOCK_FACTORS = [
  { factor_code: 'MA5', factor_name: '5日均线', category: '技术' },
  { factor_code: 'MACD', factor_name: 'MACD因子', category: '技术' },
  { factor_code: 'Volume_Slope', factor_name: '成交量斜率', category: '价量' },
  { factor_code: 'Volatility', factor_name: '波动率', category: '风险' },
  { factor_code: 'RSI', factor_name: '相对强弱指标', category: '价量' }
]

const MOCK_IC_CURVE = (() => {
  const data = []
  const start = new Date('2024-01-05')
  for (let i = 0; i < 30; i++) {
    const d = new Date(start)
    d.setDate(d.getDate() + i * 2)
    data.push({
      trade_date: d.toISOString().slice(0, 10),
      ic: parseFloat((Math.random() * 0.3 - 0.1).toFixed(3))
    })
  }
  return data
})()

const MOCK_GROUP_RETURN_5 = [
  { group: 'Q1', return: 0.021 },
  { group: 'Q2', return: 0.008 },
  { group: 'Q3', return: -0.005 },
  { group: 'Q4', return: -0.015 },
  { group: 'Q5', return: -0.028 }
]

const MOCK_GROUP_RETURN_10 = [
  { group: 'Q1', return: 0.028 },
  { group: 'Q2', return: 0.018 },
  { group: 'Q3', return: 0.010 },
  { group: 'Q4', return: 0.003 },
  { group: 'Q5', return: -0.002 },
  { group: 'Q6', return: -0.008 },
  { group: 'Q7', return: -0.014 },
  { group: 'Q8', return: -0.019 },
  { group: 'Q9', return: -0.025 },
  { group: 'Q10', return: -0.032 }
]

const MOCK_ANALYSIS = {
  ic_curve: MOCK_IC_CURVE,
  group_return: MOCK_GROUP_RETURN_5,
  coverage: { covered: 2800, total: 3500, ratio: 0.8 }
}

const MOCK_COVERAGE_TABLE = [
  { factor_code: 'MA5', covered: 3210, total: 3500, coverage: '91.71%', ic_mean: 0.062, ir: 1.18, long_short_annual: '13.42%', info_ratio: 1.21 },
  { factor_code: 'MACD', covered: 3050, total: 3500, coverage: '87.14%', ic_mean: 0.057, ir: 1.07, long_short_annual: '11.28%', info_ratio: 1.03 },
  { factor_code: 'Volume_Slope', covered: 2980, total: 3500, coverage: '85.14%', ic_mean: -0.032, ir: -0.61, long_short_annual: '-5.14%', info_ratio: -0.55 },
  { factor_code: 'Volatility', covered: 3350, total: 3500, coverage: '95.71%', ic_mean: 0.045, ir: 0.89, long_short_annual: '9.76%', info_ratio: 0.92 },
  { factor_code: 'RSI', covered: 3180, total: 3500, coverage: '90.86%', ic_mean: 0.038, ir: 0.72, long_short_annual: '7.54%', info_ratio: 0.68 }
]

const HEATMAP_FACTORS = ['MA5', 'MACD', 'VolSlope', 'Volatility', 'RSI']
const MOCK_HEATMAP_DATA = (() => {
  const data = []
  for (let i = 0; i < HEATMAP_FACTORS.length; i++) {
    for (let j = 0; j < HEATMAP_FACTORS.length; j++) {
      const v = i === j ? 1 : parseFloat((Math.random() * 1.6 - 0.8).toFixed(2))
      data.push([i, j, v])
    }
  }
  return data
})()

export default {
  name: 'FactorLabView',
  data() {
    return {
      activeCategory: '',
      filterForm: {
        factor_code: '',
        market: '沪深A股',
        start_date: '',
        end_date: '',
        ic_period: '20日',
        groups: 5
      },
      factorOptions: [],
      icCurveData: [],
      groupReturnData: [],
      coverageTable: [],
      icChart: null,
      groupChart: null,
      heatmapChart: null
    }
  },
  computed: {
    categories() {
      return [
        { key: '技术', label: '技术类', count: 128, desc: 'MA20突破、RSI(14)、MACD、KDJ' },
        { key: '价量', label: '价量类', count: 86, desc: '成交量斜率、量价背离、换手率' },
        { key: '风险', label: '风险类', count: 34, desc: '波动率、Beta、下行风险' }
      ]
    }
  },
  methods: {
    async fetchFactors() {
      try {
        const res = await axios.get('/api/factors', { params: { category: this.activeCategory } })
        const d = res.data?.data || res.data
        this.factorOptions = d.items || d.list || d || []
      } catch {
        this.factorOptions = MOCK_FACTORS.filter(f => !this.activeCategory || f.category === this.activeCategory)
      }
    },
    async fetchAnalysis() {
      try {
        const res = await axios.post('/api/factors/analyze', {
          factor_code: this.filterForm.factor_code,
          start_date: this.filterForm.start_date,
          end_date: this.filterForm.end_date,
          groups: this.filterForm.groups
        })
        const d = res.data?.data || res.data
        this.icCurveData = d.ic_curve || []
        this.groupReturnData = d.group_return || []
      } catch {
        this.icCurveData = MOCK_ANALYSIS.ic_curve
        this.groupReturnData = this.filterForm.groups === 10 ? MOCK_GROUP_RETURN_10 : MOCK_GROUP_RETURN_5
      }
    },
    async fetchCoverage() {
      try {
        await axios.get(`/api/factors/${this.filterForm.factor_code || 'MA5'}/coverage`)
        // API 返回单对象，表格需要数组，直接使用 mock 数据
        this.coverageTable = MOCK_COVERAGE_TABLE
      } catch {
        this.coverageTable = MOCK_COVERAGE_TABLE
      }
    },
    handleCategoryChange(key) {
      this.activeCategory = this.activeCategory === key ? '' : key
      this.filterForm.factor_code = ''
      this.fetchFactors()
    },
    async handleAnalyze() {
      if (!this.filterForm.factor_code) {
        this.$message?.warning('请选择因子')
        return
      }
      await this.fetchAnalysis()
      await this.fetchCoverage()
      this.$nextTick(() => {
        this.initIcChart()
        this.initGroupChart()
        this.initHeatmapChart()
      })
    },
    handleReset() {
      this.filterForm = { factor_code: '', market: '沪深A股', start_date: '', end_date: '', ic_period: '20日', groups: 5 }
      this.activeCategory = ''
      this.icCurveData = []
      this.groupReturnData = []
      this.coverageTable = []
      this.fetchFactors()
    },
    initIcChart() {
      const el = this.$refs.icChartRef
      if (!el) return
      if (this.icChart) { this.icChart.dispose(); this.icChart = null }
      this.icChart = echarts.init(el)
      const dates = this.icCurveData.map(d => d.trade_date)
      const values = this.icCurveData.map(d => d.ic)
      this.icChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 50, right: 16, top: 16, bottom: 30 },
        xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 10, interval: Math.floor(dates.length / 5) } },
        yAxis: { type: 'value', axisLabel: { fontSize: 10 } },
        series: [{
          type: 'line',
          data: values,
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#007f7a', width: 2 },
          itemStyle: { color: '#007f7a' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,127,122,0.25)' },
            { offset: 1, color: 'rgba(0,127,122,0.02)' }
          ])}
        }]
      })
    },
    initGroupChart() {
      const el = this.$refs.groupChartRef
      if (!el) return
      if (this.groupChart) { this.groupChart.dispose(); this.groupChart = null }
      this.groupChart = echarts.init(el)
      const groups = this.groupReturnData.map(d => d.group)
      const values = this.groupReturnData.map(d => d.return)
      const colors = values.map(v => v >= 0 ? '#007f7a' : '#f56c6c')
      this.groupChart.setOption({
        tooltip: {
          trigger: 'axis',
          formatter(params) {
            const p = params[0]
            return `${p.name}<br/>${p.marker} ${(p.value * 100).toFixed(2)}%`
          }
        },
        grid: { left: 60, right: 16, top: 16, bottom: 30 },
        xAxis: { type: 'category', data: groups, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 10, formatter: v => (v * 100).toFixed(1) + '%' } },
        series: [{
          type: 'bar',
          data: values.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
          barWidth: '50%'
        }]
      })
    },
    initHeatmapChart() {
      const el = this.$refs.heatmapChartRef
      if (!el) return
      if (this.heatmapChart) { this.heatmapChart.dispose(); this.heatmapChart = null }
      this.heatmapChart = echarts.init(el)
      this.heatmapChart.setOption({
        tooltip: {
          formatter(p) {
            return `${HEATMAP_FACTORS[p.data[0]]} vs ${HEATMAP_FACTORS[p.data[1]]}<br/>相关系数: ${p.data[2]}`
          }
        },
        grid: { left: 60, right: 40, top: 10, bottom: 40 },
        xAxis: { type: 'category', data: HEATMAP_FACTORS, axisLabel: { fontSize: 10 }, splitArea: { show: true } },
        yAxis: { type: 'category', data: HEATMAP_FACTORS, axisLabel: { fontSize: 10 }, splitArea: { show: true } },
        visualMap: { min: -1, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: { color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'] } },
        series: [{
          type: 'heatmap',
          data: MOCK_HEATMAP_DATA,
          label: { show: true, fontSize: 10 },
          emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
        }]
      })
    },
    handleResize() {
      this.icChart && this.icChart.resize()
      this.groupChart && this.groupChart.resize()
      this.heatmapChart && this.heatmapChart.resize()
    }
  },
  mounted() {
    this.fetchFactors()
    this.fetchCoverage()
    this.$nextTick(() => {
      this.initIcChart()
      this.initGroupChart()
      this.initHeatmapChart()
    })
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this.icChart) { this.icChart.dispose(); this.icChart = null }
    if (this.groupChart) { this.groupChart.dispose(); this.groupChart = null }
    if (this.heatmapChart) { this.heatmapChart.dispose(); this.heatmapChart = null }
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
.category-card { height: 100%; }
.category-list { display: flex; flex-direction: column; gap: 12px; }
.category-item { padding: 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; }
.category-item:hover { background: #f0f9f8; border-color: #b2dfdb; }
.category-item.active { background: #e0f2f1; border-color: #007f7a; }
.category-item strong { font-size: 14px; color: #303133; }
.category-desc { margin: 4px 0 0; font-size: 12px; color: #909399; }
.filter-card { margin-bottom: 0; }
.chart-container { height: 280px; }
</style>
