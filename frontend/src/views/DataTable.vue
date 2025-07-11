<template>
  <div class="stock-table-page">
    <el-card class="stock-table-card">
      <div class="search-bar">
        <el-input v-model="searchForm.code" placeholder="股票代码" class="search-input" clearable />
        <el-input v-model="searchForm.name" placeholder="名称" class="search-input" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <el-table :data="tableData" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="code" label="股票代码" width="120" />
        <el-table-column prop="name" label="名称" width="160" />
        <el-table-column prop="region" label="上市地区" width="120" />
        <el-table-column prop="industry" label="行业" />
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
  name: 'DataTable',
  data() {
    return {
      searchForm: {
        code: '',
        name: ''
      },
      tableData: [],
      total: 0,
      page: 1,
      pageSize: 10,
      loading: false
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const params = {
          code: this.searchForm.code,
          name: this.searchForm.name,
          page: this.page,
          page_size: this.pageSize
        }
        const res = await axios.get('/api/stocks', { params })
        // 判断data是否为数组，否则用mock数据
        if (Array.isArray(res.data.data)) {
          this.tableData = res.data.data
        } else {
          // mock数据
          this.tableData = [
            { code: '600000', name: '浦发银行', region: '上海', industry: '银行' },
            { code: '000001', name: '平安银行', region: '深圳', industry: '银行' },
            { code: '600519', name: '贵州茅台', region: '上海', industry: '白酒' },
            { code: '300750', name: '宁德时代', region: '深圳', industry: '新能源' }
          ]
        }
        this.total = res.data.total || this.tableData.length
      } catch (e) {
        this.$message.error('获取数据失败')
        // mock数据
        this.tableData = [
          { code: '600000', name: '浦发银行', region: '上海', industry: '银行' },
          { code: '000001', name: '平安银行', region: '深圳', industry: '银行' },
          { code: '600519', name: '贵州茅台', region: '上海', industry: '白酒' },
          { code: '300750', name: '宁德时代', region: '深圳', industry: '新能源' }
        ]
        this.total = this.tableData.length
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
    }
  },
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
.stock-table-page {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}
.stock-table-card {
  max-width: 900px;
  margin: 0 auto;
}
.search-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}
.search-input {
  width: 180px;
}
.pagination-bar {
  margin-top: 18px;
  text-align: right;
}
</style> 