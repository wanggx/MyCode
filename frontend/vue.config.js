const { defineConfig } = require('@vue/cli-service')

// 根據環境變量決定後端地址
const getBackendUrl = () => {
  const env = process.env.NODE_ENV || 'development'
  
  switch (env) {
    case 'development':
      return process.env.VUE_APP_BACKEND_URL || 'http://localhost:8080'
    case 'test':
      return process.env.VUE_APP_BACKEND_URL || 'http://test-backend:8080'
    case 'production':
      return process.env.VUE_APP_BACKEND_URL || 'http://production-backend:8080'
    default:
      return 'http://localhost:8080'
  }
}

module.exports = defineConfig({
  devServer: {
    proxy: {
      '/api': {
        target: getBackendUrl(),
        changeOrigin: true,
        logLevel: 'debug', // 開發時顯示代理日誌
        // 移除 pathRewrite，保持 /api 前缀
      }
    }
  }
})

