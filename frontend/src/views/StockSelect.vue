<template>
  <div class="stock-select-view">
    <el-card>
      <div class="filter-bar">
        <div class="filter-bar-left">
          <el-date-picker
            v-model="queryDate"
            type="date"
            placeholder="选择选股日期（必填）"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="margin-bottom: 0;"
            @change="handleDateChange"
            :clearable="false"
            :disabled="loading"
          />
          <el-button type="primary" @click="fetchData" style="margin-left: 12px;" :disabled="!queryDate || loading">查询</el-button>
        </div>
        <span v-if="!queryDate" style="color: #f56c6c; margin-left: 12px; font-size: 13px; align-self: center;">请先选择选股日期</span>
      </div>
      <div class="table-wrapper">
        <el-table
          :data="queryDate ? tableData : []"
          border
          style="margin-top: 8px; min-width: 900px; max-width: 1200px; width: auto;"
          v-loading="loading"
          header-cell-class-name="left-align-header" cell-class-name="left-align-cell"
        >
          <el-table-column prop="select_date" label="选股日期" width="110" align="left" header-align="left" />
          <el-table-column prop="ts_code" label="股票代码" width="120" align="left" header-align="left">
            <template #default="scope">
              <a
                :href="`https://stockpage.10jqka.com.cn/${getCodePrefix(scope.row.ts_code)}`"
                target="_blank"
                class="stock-link"
              >
                {{ scope.row.ts_code }}
              </a>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="股票名称" width="120" align="left" header-align="left" />
          <el-table-column prop="vol" label="成交放量" width="100" align="left" header-align="left" />
          <el-table-column prop="trend3" label="3日趋势" width="100" align="left" header-align="left" />
          <el-table-column prop="trend5" label="5日趋势" width="100" align="left" header-align="left" />
          <el-table-column prop="trend10" label="10日趋势" width="100" align="left" header-align="left" />
          <el-table-column prop="trend20" label="20日趋势" width="100" align="left" header-align="left" />
          <el-table-column prop="trend30" label="30日趋势" width="100" align="left" header-align="left" />
        </el-table>
      </div>
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

const getCodePrefix = (tsCode) => {
  if (!tsCode || !tsCode.includes('.')) return tsCode
  return tsCode.split('.')[0]
}

// 获取今天日期字符串
const getToday = () => {
  const d = new Date()
  const m = d.getMonth() + 1
  const day = d.getDate()
  return `${d.getFullYear()}-${m < 10 ? '0' + m : m}-${day < 10 ? '0' + day : day}`
}

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const queryDate = ref(getToday())

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
    } else if (res.data && res.data.error) {
      ElMessage.info(res.data.error)
      tableData.value = []
      total.value = 0
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
  padding: 0px;
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
.table-wrapper {
  text-align: left;
  margin-left: 0;
  padding-left: 16px;
}
.left-align-header {
  text-align: left !important;
}
.left-align-cell {
  text-align: left !important;
}
</style> 