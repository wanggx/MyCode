<template>
  <el-card class="chart-card">
    <h2>图表展示</h2>
    <div ref="chart" style="height:400px;"></div>
  </el-card>
</template>

<script>
import * as echarts from 'echarts'
export default {
  name: 'ChartViewPage',
  mounted() {
    this.initChart()
  },
  methods: {
    initChart() {
      const chart = echarts.init(this.$refs.chart)
      chart.setOption({
        title: { text: '示例折线图' },
        tooltip: {},
        xAxis: { data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: {},
        series: [{
          name: '访问量',
          type: 'line',
          data: [120, 200, 150, 80, 70, 110, 130]
        }]
      })
    }
  }
}
</script>

<style scoped>
.chart-card {
  max-width: 900px;
  margin: 60px auto;
  padding: 30px 20px;
}
</style> 