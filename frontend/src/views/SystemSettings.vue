<template>
  <div class="system-settings-page">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-form :model="settingsForm" label-width="120px" class="settings-form">
        <el-form-item label="数据同步">
          <el-button type="primary" @click="handleSyncData" :loading="syncLoading">
            同步股票数据
          </el-button>
          <span class="form-tip">点击同步最新的股票列表数据</span>
        </el-form-item>
        
        <el-form-item label="系统状态">
          <el-tag :type="systemStatus === 'running' ? 'success' : 'warning'">
            {{ systemStatus === 'running' ? '运行中' : '待机中' }}
          </el-tag>
        </el-form-item>
        
        <el-form-item label="数据库连接">
          <el-tag :type="dbStatus === 'connected' ? 'success' : 'danger'">
            {{ dbStatus === 'connected' ? '已连接' : '连接失败' }}
          </el-tag>
        </el-form-item>
        
        <el-form-item label="版本信息">
          <span class="version-info">v1.0.0</span>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from '@/config/axios'

export default {
  name: 'SystemSettings',
  data() {
    return {
      settingsForm: {},
      syncLoading: false,
      systemStatus: 'running',
      dbStatus: 'connected'
    }
  },
  methods: {
    async handleSyncData() {
      this.syncLoading = true
      try {
        const res = await axios.post('/api/stocks/sync')
        if (res.data && res.data.success) {
          this.$message.success('数据同步成功')
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
    }
  },
  mounted() {
    // 可以在这里获取系统状态信息
  }
}
</script>

<style scoped>
.system-settings-page {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}
.settings-card {
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.settings-form {
  margin-top: 20px;
}
.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 14px;
}
.version-info {
  color: #606266;
  font-size: 14px;
}
</style> 