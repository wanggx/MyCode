<template>
  <div class="system-settings-page">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="关于系统" name="about">
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
        </el-tab-pane>
        <el-tab-pane label="接口Mock" name="mock">
          <el-form label-width="120px" class="mock-form">
            <el-form-item label="Mock接口地址">
              <el-input v-model="mockApiUrl" readonly />
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="mockTsCode" placeholder="请输入股票代码" />
            </el-form-item>
            <el-form-item label="日期">
              <el-date-picker
                v-model="mockDateStr"
                type="date"
                value-format="yyyy-MM-dd"
                placeholder="选择日期"
                style="width: 200px;"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleMockRequest" :loading="mockLoading">请求Mock</el-button>
            </el-form-item>
            <el-form-item label="返回内容">
              <el-input type="textarea" :rows="8" v-model="mockResult" readonly />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import axios from '@/config/axios'

function getTodayYMD() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  return `${yyyy}${mm}${dd}`;
}

export default {
  name: 'SystemSettings',
  data() {
    const todayStr = getTodayYMD();
    console.log('data初始化 mockDateStr:', todayStr);
    return {
      activeTab: 'about',
      settingsForm: {},
      syncLoading: false,
      systemStatus: 'running',
      dbStatus: 'connected',
      // mock tab
      mockApiUrl: '/api/stock/select/mock',
      mockTsCode: '',
      mockDateStr: todayStr,
      mockResult: '',
      mockLoading: false
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
    },
    async handleMockRequest() {
      if (!this.mockTsCode || !this.mockDateStr) {
        this.$message.warning('请填写股票代码和日期')
        return
      }
      this.mockLoading = true
      this.mockResult = ''
      try {
        console.log('mockDateStr:', this.mockDateStr)
        const res = await axios.post(this.mockApiUrl, {
          ts_code: this.mockTsCode,
          date_str: this.mockDateStr
        })
        if (res.data && res.data.result) {
          this.mockResult = res.data.result
        } else if (res.data && res.data.error) {
          this.mockResult = res.data.error
        } else {
          this.mockResult = JSON.stringify(res.data)
        }
      } catch (e) {
        this.mockResult = '请求失败: ' + e
      } finally {
        this.mockLoading = false
      }
    }
  },
  mounted() {
    // 可以在这里获取系统状态信息
  },
  watch: {
    activeTab(val) {
      if (val === 'mock') {
        // this.mockDateStr = getTodayYMD(); // 移除watch中activeTab对mockDateStr的重置
        console.log('watch切换Tab mockDateStr:', this.mockDateStr);
      }
    }
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
.mock-form {
  margin-top: 20px;
  max-width: 600px;
}
</style> 