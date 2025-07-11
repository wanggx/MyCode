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
      const res = await axios.post('/api/login', { username, password })
      commit('setToken', res.data.token)
      commit('setUser', res.data.user)
    },
    async fetchUser({ commit, state }) {
      if (!state.token) return
      const res = await axios.get('/api/user', {
        headers: { Authorization: `Bearer ${state.token}` }
      })
      commit('setUser', res.data)
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