<template>
  <el-container class="main-layout">
    <el-aside width="180px" class="sidebar">
      <div class="sidebar-logo">
        <img src="@/assets/logo.png" alt="Logo" class="logo-img" />
        <span class="logo-title">量化平台</span>
      </div>
      <el-menu :default-active="activeMenu" router class="sidebar-menu" :collapse="false" background-color="#001529" text-color="#ffffffb3" active-text-color="#ffffff">
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <span class="menu-icon">{{ item.icon }}</span>
          <span class="menu-text">{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="main-right">
      <el-header class="top-header" height="40px">
        <div class="header-left">
          <span class="data-date">数据日期: {{ dataDate }}</span>
        </div>
        <div class="header-right">
          <a href="http://tushare.pro/" target="_blank" class="tushare-link">Tushare官网</a>
          <el-dropdown @command="handleCommand" trigger="click">
            <span class="account-dropdown">
              {{ user ? user.username : '' }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px" :close-on-click-modal="false">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword" :loading="changePasswordLoading">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { ArrowDown } from '@element-plus/icons-vue'
import axios from '@/config/axios'

export default {
  name: 'MainLayout',
  components: { ArrowDown },
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    return {
      menuItems: [
        { path: '/workspace', title: '工作台', icon: '📊' },
        { path: '/strategies', title: '策略研究', icon: '📝' },
        { path: '/backtest', title: '回测中心', icon: '⚡' },
        { path: '/paper-trading', title: '模拟交易', icon: '📝' },
        { path: '/trading', title: '实盘交易', icon: '🔴' },
        { path: '/factors', title: '因子研究', icon: '🔬' },
        { path: '/tasks', title: '任务中心', icon: '⏰' },
        { path: '/data', title: '数据中心', icon: '📈' },
        { path: '/settings', title: '系统设置', icon: '⚙' }
      ],
      passwordDialogVisible: false,
      changePasswordLoading: false,
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      passwordRules: {
        oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters(['user']),
    activeMenu() {
      return this.$route.path
    },
    dataDate() {
      const d = new Date()
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    }
  },
  methods: {
    ...mapActions(['logout']),
    handleCommand(command) {
      if (command === 'logout') {
        this.logout()
        this.$router.push('/login')
      } else if (command === 'changePassword') {
        this.passwordDialogVisible = true
      }
    },
    async handleChangePassword() {
      try {
        await this.$refs.passwordFormRef.validate()
        this.changePasswordLoading = true
        const res = await axios.post('/api/user/change-password', {
          old_password: this.passwordForm.oldPassword,
          new_password: this.passwordForm.newPassword
        })
        if (res.data && res.data.success) {
          this.$message.success('密码修改成功')
          this.passwordDialogVisible = false
          this.resetPasswordForm()
        } else {
          this.$message.error(res.data.message || '密码修改失败')
        }
      } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
          this.$message.error(e.response.data.error)
        } else {
          this.$message.error('密码修改失败')
        }
      } finally {
        this.changePasswordLoading = false
      }
    },
    resetPasswordForm() {
      this.passwordForm = { oldPassword: '', newPassword: '', confirmPassword: '' }
      this.$refs.passwordFormRef.resetFields()
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
.main-layout { height: 100vh; }
.sidebar { background: #001529; overflow-y: auto; overflow-x: hidden; }
.sidebar-logo { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid #ffffff1a; }
.logo-img { width: 24px; height: 24px; margin-right: 8px; }
.logo-title { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.sidebar-menu { border-right: none; }
.sidebar-menu .el-menu-item { height: 44px; line-height: 44px; }
.sidebar-menu .el-menu-item .menu-icon { font-size: 16px; margin-right: 10px; }
.sidebar-menu .el-menu-item .menu-text { font-size: 14px; }
.sidebar-menu .el-menu-item.is-active { background-color: #007f7a !important; }
.sidebar-menu .el-menu-item:hover { background-color: #ffffff1a !important; }
.main-right { display: flex; flex-direction: column; overflow: hidden; }
.top-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; }
.header-left { display: flex; align-items: center; }
.data-date { font-size: 13px; color: #909399; }
.header-right { display: flex; align-items: center; gap: 8px; }
.tushare-link { font-size: 13px; color: #007f7a; text-decoration: none; }
.tushare-link:hover { text-decoration: underline; }
.account-dropdown { font-size: 14px; color: #007f7a; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.account-dropdown:hover { color: #00a39e; }
.main-content { flex: 1; overflow-y: auto; background: #f5f7fa; padding: 0; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 12px; }
</style>
