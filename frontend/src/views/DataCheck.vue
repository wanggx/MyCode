<template>
  <div class="data-check-page">
    <el-card>
      <div class="data-check-toolbar">
        <div class="toolbar-left">
          <el-date-picker v-model="searchForm.startDate" type="date" placeholder="开始时间" style="width: 140px;" />
          <el-date-picker v-model="searchForm.endDate" type="date" placeholder="结束时间" style="width: 140px; margin-left: 8px;" />
          <el-button type="primary" @click="handleSearch" style="margin-left: 8px;">查询</el-button>
        </div>
        <div class="toolbar-right">
          <el-date-picker v-model="addStartDate" type="date" placeholder="补录开始日期（必选）" style="width: 140px;" />
          <el-date-picker v-model="addEndDate" type="date" placeholder="补录结束日期（必选）" style="width: 140px; margin-left: 8px;" />
          <el-button type="success" :disabled="!addStartDate || !addEndDate" @click="handleAdd" style="margin-left: 8px;">补录</el-button>
        </div>
      </div>
      <el-table :data="tableData" style="width: 100%; margin-top: 18px;" border stripe>
        <el-table-column prop="trade_date" label="日期" width="160" />
        <el-table-column prop="cnt" label="数据条数" width="120" />
      </el-table>
      <div class="pagination-bar">
        <el-pagination
          background
          layout="prev, pager, next, jumper, ->, total"
          :total="total"
          :page-size="pageSize"
          v-model:current-page="page"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from '@/config/axios'

export default {
  name: 'DataCheck',
  data() {
    return {
      searchForm: {
        startDate: '',
        endDate: ''
      },
      addStartDate: '',
      addEndDate: '',
      tableData: [],
      total: 0,
      page: 1,
      pageSize: 10,
      loading: false
    }
  },
  methods: {
    formatDate(date) {
      if (!date) return ''
      if (typeof date === 'string' && date.length === 8) return date
      const d = new Date(date)
      const y = d.getFullYear()
      const m = (d.getMonth() + 1).toString().padStart(2, '0')
      const day = d.getDate().toString().padStart(2, '0')
      return `${y}${m}${day}`
    },
    async fetchData() {
      this.loading = true
      try {
        const params = {
          startDate: this.formatDate(this.searchForm.startDate),
          endDate: this.formatDate(this.searchForm.endDate),
          page: this.page,
          page_size: this.pageSize
        }
        const res = await axios.get('/api/stock/check', { params })
        if (res.data && res.data.code === 0 && res.data.data && res.data.data.list) {
          this.tableData = res.data.data.list
          this.total = res.data.data.total
        } else {
          this.$message.error(res.data && res.data.message ? res.data.message : '查询失败')
          this.tableData = []
          this.total = 0
        }
      } catch (e) {
        this.$message.error('查询失败')
        this.tableData = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.fetchData()
    },
    handlePageChange(val) {
      this.page = val
      this.fetchData()
    },
    async handleAdd() {
      if (!this.addStartDate || !this.addEndDate) {
        this.$message.warning('请选择补录开始日期和结束日期')
        return
      }
      const start_date = this.formatDate(this.addStartDate)
      const end_date = this.formatDate(this.addEndDate)
      try {
        const res = await axios.post('/api/stock/daily/add', { start_date, end_date })
        if (res.data && res.data.success) {
          this.$message.success(res.data && res.data.message ? res.data.message : '补录成功')
        } else {
          this.$message.error(res.data && res.data.message ? res.data.message : '补录失败')
        }
      } catch (e) {
        this.$message.error('补录失败')
      }
    }
  }
}
</script>

<style scoped>
.data-check-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style> 