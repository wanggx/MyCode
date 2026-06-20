const { defineConfig } = require('@vue/cli-service')

const getBackendUrl = () => {
  const env = process.env.NODE_ENV || 'development'
  switch (env) {
    case 'development': return process.env.VUE_APP_BACKEND_URL || 'http://localhost:5000'
    case 'test': return process.env.VUE_APP_BACKEND_URL || 'http://test-backend:5000'
    case 'production': return process.env.VUE_APP_BACKEND_URL || 'http://production-backend:5000'
    default: return 'http://localhost:8080'
  }
}

module.exports = defineConfig({
  devServer: {
    port: 5100,
    client: { overlay: { errors: true, warnings: false, runtimeErrors: false } },
    proxy: {
      '/api': {
        target: getBackendUrl(),
        changeOrigin: true,
      }
    }
  }
})

