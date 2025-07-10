<template>
  <div class="login">
    <h2>登录</h2>
    <form @submit.prevent="submitLogin">
      <div class="input-group">
        <label for="username">用户名：</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="input-group">
        <label for="password">密码：</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">登录</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginApp',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async submitLogin() {
      try {
        const response = await axios.post('/api/login', {
          username: this.username,
          password: this.password
        });

        // 登录成功处理逻辑，例如跳转页面或保存 token
        alert('登录成功');
        console.log('Response:', response.data);
        this.error = '';
      } catch (err) {
        this.error = '登录失败，请检查用户名和密码';
        console.error(err);
      }
    }
  }
};
</script>

<style scoped>
.login {
  width: 300px;
  margin: 60px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  text-align: left;
}

.input-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

button:hover {
  background-color: #369d6b;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
