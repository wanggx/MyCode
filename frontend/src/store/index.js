import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('token') || ''
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    logout(state) {
      state.user = null
      state.token = ''
      localStorage.removeItem('token')
    }
  },
  actions: {
    async login({ commit }, { username, password }) {
      const res = await axios.post('/api/user/login', { username, password })
      if (res.data.message === '登录成功') {
        commit('setToken', res.data.data.token)
        commit('setUser', res.data.data.user)
      } else {
        throw new Error(res.data.error || '登录失败')
      }
    },
    async fetchUser({ commit, state }) {
      if (!state.token) return
      const res = await axios.get('/api/user/info', {
        headers: { Authorization: `Bearer ${state.token}` }
      })
      if (res.data.message === '获取成功') {
        commit('setUser', res.data.data)
      } else {
        throw new Error(res.data.error || '获取用户信息失败')
      }
    },
    logout({ commit }) {
      commit('logout')
    }
  },
  getters: {
    isAuthenticated: state => !!state.token,
    user: state => state.user
  }
}) 