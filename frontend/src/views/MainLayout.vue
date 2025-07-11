<template>
  <el-container class="main-layout-vertical">
    <el-header class="main-header-bar">
      <div class="header-left">
        <img src="@/assets/logo.png" alt="平台Logo" class="finance-logo" />
        <span class="logo-title">平台</span>
      </div>
      <div class="header-right">
        <span class="account">{{ user ? user.username : '' }}</span>
        <el-button class="logout-btn" type="danger" size="small" @click="handleLogout">退出</el-button>
      </div>
    </el-header>
    <el-main class="main-content-vertical">
      <div class="menu-content-wrapper">
        <el-menu :default-active="activeMenu" @select="onMenuSelect" class="main-menu-vertical">
          <el-menu-item v-for="item in menus" :key="item.key" :index="item.key">
            <span>{{ item.title }}</span>
          </el-menu-item>
        </el-menu>
        <div class="main-view-content">
          <transition name="fade" mode="out-in">
            <UserInfo v-if="activeMenu === 'userinfo'" :key="'userinfo'" />
            <ChartView v-else-if="activeMenu === 'chart'" :key="'chart'" />
            <DataTable v-else-if="activeMenu === 'table'" :key="'table'" />
          </transition>
        </div>
      </div>
    </el-main>
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
.main-layout-vertical {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main-header-bar {
  width: 100%;
  height: 30px !important;
  min-height: 30px !important;
  max-height: 30px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  box-sizing: border-box;
}
.header-left {
  display: flex;
  align-items: center;
}
.finance-logo {
  width: 22px;
  height: 22px;
  margin-right: 8px;
}
.logo-title {
  font-size: 15px;
  font-weight: bold;
  color: #409eff;
  letter-spacing: 1px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.account {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}
.logout-btn {
  height: 28px;
  padding: 0 12px;
  font-size: 13px;
}
.main-content-vertical {
  flex: 1;
  padding: 0;
  background: #f8f9fa;
}
.menu-content-wrapper {
  display: flex;
  flex-direction: row;
  height: 100%;
}
.main-menu-vertical {
  width: 180px;
  min-width: 120px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  height: 100%;
}
.main-view-content {
  flex: 1;
  padding: 24px;
  min-width: 0;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style> 