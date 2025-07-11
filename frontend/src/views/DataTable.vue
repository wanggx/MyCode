<template>
  <el-card class="table-card">
    <h2>数据表格</h2>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="date" label="日期" width="180" />
      <el-table-column prop="name" label="姓名" width="180" />
      <el-table-column prop="address" label="地址" />
    </el-table>
  </el-card>
</template>

<script>
export default {
  name: 'DataTablePage',
  data() {
    return {
      tableData: [
        { date: '2023-06-01', name: '张三', address: '上海市' },
        { date: '2023-06-02', name: '李四', address: '北京市' },
        { date: '2023-06-03', name: '王五', address: '广州市' }
      ]
    }
  }
}
</script>

<style scoped>
.table-card {
  max-width: 800px;
  margin: 60px auto;
  padding: 30px 20px;
}
</style> 