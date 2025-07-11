<template>
  <el-container class="page-layout">
    <el-aside width="200px" class="page-aside">
      <el-menu :default-active="activeMenu" @select="onMenuSelect">
        <el-menu-item v-for="item in menus" :key="item.key" :index="item.key">
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main class="page-main">
      <div v-if="activeMenu === 'line'">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>折线图</span>
              <el-button type="primary" size="small" @click="refreshLineChart">刷新数据</el-button>
            </div>
          </template>
          <div class="chart-wrapper">
            <div ref="lineChart" style="height: 400px; width: 100%;"></div>
          </div>
        </el-card>
      </div>
      <div v-else-if="activeMenu === 'bar'">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>柱状图</span>
              <el-button type="primary" size="small" @click="refreshBarChart">刷新数据</el-button>
            </div>
          </template>
          <div class="chart-wrapper">
            <div ref="barChart" style="height: 400px; width: 100%;"></div>
          </div>
        </el-card>
      </div>
      <div v-else-if="activeMenu === 'pie'">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>饼图</span>
              <el-button type="primary" size="small" @click="refreshPieChart">刷新数据</el-button>
            </div>
          </template>
          <div class="chart-wrapper">
            <div ref="pieChart" style="height: 400px; width: 100%;"></div>
          </div>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ChartView',
  data() {
    return {
      menus: [
        { key: 'line', title: '折线图' },
        { key: 'bar', title: '柱状图' },
        { key: 'pie', title: '饼图' }
      ],
      activeMenu: 'line',
      lineChart: null,
      barChart: null,
      pieChart: null
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initCharts()
    })
  },
  beforeUnmount() {
    if (this.lineChart) this.lineChart.dispose()
    if (this.barChart) this.barChart.dispose()
    if (this.pieChart) this.pieChart.dispose()
  },
  methods: {
    onMenuSelect(key) {
      this.activeMenu = key
      this.$nextTick(() => {
        this.initCharts()
      })
    },
    initCharts() {
      if (this.activeMenu === 'line' && this.$refs.lineChart) {
        this.initLineChart()
      } else if (this.activeMenu === 'bar' && this.$refs.barChart) {
        this.initBarChart()
      } else if (this.activeMenu === 'pie' && this.$refs.pieChart) {
        this.initPieChart()
      }
    },
    initLineChart() {
      if (this.lineChart) this.lineChart.dispose()
      this.lineChart = echarts.init(this.$refs.lineChart)
      const option = {
        title: { text: '访问量趋势', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'] },
        yAxis: { type: 'value' },
        series: [{
          name: '访问量',
          type: 'line',
          data: [120, 200, 150, 80, 70, 110, 130],
          smooth: true
        }]
      }
      this.lineChart.setOption(option)
    },
    initBarChart() {
      if (this.barChart) this.barChart.dispose()
      this.barChart = echarts.init(this.$refs.barChart)
      const option = {
        title: { text: '用户注册量', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'] },
        yAxis: { type: 'value' },
        series: [{
          name: '注册量',
          type: 'bar',
          data: [20, 35, 25, 15, 12, 18, 22]
        }]
      }
      this.barChart.setOption(option)
    },
    initPieChart() {
      if (this.pieChart) this.pieChart.dispose()
      this.pieChart = echarts.init(this.$refs.pieChart)
      const option = {
        title: { text: '用户分布', left: 'center' },
        tooltip: { trigger: 'item' },
        series: [{
          name: '用户分布',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 335, name: '北京' },
            { value: 310, name: '上海' },
            { value: 234, name: '广州' },
            { value: 135, name: '深圳' },
            { value: 1548, name: '其他' }
          ]
        }]
      }
      this.pieChart.setOption(option)
    },
    refreshLineChart() {
      const newData = Array.from({length: 7}, () => Math.floor(Math.random() * 200) + 50)
      this.lineChart.setOption({
        series: [{ data: newData }]
      })
      this.$message.success('折线图数据已刷新')
    },
    refreshBarChart() {
      const newData = Array.from({length: 7}, () => Math.floor(Math.random() * 50) + 10)
      this.barChart.setOption({
        series: [{ data: newData }]
      })
      this.$message.success('柱状图数据已刷新')
    },
    refreshPieChart() {
      const newData = [
        { value: Math.floor(Math.random() * 500) + 100, name: '北京' },
        { value: Math.floor(Math.random() * 500) + 100, name: '上海' },
        { value: Math.floor(Math.random() * 500) + 100, name: '广州' },
        { value: Math.floor(Math.random() * 500) + 100, name: '深圳' },
        { value: Math.floor(Math.random() * 2000) + 500, name: '其他' }
      ]
      this.pieChart.setOption({
        series: [{ data: newData }]
      })
      this.$message.success('饼图数据已刷新')
    }
  }
}
</script>

<style scoped>
.page-layout {
  height: 100vh;
}
.page-aside {
  background: #f8f9fa;
  border-right: 1px solid #e4e7ed;
}
.page-main {
  padding: 20px;
  background: #f5f5f5;
}
.chart-card {
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chart-wrapper {
  min-width: 0;
  overflow: hidden;
}
</style> 