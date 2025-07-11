// API 配置文件
const config = {
  // 開發環境
  development: {
    baseURL: '/api',
    timeout: 5000
  },
  // 測試環境
  test: {
    baseURL: '/api',
    timeout: 5000
  },
  // 生產環境
  production: {
    baseURL: '/api',
    timeout: 10000
  }
}

// 獲取當前環境
const env = process.env.NODE_ENV || 'development'

// 導出當前環境的配置
export default config[env]

// 導出所有配置
export { config } 