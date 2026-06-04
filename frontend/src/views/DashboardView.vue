<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h2>总览</h2>
        <p class="page-desc">跟踪今日信号、策略表现、数据质量和系统提示。</p>
      </div>
      <div class="toolbar">
        <el-button size="default" @click="setRange('1y')" :type="rangeBtn==='1y'?'primary':''">近1年</el-button>
        <el-button size="default" @click="setRange('2y')" :type="rangeBtn==='2y'?'primary':''">近2年</el-button>
        <el-button type="primary" size="default" @click="handleRefresh">刷新</el-button>
      </div>
    </div>
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6" v-for="kpi in kpiCards" :key="kpi.label">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-info">
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-value" :style="{ color: kpi.valueColor }">{{ kpi.value }}</div>
            <div class="kpi-note" :style="{ color: kpi.noteColor }">{{ kpi.note }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" class="content-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">策略收益 vs 沪深300</span>
              <div class="legend-tags">
                <span class="legend-tag active">组合综合</span>
                <span class="legend-tag">沪深300</span>
              </div>
            </div>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">今日信号排行</span>
              <el-button type="primary" link>查看全部 ›</el-button>
            </div>
          </template>
          <el-table :data="signalRanking" size="small" stripe>
            <el-table-column prop="rank" label="排名" width="60">
              <template #default="{ row }">
                <span :class="{ 'rank-top': row.rank <= 3 }">{{ row.rank }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="策略" min-width="120" />
            <el-table-column prop="signal_count" label="信号数" width="80" />
            <el-table-column prop="avg_score" label="信号分均值" width="100" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" class="content-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">任务状态</span></template>
          <el-table :data="taskStatus" size="small" stripe :show-header="false">
            <el-table-column prop="name" min-width="120" />
            <el-table-column prop="time" min-width="140" />
            <el-table-column prop="status" width="80">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small" effect="dark">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">系统提示</span></template>
          <el-table :data="systemTips" size="small" stripe :show-header="false">
            <el-table-column prop="text" min-width="260">
              <template #default="{ row }">
                <span :class="{ 'tip-warning': row.isWarning }">{{ row.text }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="time" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'DashboardView',
  data() {
    return {
      rangeBtn: '1y',
      kpiCards: [
        { label: '今日信号', value: '38', valueColor: '#303133', note: '较昨日 +12 / 46.15%', noteColor: '#0f9f6e' },
        { label: '运行策略', value: '12', valueColor: '#303133', note: '较昨日 +1 / 9.09%', noteColor: '#0f9f6e' },
        { label: '数据完整率', value: '98.6%', valueColor: '#303133', note: '较昨日 +0.3pp', noteColor: '#0f9f6e' },
        { label: '最大回撤', value: '-6.2%', valueColor: '#0f9f6e', note: '历史最大 -18.7%', noteColor: '#d84a57' }
      ],
      signalRanking: [
        { rank: 1, name: '放量突破', signal_count: 14, avg_score: 82.1 },
        { rank: 2, name: '均线趋势', signal_count: 10, avg_score: 78.3 },
        { rank: 3, name: 'MACD/KDJ共振', signal_count: 8, avg_score: 73.6 },
        { rank: 4, name: '港股趋势', signal_count: 6, avg_score: 69.2 }
      ],
      taskStatus: [
        { name: '数据同步', time: '今日 08:45:32', status: '成功', statusType: 'success' },
        { name: '策略运行', time: '今日 09:15:07', status: '运行中', statusType: '' },
        { name: '通知', time: '今日 09:15:05', status: '已发送', statusType: 'success' }
      ],
      systemTips: [
        { text: '沪深股票日线数据已更新至 2026-06-04', time: '08:45', isWarning: false },
        { text: '港股日线数据已更新至 2026-06-04', time: '08:46', isWarning: false },
        { text: '部分因子IC异常，请检查：动量因子', time: '08:40', isWarning: true }
      ],
      chart: null
    }
  },
  methods: {
    setRange(r) {
      this.rangeBtn = r
      this.initChart()
    },
    handleRefresh() {
      this.initChart()
      this.$message.success('已刷新')
    },
    initChart() {
      const el = this.$refs.chartRef
      if (!el) return
      if (this.chart) this.chart.dispose()
      this.chart = echarts.init(el)
      const pointCount = this.rangeBtn === '2y' ? 60 : 30
      const dates = []
      const strategyValues = []
      const benchmarkValues = []
      let sBase = 1000
      let bBase = 1000
      for (let i = 0; i < pointCount; i++) {
        const d = new Date()
        d.setDate(d.getDate() - (pointCount - 1 - i))
        dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
        sBase += (Math.random() - 0.42) * 25
        bBase += (Math.random() - 0.46) * 12
        strategyValues.push(Math.round(sBase * 100) / 100)
        benchmarkValues.push(Math.round(bBase * 100) / 100)
      }
      this.chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: {
          data: ['策略组合', '沪深300'],
          bottom: 0,
          textStyle: { fontSize: 12 }
        },
        grid: { left: 50, right: 20, top: 20, bottom: 40 },
        xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
        series: [
          {
            name: '策略组合',
            type: 'line',
            data: strategyValues,
            smooth: true,
            lineStyle: { color: '#007f7a', width: 2 },
            areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0,127,122,0.3)' },
              { offset: 1, color: 'rgba(0,127,122,0.02)' }
            ])}
          },
          {
            name: '沪深300',
            type: 'line',
            data: benchmarkValues,
            smooth: true,
            lineStyle: { color: '#a9b4c0', width: 2 },
            areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(169,180,192,0.15)' },
              { offset: 1, color: 'rgba(169,180,192,0.01)' }
            ])}
          }
        ]
      })
    }
  },
  mounted() {
    this.$nextTick(() => { this.initChart() })
    this._resizeHandler = () => { this.chart && this.chart.resize() }
    window.addEventListener('resize', this._resizeHandler)
  },
  beforeUnmount() {
    if (this.chart) { this.chart.dispose(); this.chart = null }
    window.removeEventListener('resize', this._resizeHandler)
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.toolbar { display: flex; gap: 8px; }
.kpi-row { margin-bottom: 16px; }
.kpi-card :deep(.el-card__body) { padding: 20px; }
.kpi-info { }
.kpi-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.kpi-value { font-size: 28px; font-weight: 700; line-height: 1.3; }
.kpi-note { font-size: 12px; margin-top: 4px; }
.content-row { margin-bottom: 16px; }
.card-title { font-weight: 600; font-size: 15px; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.legend-tags { display: flex; gap: 6px; }
.legend-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  color: #909399;
  cursor: pointer;
}
.legend-tag.active { background: #007f7a; color: #fff; border-color: #007f7a; }
.chart-container { height: 280px; }
.rank-top { color: #d28a17; font-weight: 600; }
.tip-warning { color: #d28a17; }
</style>
