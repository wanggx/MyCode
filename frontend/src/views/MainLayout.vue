<template>
  <el-container class="main-layout">
    <el-aside width="200px" class="main-aside">
      <el-menu :default-active="activeMenu" @select="onMenuSelect">
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
        <transition name="fade" mode="out-in">
          <UserInfo v-if="activeMenu === 'userinfo'" :key="'userinfo'" />
          <ChartView v-else-if="activeMenu === 'chart'" :key="'chart'" />
          <DataTable v-else-if="activeMenu === 'table'" :key="'table'" />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import UserInfo from './UserInfo.vue'
import ChartView from './ChartView.vue'
import DataTable from './DataTable.vue'

export default {
  name: 'MainLayout',
  components: {
    UserInfo,
    ChartView,
    DataTable
  },
  data() {
    return {
      menus: [
        { key: 'userinfo', title: '用户信息' },
        { key: 'chart', title: '数据图表' },
        { key: 'table', title: '数据表格' }
      ],
      activeMenu: 'userinfo'
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
  padding: 0;
  overflow: hidden;
  min-width: 0;
  position: relative;
}
/* 切换动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style> 