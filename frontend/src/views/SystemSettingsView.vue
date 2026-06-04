<template>
  <div class="page-container">
    <div class="page-header">
      <h2>系统设置</h2>
      <p class="page-desc">保留简单配置项，权限登录先轻量实现。</p>
    </div>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">数据源</span></template>
          <el-form label-position="top" :model="form">
            <el-form-item label="Tushare Token">
              <el-input v-model="form.tushare_token" type="password" show-password placeholder="请输入 Tushare Token" />
            </el-form-item>
            <el-form-item label="默认市场">
              <el-select v-model="form.default_market" style="width: 100%">
                <el-option label="A股+港股" value="A股+港股" />
                <el-option label="仅A股" value="仅A股" />
                <el-option label="仅港股" value="仅港股" />
              </el-select>
            </el-form-item>
            <el-button type="primary" @click="handleSaveDataSource">保存</el-button>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">通知</span></template>
          <el-form label-position="top" :model="form">
            <el-form-item label="企业微信 Webhook">
              <el-input v-model="form.webhook_url" placeholder="请输入 Webhook 地址" />
            </el-form-item>
            <el-form-item label="通知级别">
              <el-select v-model="form.notify_level" style="width: 100%">
                <el-option label="成功+异常" value="成功+异常" />
                <el-option label="仅异常" value="仅异常" />
              </el-select>
            </el-form-item>
            <el-button type="primary" @click="handleTestNotify">发送测试</el-button>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">权限</span></template>
          <p class="perm-desc">第一阶段只保留普通用户和管理员。复杂团队权限暂缓。</p>
          <el-button @click="pwdDialogVisible = true">修改密码</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px" :close-on-click-modal="false">
      <el-form :model="pwdForm" label-width="90px" :rules="pwdRules" ref="pwdFormRef">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="pwdLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from '@/config/axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'SystemSettingsView',
  data() {
    const validateConfirm = (rule, value, callback) => {
      if (value !== this.pwdForm.new_password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    return {
      form: {
        tushare_token: '**************',
        default_market: 'A股+港股',
        webhook_url: '',
        notify_level: '成功+异常'
      },
      pwdDialogVisible: false,
      pwdLoading: false,
      pwdForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      pwdRules: {
        old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
        new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度不少于6位', trigger: 'blur' }],
        confirm_password: [{ required: true, message: '请确认新密码', trigger: 'blur' }, { validator: validateConfirm, trigger: 'blur' }]
      }
    }
  },
  methods: {
    handleSaveDataSource() {
      localStorage.setItem('settings_data_source', JSON.stringify({
        tushare_token: this.form.tushare_token,
        default_market: this.form.default_market
      }))
      ElMessage.success('数据源设置已保存')
    },
    handleTestNotify() {
      localStorage.setItem('settings_notify', JSON.stringify({
        webhook_url: this.form.webhook_url,
        notify_level: this.form.notify_level
      }))
      ElMessage.success('测试通知已发送（mock）')
    },
    async handleChangePassword() {
      try {
        await this.$refs.pwdFormRef.validate()
      } catch {
        return
      }
      this.pwdLoading = true
      try {
        await axios.post('/api/user/change-password', {
          old_password: this.pwdForm.old_password,
          new_password: this.pwdForm.new_password
        })
        ElMessage.success('密码修改成功')
        this.pwdDialogVisible = false
        this.pwdForm = { old_password: '', new_password: '', confirm_password: '' }
      } catch {
        ElMessage.error('密码修改失败（mock: 原密码错误）')
      } finally {
        this.pwdLoading = false
      }
    }
  },
  mounted() {
    const ds = localStorage.getItem('settings_data_source')
    if (ds) {
      try {
        const parsed = JSON.parse(ds)
        if (parsed.tushare_token !== undefined) this.form.tushare_token = parsed.tushare_token
        if (parsed.default_market) this.form.default_market = parsed.default_market
      } catch { /* ignore parse errors */ }
    }
    const nt = localStorage.getItem('settings_notify')
    if (nt) {
      try {
        const parsed = JSON.parse(nt)
        if (parsed.webhook_url !== undefined) this.form.webhook_url = parsed.webhook_url
        if (parsed.notify_level) this.form.notify_level = parsed.notify_level
      } catch { /* ignore parse errors */ }
    }
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.card-title { font-size: 15px; font-weight: 600; color: #303133; }
.perm-desc { margin: 0 0 16px; color: #909399; font-size: 13px; line-height: 1.6; }
</style>
