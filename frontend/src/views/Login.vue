<template>
  <el-card class="login-card">
    <el-tabs v-model="activeTab" stretch>
      <el-tab-pane label="登录" name="login">
        <el-form :model="loginForm" @submit.prevent="onLogin" label-width="80px" class="login-form">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" autocomplete="username" clearable @keyup.enter="onLogin" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" autocomplete="current-password" clearable @keyup.enter="onLogin" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onLogin" class="login-btn">登录</el-button>
          </el-form-item>
          <el-alert v-if="loginError" :title="loginError" type="error" show-icon class="login-alert" />
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="注册" name="register">
        <el-form :model="registerForm" @submit.prevent="onRegister" label-width="80px" class="login-form">
          <el-form-item label="用户名">
            <el-input v-model="registerForm.username" clearable />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="registerForm.password" type="password" clearable />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="registerForm.confirm" type="password" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onRegister" class="login-btn">注册</el-button>
          </el-form-item>
          <el-alert v-if="registerError" :title="registerError" type="error" show-icon class="login-alert" />
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script>
import { mapActions } from 'vuex'
import axios from 'axios'
export default {
  name: 'LoginPage',
  data() {
    return {
      activeTab: 'login',
      loginForm: { username: '', password: '' },
      registerForm: { username: '', password: '', confirm: '' },
      loginError: '',
      registerError: ''
    }
  },
  methods: {
    ...mapActions(['login']),
    async onLogin() {
      this.loginError = ''
      try {
        await this.login(this.loginForm)
        this.$router.push('/user')
      } catch (e) {
        this.loginError = '登录失败，请检查用户名和密码'
      }
    },
    async onRegister() {
      this.registerError = ''
      if (this.registerForm.password !== this.registerForm.confirm) {
        this.registerError = '两次密码不一致'
        return
      }
      try {
        await axios.post('/api/register', {
          username: this.registerForm.username,
          password: this.registerForm.password
        })
        this.activeTab = 'login'
      } catch (e) {
        this.registerError = (e.response && e.response.data && e.response.data.message) || '注册失败，请重试'
      }
    }
  }
}
</script>

<style scoped>
.login-card {
  max-width: 380px;
  margin: 80px auto 0 auto;
  padding: 36px 32px 28px 32px;
  border-radius: 18px;
  box-shadow: 0 4px 24px 0 rgba(60, 120, 200, 0.10);
  background: #fff;
  transition: box-shadow 0.3s;
}
.login-card:hover {
  box-shadow: 0 8px 32px 0 rgba(60, 120, 200, 0.18);
}
.login-form {
  margin-top: 18px;
}
.el-form-item {
  margin-bottom: 22px;
}
.el-form-item__label {
  text-align: left;
  color: #333;
  font-weight: 500;
  font-size: 15px;
}
.el-input {
  width: 100%;
}
.login-btn {
  width: 100%;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  margin-bottom: 6px;
  transition: background 0.2s;
}
.login-btn:hover {
  background: #409eff;
}
.login-alert {
  margin-top: 10px;
}
h2 {
  margin-bottom: 10px;
  font-weight: 700;
  color: #409eff;
  letter-spacing: 2px;
}
</style> 