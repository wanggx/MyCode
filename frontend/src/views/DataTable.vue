<template>
  <div class="stock-table-page">
    <el-card class="stock-table-card">
      <div class="search-bar">
        <div class="search-left">
          <el-input v-model="searchForm.code" placeholder="股票代码" class="search-input" clearable />
          <el-input v-model="searchForm.name" placeholder="名称" class="search-input" clearable />
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </div>
        <div class="search-right">
          <el-button type="success" @click="handleSync" :loading="syncLoading">同步Tushare列表</el-button>
        </div>
      </div>
      <div class="table-wrapper">
        <el-table :data="tableData" stripe border v-loading="loading"
          style="margin-top: 0; min-width: 900px; max-width: 1200px; width: auto;"
          header-cell-class-name="left-align-header" cell-class-name="left-align-cell">
          <el-table-column prop="ts_code" label="TS代码" width="120" align="left" header-align="left">
            <template #default="scope">
              <el-link type="primary" @click="openStockDialog(scope.row.ts_code)">{{ scope.row.ts_code }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="symbol" label="股票代码" width="120" align="left" header-align="left" />
          <el-table-column prop="name" label="股票名称" width="160" align="left" header-align="left" />
          <el-table-column prop="area" label="地域" width="120" align="left" header-align="left" />
          <el-table-column prop="industry" label="行业" width="120" align="left" header-align="left" />
          <el-table-column prop="market" label="市场" width="100" align="left" header-align="left" />
          <el-table-column prop="list_date" label="上市日期" width="120" align="left" header-align="left" />
        </el-table>
      </div>
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
    <el-dialog
      v-model="stockDialogVisible"
      width="900px"
      :before-close="closeStockDialog"
      title="近60天日线数据"
      append-to-body>
      <template #title>
        <span>近60天日线数据 - {{ stockDialogTsCode }}</span>
        <el-button style="float:right;" icon="el-icon-close" @click="closeStockDialog" circle plain></el-button>
      </template>
      <el-table :data="stockDialogData" stripe border v-loading="stockDialogLoading" style="margin-top: 0; min-width: 800px;">
        <el-table-column prop="ts_code" label="TS代码" width="120" />
        <el-table-column prop="trade_date" label="交易日期" width="120" />
        <el-table-column prop="open" label="开盘价" width="100" />
        <el-table-column prop="high" label="最高价" width="100" />
        <el-table-column prop="low" label="最低价" width="100" />
        <el-table-column prop="close" label="收盘价" width="100" />
        <el-table-column prop="pre_close" label="昨收" width="100" />
        <el-table-column prop="change" label="涨跌额" width="100" />
        <el-table-column prop="pct_chg" label="涨跌幅%" width="100" />
        <el-table-column prop="vol" label="成交量" width="120" />
      </el-table>
      <div class="pagination-bar">
        <el-pagination
          background
          layout="prev, pager, next, jumper, ->, total"
          :total="stockDialogTotal"
          :page-size="stockDialogPageSize"
          v-model:current-page="stockDialogPage"
          @current-change="handleStockDialogPageChange"
        />
      </div>
    </el-dialog>
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
      loading: false,
      syncLoading: false,
      stockDialogVisible: false,
      stockDialogTsCode: '',
      stockDialogData: [],
      stockDialogTotal: 0,
      stockDialogPage: 1,
      stockDialogPageSize: 10,
      stockDialogLoading: false,
      stockDialogStartDate: '',
      stockDialogEndDate: '',
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const params = {
          keyword: this.searchForm.code || this.searchForm.name,
          page: this.page,
          page_size: this.pageSize
        }
        const res = await axios.get('/api/stocks', { params })
        
        // 检查响应数据结构
        if (res.data && res.data.data && res.data.data.stocks) {
          this.tableData = res.data.data.stocks
          this.total = res.data.data.total
        } else {
          // 使用mock数据作为后备
          this.tableData = [
            { ts_code: '000001.SZ', symbol: '1', name: '平安银行', area: '深圳', industry: '银行', market: '主板', list_date: '19910403' },
            { ts_code: '000002.SZ', symbol: '2', name: '万科A', area: '深圳', industry: '房地产', market: '主板', list_date: '19910129' },
            { ts_code: '600519.SH', symbol: '600519', name: '贵州茅台', area: '贵州', industry: '白酒', market: '主板', list_date: '20010827' },
            { ts_code: '002594.SZ', symbol: '2594', name: '比亚迪', area: '深圳', industry: '汽车', market: '中小板', list_date: '20110630' }
          ]
          this.total = this.tableData.length
        }
      } catch (e) {
        console.error('获取数据失败:', e)
        this.$message.error('获取数据失败')
        // 使用mock数据作为后备
        this.tableData = [
          { ts_code: '000001.SZ', symbol: '1', name: '平安银行', area: '深圳', industry: '银行', market: '主板', list_date: '19910403' },
          { ts_code: '000002.SZ', symbol: '2', name: '万科A', area: '深圳', industry: '房地产', market: '主板', list_date: '19910129' },
          { ts_code: '600519.SH', symbol: '600519', name: '贵州茅台', area: '贵州', industry: '白酒', market: '主板', list_date: '20010827' },
          { ts_code: '002594.SZ', symbol: '2594', name: '比亚迪', area: '深圳', industry: '汽车', market: '中小板', list_date: '20110630' }
        ]
        this.total = this.tableData.length
      } finally {
        this.loading = false
      }
    },
    async handleSync() {
      this.syncLoading = true
      try {
        const res = await axios.post('/api/stocks/sync')

        // 判断接口返回的 res.data 是否有 success 字段并为 true
        if (res.data && res.data.success) {
          this.$message.success('同步成功')
          this.fetchData() // 可选：同步后刷新表格数据
        } else {
          const message = res.data.message || '同步失败'
          this.$message.error(message)
        }
      } catch (e) {
        console.error('同步失败:', e)
        this.$message.error('同步失败')
      } finally {
        this.syncLoading = false
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
    openStockDialog(ts_code) {
      // 近60天，endDate为今天，startDate为60天前
      const today = new Date();
      const endDate = today.toISOString().slice(0, 10).replace(/-/g, '');
      const start = new Date(today.getTime() - 59 * 24 * 60 * 60 * 1000);
      const startDate = start.toISOString().slice(0, 10).replace(/-/g, '');
      this.stockDialogTsCode = ts_code;
      this.stockDialogStartDate = startDate;
      this.stockDialogEndDate = endDate;
      this.stockDialogPage = 1;
      this.stockDialogVisible = true;
      this.fetchStockDialogData();
    },
    async fetchStockDialogData() {
      this.stockDialogLoading = true;
      try {
        const res = await axios.get('/api/stock/data', {
          params: {
            ts_code: this.stockDialogTsCode,
            startDate: this.stockDialogStartDate,
            endDate: this.stockDialogEndDate,
            page: this.stockDialogPage,
            page_size: this.stockDialogPageSize
          }
        });
        if (res.data && res.data.data) {
          this.stockDialogData = res.data.data.items;
          this.stockDialogTotal = res.data.data.total;
        } else {
          this.stockDialogData = [];
          this.stockDialogTotal = 0;
        }
      } catch (e) {
        this.$message.error('获取日线数据失败');
        this.stockDialogData = [];
        this.stockDialogTotal = 0;
      } finally {
        this.stockDialogLoading = false;
      }
    },
    handleStockDialogPageChange(val) {
      this.stockDialogPage = val;
      this.fetchStockDialogData();
    },
    closeStockDialog() {
      this.stockDialogVisible = false;
    },
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
  width: 100%;
  margin: 0 auto;
  padding: 0;
  box-sizing: border-box;
}
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 0 16px;
}
.search-left {
  display: flex;
  gap: 16px;
  align-items: center;
}
.search-right {
  display: flex;
  align-items: center;
}
.search-input {
  width: 180px;
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
::v-deep .el-card__body {
  padding: 0;
}
.pagination-bar {
  margin-top: 18px;
  text-align: right;
  padding: 0 16px 16px 16px;
}
</style> 