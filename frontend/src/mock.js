import axios from 'axios'

// 模拟用户数据库
let users = [
  { username: 'test', password: '123456', email: 'test@example.com', role: '管理员' }
]

// 拦截注册
axios.interceptors.request.use(async config => {
  if (config.url === '/api/register' && config.method === 'post') {
    const { username, password } = config.data
    if (users.find(u => u.username === username)) {
      return Promise.reject({ response: { data: { message: '用户名已存在' } } })
    }
    users.push({ username, password, email: '', role: '普通用户' })
    return {
      ...config,
      adapter: () => Promise.resolve({
        data: { message: '注册成功' },
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      })
    }
  }
  return config
})

// 拦截登录
axios.interceptors.request.use(async config => {
  if (config.url === '/api/login' && config.method === 'post') {
    const { username, password } = config.data
    const user = users.find(u => u.username === username && u.password === password)
    if (!user) {
      return Promise.reject({ response: { data: { message: '用户名或密码错误' } } })
    }
    return {
      ...config,
      adapter: () => Promise.resolve({
        data: {
          token: 'mock-token-' + username,
          user: { username: user.username, email: user.email, role: user.role }
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      })
    }
  }
  return config
})

// 拦截获取用户信息
axios.interceptors.request.use(async config => {
  if (config.url === '/api/user' && config.method === 'get') {
    // 简单模拟 token 校验
    const token = config.headers.Authorization
    if (!token) {
      return Promise.reject({ response: { data: { message: '未登录' } } })
    }
    const username = token.replace('Bearer mock-token-', '')
    const user = users.find(u => u.username === username)
    if (!user) {
      return Promise.reject({ response: { data: { message: '用户不存在' } } })
    }
    return {
      ...config,
      adapter: () => Promise.resolve({
        data: { username: user.username, email: user.email, role: user.role },
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      })
    }
  }
  return config
}) 