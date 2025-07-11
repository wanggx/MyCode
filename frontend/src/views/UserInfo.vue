<template>
  <el-container class="main-layout">
    <el-aside width="200px" class="main-aside">
      <el-menu :default-active="activeMenu" @select="onMenuSelect" router>
        <el-menu-item v-for="item in menus" :key="item.key" :index="item.key">
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="main-content-container">
      <el-header class="main-header">
        <div class="header-right">
          <span class="account">账号：{{ user ? user.username : '' }}</span>
          <el-button class="logout-btn" type="danger" size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <div v-if="activeMenu === 'info'">
          <el-descriptions :title="'用户信息'" :column="1">
            <el-descriptions-item label="用户名">{{ user ? user.username : '' }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ user ? (user.email || '未设置') : '' }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{ user ? (user.role || '普通用户') : '' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div v-else-if="activeMenu === 'table'">
          <div class="table-wrapper">
            <el-table :data="tableData" style="width: 100%">
              <el-table-column prop="date" label="日期" width="180" />
              <el-table-column prop="name" label="姓名" width="180" />
              <el-table-column prop="address" label="地址" />
            </el-table>
          </div>
        </div>
        <div v-else-if="activeMenu === 'about'">
          <el-card>
            <h3>关于本系统</h3>
            <p>这是一个基于 Vue3 + Element Plus 的前端 mock 演示系统。</p>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
export default {
  name: 'UserInfoPage',
  data() {
    return {
      menus: [
        { key: 'info', title: '用户信息' },
        { key: 'table', title: '数据表格' },
        { key: 'about', title: '关于' }
      ],
      activeMenu: 'info',
      tableData: [
        { date: '2023-06-01', name: '张三', address: '上海市' },
        { date: '2023-06-02', name: '李四', address: '北京市' },
        { date: '2023-06-03', name: '王五', address: '广州市' }
      ]
    }
  },
  computed: {
    ...mapGetters(['user'])
  },
  methods: {
    ...mapActions(['logout']),
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    },
    onMenuSelect(key) {
      this.activeMenu = key
    }
  },
  mounted() {
    if (!this.user) {
      this.$store.dispatch('fetchUser')
    }
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  min-width: 0;
}
.main-aside {
  background: #f8f9fa;
  border-right: 1px solid #e4e7ed;
  min-height: 100vh;
  z-index: 2;
  position: relative;
}
.main-content-container {
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 0;
  flex: 1;
  overflow: hidden;
}
.main-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  height: 60px;
  z-index: 1;
}
.header-right {
  display: flex;
  align-items: center;
}
.account {
  font-size: 15px;
  color: #409eff;
  font-weight: 500;
  margin-right: 18px;
}
.logout-btn {
  margin-left: 0;
}
.main-content {
  padding: 32px 24px;
  overflow: auto;
  min-width: 0;
}
.table-wrapper {
  min-width: 0;
  overflow-x: auto;
}
</style> 