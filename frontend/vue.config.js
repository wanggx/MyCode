const { defineConfig } = require('@vue/cli-service')
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // Flask 后端地址
        changeOrigin: true
        // 移除 pathRewrite，保持 /api 前缀
      }
    }
  }
}

