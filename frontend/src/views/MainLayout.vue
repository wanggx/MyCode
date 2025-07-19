<template>
  <el-container class="main-layout-vertical">
    <el-header class="main-header-bar">
      <div class="header-left">
        <img src="@/assets/logo.png" alt="平台Logo" class="finance-logo" />
        <span class="logo-title">平台</span>
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
    <el-main class="main-content-vertical">
      <div class="menu-content-wrapper">
        <el-menu :default-active="activeMenu" @select="onMenuSelect" class="main-menu-vertical">
          <el-menu-item v-for="item in menus" :key="item.key" :index="item.key">
            <span>{{ item.title }}</span>
          </el-menu-item>
        </el-menu>
        <div class="main-view-content">
          <transition name="fade" mode="out-in">
            <DataTable v-if="activeMenu === 'table'" :key="'table'" />
            <StockSelect v-else-if="activeMenu === 'stockselect'" :key="'stockselect'" />
            <DataCheck v-else-if="activeMenu === 'datacheck'" :key="'datacheck'" />
            <SystemSettings v-else-if="activeMenu === 'settings'" :key="'settings'" />
          </transition>
        </div>
      </div>
    </el-main>

    <!-- 修改密码对话框 -->
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
import DataTable from './DataTable.vue'
import StockSelect from './StockSelect.vue'
import DataCheck from './DataCheck.vue'
import SystemSettings from './SystemSettings.vue'
import axios from '@/config/axios'

export default {
  name: 'MainLayout',
  components: {
    DataTable,
    StockSelect,
    DataCheck,
    SystemSettings,
    ArrowDown
  },
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    return {
      menus: [
        { key: 'table', title: '股票列表' },
        { key: 'stockselect', title: '选股列表' },
        { key: 'datacheck', title: '数据补录' },
        { key: 'settings', title: '系统设置' }
      ],
      activeMenu: 'table',
      passwordDialogVisible: false,
      changePasswordLoading: false,
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      passwordRules: {
        oldPassword: [
          { required: true, message: '请输入原密码', trigger: 'blur' }
        ],
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
    },
    handleCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
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
      this.passwordForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
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
.account-dropdown {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
.account-dropdown:hover {
  color: #66b1ff;
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

.tushare-link {
  font-size: 14px;
  color: #409eff;
  text-decoration: none;
  margin-right: 8px;
}
.tushare-link:hover {
  text-decoration: underline;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
