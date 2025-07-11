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
      <div v-if="activeMenu === 'users'">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span>用户列表</span>
              <el-button type="primary" size="small" @click="refreshUsers">刷新数据</el-button>
            </div>
          </template>
          <div class="table-wrapper">
            <el-table :data="userData" style="width: 100%" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="姓名" width="120" />
              <el-table-column prop="age" label="年龄" width="80" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="address" label="地址" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === '活跃' ? 'success' : 'info'">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </div>
      <div v-else-if="activeMenu === 'orders'">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span>订单列表</span>
              <el-button type="primary" size="small" @click="refreshOrders">刷新数据</el-button>
            </div>
          </template>
          <div class="table-wrapper">
            <el-table :data="orderData" style="width: 100%" stripe>
              <el-table-column prop="orderId" label="订单号" width="120" />
              <el-table-column prop="customer" label="客户" width="100" />
              <el-table-column prop="product" label="产品" />
              <el-table-column prop="amount" label="金额" width="100">
                <template #default="scope">
                  ¥{{ scope.row.amount }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getOrderStatusType(scope.row.status)">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="date" label="日期" width="120" />
            </el-table>
          </div>
        </el-card>
      </div>
      <div v-else-if="activeMenu === 'products'">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <span>产品列表</span>
              <el-button type="primary" size="small" @click="refreshProducts">刷新数据</el-button>
            </div>
          </template>
          <div class="table-wrapper">
            <el-table :data="productData" style="width: 100%" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="产品名称" />
              <el-table-column prop="category" label="分类" width="100" />
              <el-table-column prop="price" label="价格" width="100">
                <template #default="scope">
                  ¥{{ scope.row.price }}
                </template>
              </el-table-column>
              <el-table-column prop="stock" label="库存" width="80" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === '在售' ? 'success' : 'danger'">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script>
export default {
  name: 'DataTable',
  data() {
    return {
      menus: [
        { key: 'users', title: '用户列表' },
        { key: 'orders', title: '订单列表' },
        { key: 'products', title: '产品列表' }
      ],
      activeMenu: 'users',
      userData: [
        { id: 1, name: '张三', age: 25, email: 'zhangsan@example.com', address: '上海市浦东新区', status: '活跃' },
        { id: 2, name: '李四', age: 30, email: 'lisi@example.com', address: '北京市朝阳区', status: '活跃' },
        { id: 3, name: '王五', age: 28, email: 'wangwu@example.com', address: '广州市天河区', status: '离线' },
        { id: 4, name: '赵六', age: 35, email: 'zhaoliu@example.com', address: '深圳市南山区', status: '活跃' },
        { id: 5, name: '钱七', age: 27, email: 'qianqi@example.com', address: '杭州市西湖区', status: '离线' }
      ],
      orderData: [
        { orderId: 'ORD001', customer: '张三', product: 'iPhone 15', amount: 5999, status: '已完成', date: '2024-01-15' },
        { orderId: 'ORD002', customer: '李四', product: 'MacBook Pro', amount: 12999, status: '处理中', date: '2024-01-14' },
        { orderId: 'ORD003', customer: '王五', product: 'iPad Air', amount: 3999, status: '已发货', date: '2024-01-13' },
        { orderId: 'ORD004', customer: '赵六', product: 'AirPods Pro', amount: 1999, status: '已完成', date: '2024-01-12' },
        { orderId: 'ORD005', customer: '钱七', product: 'Apple Watch', amount: 2999, status: '已取消', date: '2024-01-11' }
      ],
      productData: [
        { id: 1, name: 'iPhone 15', category: '手机', price: 5999, stock: 50, status: '在售' },
        { id: 2, name: 'MacBook Pro', category: '电脑', price: 12999, stock: 20, status: '在售' },
        { id: 3, name: 'iPad Air', category: '平板', price: 3999, stock: 30, status: '在售' },
        { id: 4, name: 'AirPods Pro', category: '耳机', price: 1999, stock: 100, status: '在售' },
        { id: 5, name: 'Apple Watch', category: '手表', price: 2999, stock: 0, status: '缺货' }
      ]
    }
  },
  methods: {
    onMenuSelect(key) {
      this.activeMenu = key
    },
    refreshUsers() {
      this.$message.success('用户数据已刷新')
    },
    refreshOrders() {
      this.$message.success('订单数据已刷新')
    },
    refreshProducts() {
      this.$message.success('产品数据已刷新')
    },
    getOrderStatusType(status) {
      const statusMap = {
        '已完成': 'success',
        '处理中': 'warning',
        '已发货': 'primary',
        '已取消': 'danger'
      }
      return statusMap[status] || 'info'
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
.table-card {
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.table-wrapper {
  min-width: 0;
  overflow-x: auto;
}
</style> 