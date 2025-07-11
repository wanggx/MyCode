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
      <div v-if="activeMenu === 'basic'">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ user ? user.username : '' }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ user ? (user.email || '未设置') : '' }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{ user ? (user.role || '普通用户') : '' }}</el-descriptions-item>
            <el-descriptions-item label="登录时间">{{ loginTime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>
      <div v-else-if="activeMenu === 'settings'">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>账户设置</span>
            </div>
          </template>
          <el-form label-width="100px">
            <el-form-item label="修改密码">
              <el-button type="primary">修改密码</el-button>
            </el-form-item>
            <el-form-item label="通知设置">
              <el-switch v-model="notificationEnabled" />
            </el-form-item>
          </el-form>
        </el-card>
      </div>
      <div v-else-if="activeMenu === 'history'">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>登录历史</span>
            </div>
          </template>
          <el-table :data="loginHistory" style="width: 100%">
            <el-table-column prop="time" label="登录时间" />
            <el-table-column prop="ip" label="IP地址" />
            <el-table-column prop="device" label="设备" />
          </el-table>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'UserInfo',
  data() {
    return {
      menus: [
        { key: 'basic', title: '基本信息' },
        { key: 'settings', title: '账户设置' },
        { key: 'history', title: '登录历史' }
      ],
      activeMenu: 'basic',
      loginTime: new Date().toLocaleString(),
      notificationEnabled: true,
      loginHistory: [
        { time: '2024-01-15 10:30:00', ip: '192.168.1.100', device: 'Chrome/Windows' },
        { time: '2024-01-14 15:20:00', ip: '192.168.1.100', device: 'Chrome/Windows' },
        { time: '2024-01-13 09:15:00', ip: '192.168.1.101', device: 'Safari/Mac' }
      ]
    }
  },
  computed: {
    ...mapGetters(['user'])
  },
  methods: {
    onMenuSelect(key) {
      this.activeMenu = key
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
.info-card {
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 