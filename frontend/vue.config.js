const { defineConfig } = require('@vue/cli-service')
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // Flask 后端地址
        changeOrigin: true,
        pathRewrite: {
          '^/api': '' // 请求时使用 /api/login 会代理到 http://localhost:5000/login
        }
      }
    }
  }
}

