<!-- VolLine.vue -->
<template>
  <div class="vol-line-container">
    <div class="filter-bar">
      <div class="filter-bar-left">
        <el-date-picker
            v-model="startDate"
            type="date"
            placeholder="开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :clearable="false"
            style="margin-bottom: 0;"
        />
        <span class="date-separator">至</span>
        <el-date-picker
            v-model="endDate"
            type="date"
            placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :clearable="false"
            style="margin-bottom: 0;"
        />
        <el-button type="primary" @click="fetchData" style="margin-left: 15px;">查询</el-button>
      </div>
    </div>

    <div class="chart-container" v-loading="loading">
      <div ref="chartContainer" class="chart-area"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';
import axios from 'axios';

// 响应式数据
const startDate = ref('')
const endDate = ref('')
const chart = ref(null)
const loading = ref(false)
const chartData = ref([])
const chartContainer = ref(null)

// 获取指定天数前的日期
const getDateNDaysAgo = (n) => {
  const date = new Date()
  date.setDate(date.getDate() - n)
  return date
}

// 格式化日期为 YYYY-MM-DD 格式
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 初始化默认日期（60天前到今天）
const initDefaultDates = () => {
  startDate.value = formatDate(getDateNDaysAgo(60))
  endDate.value = formatDate(new Date())
}

// 初始化图表
const initChart = () => {
  nextTick(() => {
    if (chartContainer.value) {
      if (chart.value) {
        chart.value.dispose()
      }
      chart.value = echarts.init(chartContainer.value)
      // 初始化时显示空图表
      const emptyOption = {
        title: {
          text: '放量趋势',
          left: 'center'
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: [],
          type: 'line'
        }]
      }
      chart.value.setOption(emptyOption, true)
    }
  })
}

// 获取数据
const fetchData = async () => {
  if (!startDate.value || !endDate.value) {
    ElMessage.warning('请选择开始日期和结束日期')
    return
  }

  loading.value = true
  try {
    // 使用 axios 替代 this.$http
    const response = await axios.get('/api/vol_line', {
      params: {
        startDate: startDate.value,
        endDate: endDate.value
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.data && response.data.data) {
      chartData.value = response.data.data
      updateChart()
    } else {
      // 如果没有数据，清空图表
      chartData.value = []
      updateChart()
    }
  } catch (error) {
    console.error('获取成交量数据失败:', error)
    ElMessage.error('加载数据失败')
    // 出错时清空图表
    chartData.value = []
    updateChart()
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateChart = () => {
  if (!chart.value) return

  // 确保数据存在且有效
  if (!Array.isArray(chartData.value)) {
    chartData.value = []
  }

  // 准备图表数据，每个点包含日期信息
  const chartSeriesData = chartData.value.map(item => {
    return {
      value: item && typeof item.count === 'number' ? item.count : 0,
      date: item && item.select_date ? item.select_date : ''
    }
  })

  const dates = chartData.value.map(item => {
    return item && item.select_date ? item.select_date : ''
  }).filter(date => date !== '')

  const option = {
    title: {
      text: '放量趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        if (params && params.length > 0) {
          const point = params[0]
          return `${point.name}<br/>数量: ${point.value}`
        }
        return ''
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        interval: 0, // 显示所有标签
        rotate: 45, // 旋转45度防止重叠
        formatter: function(value) {
          // 只显示月日，例如 "01-15"
          if (value && value.length >= 10) {
            return value.substring(5, 10)
          }
          return value
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '数量'
    },
    series: [{
      data: chartSeriesData.map(item => item.value),
      type: 'line',
      smooth: true,
      areaStyle: {},
      symbol: 'circle', // 显示数据点
      symbolSize: 6, // 数据点大小
      label: {
        show: false, // 默认不显示标签
        position: 'top',
        formatter: '{c}' // 显示数值
      },
      emphasis: {
        focus: 'series',
        label: {
          show: true // 高亮时显示标签
        }
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%', // 增加底部空间以容纳X轴标签
      containLabel: true
    }
  }

  // 使用 notMerge: true 避免配置合并问题
  chart.value.setOption(option, true)
}

// 组件挂载时初始化
onMounted(() => {
  initDefaultDates()
  initChart()
  // 页面加载后自动查询一次数据
  fetchData()
})

// 组件卸载前销毁图表
onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.dispose()
    chart.value = null
  }
})
</script>

<style scoped>
.vol-line-container {
  padding: 0px;
  height: calc(100vh - 120px); /* 根据需要调整高度 */
  display: flex;
  flex-direction: column;
}

.filter-bar {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  padding-left: 16px;
}

.filter-bar-left {
  display: flex;
  align-items: center;
}

.date-separator {
  margin: 0 10px;
  color: #606266;
  align-self: center;
}

.chart-container {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 20px;
  margin-left: 16px;
  margin-right: 16px;
  margin-bottom: 16px;
  overflow: hidden;
}

.chart-area {
  height: 100%;
  width: 100%;
}
</style>