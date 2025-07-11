<template>
  <el-card class="register-card">
    <h2>注册</h2>
    <el-form :model="form" @submit.prevent="onRegister">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="form.confirm" type="password" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onRegister">注册</el-button>
        <el-button type="text" @click="$router.push('/login')">返回登录</el-button>
      </el-form-item>
      <el-alert v-if="error" :title="error" type="error" show-icon />
    </el-form>
  </el-card>
</template>

<script>
import axios from 'axios'
export default {
  name: 'RegisterPage',
  data() {
    return {
      form: { username: '', password: '', confirm: '' },
      error: ''
    }
  },
  methods: {
    async onRegister() {
      if (this.form.password !== this.form.confirm) {
        this.error = '两次密码不一致'
        return
      }
      try {
        const response = await axios.post('/api/user/register', {
          username: this.form.username,
          password: this.form.password
        })
        
        if (response.data.message === '注册成功') {
          this.$message.success('注册成功，请登录');
          this.$router.push('/login')
        } else {
          this.error = response.data.error || '注册失败';
        }
      } catch (e) {
        this.error = e.response?.data?.error || '注册失败，请重试'
      }
    }
  }
}
</script>

<style scoped>
.register-card {
  max-width: 400px;
  margin: 80px auto;
  padding: 30px 20px;
}
</style> 