<!-- VolLine.vue -->
<template>
  <div class="vol-line-container">
    <div class="date-range-selector">
      <el-date-picker
          v-model="startDate"
          type="date"
          placeholder="Start Date"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
          @change="onDateChange"
      />
      <el-date-picker
          v-model="endDate"
          type="date"
          placeholder="End Date"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
          @change="onDateChange"
      />
      <el-button type="primary" @click="fetchData">Query</el-button>
    </div>

    <div class="chart-container" v-loading="loading">
      <div ref="chartContainer" class="chart-area"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'VolLine',
  data() {
    return {
      startDate: null,
      endDate: null,
      chart: null,
      loading: false,
      chartData: []
    }
  },
  mounted() {
    this.initDefaultDates();
    this.initChart();
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose();
    }
  },
  methods: {
    initDefaultDates() {
      const today = new Date();
      const startDate = new Date();
      startDate.setDate(today.getDate() - 180);

      this.startDate = this.formatDate(startDate);
      this.endDate = this.formatDate(today);
    },

    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    initChart() {
      this.$nextTick(() => {
        if (this.$refs.chartContainer) {
          this.chart = echarts.init(this.$refs.chartContainer);
          this.updateChart();
        }
      });
    },

    onDateChange() {
      // Optional: auto-fetch when dates change
    },

    async fetchData() {
      if (!this.startDate || !this.endDate) {
        this.$message.warning('Please select both start and end dates');
        return;
      }

      this.loading = true;
      try {
        const response = await this.$http.get('/api/vol_line', {
          params: {
            startDate: this.startDate,
            endDate: this.endDate
          }
        });

        if (response.data && response.data.data) {
          this.chartData = response.data.data;
          this.updateChart();
        }
      } catch (error) {
        console.error('Failed to fetch volume line data:', error);
        this.$message.error('Failed to load data');
      } finally {
        this.loading = false;
      }
    },

    updateChart() {
      if (!this.chart) return;

      const dates = this.chartData.map(item => item.select_date);
      const counts = this.chartData.map(item => item.count);

      const option = {
        title: {
          text: 'Stock Selection Volume Trend'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: {
          type: 'value',
          name: 'Count'
        },
        series: [{
          data: counts,
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      };

      this.chart.setOption(option);
    }
  }
}
</script>

<style scoped>
.vol-line-container {
  padding: 20px;
}

.date-range-selector {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.date-range-selector .el-date-editor {
  width: 150px;
}

.chart-container {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 20px;
  min-height: 400px;
}

.chart-area {
  height: 350px;
  width: 100%;
}
</style>
