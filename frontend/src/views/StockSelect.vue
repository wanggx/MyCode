<template>
  <div class="stock-select-view">
    <el-card>
      <div class="filter-bar">
        <el-date-picker
          v-model="queryDate"
          type="date"
          placeholder="选择选股日期（必填）"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="margin-bottom: 16px;"
          @change="handleDateChange"
          :clearable="false"
          :disabled="loading"
        />
        <el-button type="primary" @click="fetchData" style="margin-left: 12px;" :disabled="!queryDate || loading">查询</el-button>
        <span v-if="!queryDate" style="color: #f56c6c; margin-left: 12px; font-size: 13px;">请先选择选股日期</span>
      </div>
      <el-table
        :data="queryDate ? tableData : []"
        border
        style="width: 100%; margin-top: 8px;"
        v-loading="loading"
      >
        <el-table-column prop="select_date" label="选股日期" width="110" />
        <el-table-column prop="ts_code" label="股票代码" width="120" />
        <el-table-column prop="name" label="股票名称" width="120" />
        <el-table-column prop="vol" label="成交放量" width="100" />
        <el-table-column prop="trend3" label="3日趋势" width="100" />
        <el-table-column prop="trend5" label="5日趋势" width="100" />
        <el-table-column prop="trend10" label="10日趋势" width="100" />
        <el-table-column prop="trend20" label="20日趋势" width="100" />
        <el-table-column prop="trend30" label="30日趋势" width="100" />
      </el-table>
      <div style="margin-top: 16px; text-align: right;">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next, jumper"
          @current-change="fetchData"
          :disabled="!queryDate || loading"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const queryDate = ref('')

const fetchData = async () => {
  if (!queryDate.value) {
    ElMessage.warning('请先选择选股日期')
    return
  }
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (queryDate.value) {
      params.select_date = queryDate.value
    }
    const res = await axios.get('/api/stock_select', {
      params,
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data && res.data.data) {
      tableData.value = res.data.data.items
      total.value = res.data.data.total
    } else {
      tableData.value = []
      total.value = 0
    }
  } catch (e) {
    ElMessage.error('获取数据失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleDateChange = () => {
  page.value = 1
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.stock-select-view {
  padding: 16px;
}
.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
</style> 