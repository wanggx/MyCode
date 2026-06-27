import { fetchBacktests, fetchBacktest, createBacktest, cancelBacktest, deleteBacktest, fetchNav, fetchTrades, fetchPositions, fetchRiskMetrics, fetchLogs } from '@/api/backtest'

export default {
  namespaced: true,
  state: () => ({
    list: [], total: 0,
    current: null,
    navData: null, trades: null, positions: null, riskMetrics: null, logs: null,
    running: null,
    loading: false
  }),
  mutations: {
    SET_LIST(state, { items, total }) { state.list = items; state.total = total },
    SET_CURRENT(state, bt) { state.current = bt },
    SET_NAV(state, d) { state.navData = d },
    SET_TRADES(state, d) { state.trades = d },
    SET_POSITIONS(state, d) { state.positions = d },
    SET_RISK(state, d) { state.riskMetrics = d },
    SET_LOGS(state, d) { state.logs = d },
    SET_RUNNING(state, bt) { state.running = bt },
    SET_LOADING(state, v) { state.loading = v }
  },
  actions: {
    async loadList({ commit }, params = {}) {
      commit('SET_LOADING', true)
      try {
        const res = await fetchBacktests(params)
        if (res.data?.success) commit('SET_LIST', res.data.data)
      } finally { commit('SET_LOADING', false) }
    },
    async loadDetail({ commit }, id) {
      const res = await fetchBacktest(id)
      if (res.data?.success) commit('SET_CURRENT', res.data.data)
      return res.data?.data
    },
    async create({ dispatch }, data) {
      try {
        const res = await createBacktest(data)
        if (res.data?.success) await dispatch('loadList')
        return res.data
      } catch (e) {
        return e.response?.data || { success: false, error: e.message || '创建失败' }
      }
    },
    async cancel({ dispatch }, id) {
      await cancelBacktest(id)
      await dispatch('loadList')
    },
    async remove({ dispatch }, id) {
      await deleteBacktest(id)
      await dispatch('loadList')
    },
    async loadNav({ commit }, id) {
      const res = await fetchNav(id, { format: 'full' })
      if (res.data?.success) commit('SET_NAV', res.data.data)
      return res.data?.data
    },
    async loadTrades({ commit }, { id, page, pageSize } = {}) {
      const res = await fetchTrades(id, { page: page || 1, page_size: pageSize || 200 })
      if (res.data?.success) commit('SET_TRADES', res.data.data)
      return res.data?.data
    },
    async loadPositions({ commit }, id) {
      const res = await fetchPositions(id)
      if (res.data?.success) commit('SET_POSITIONS', res.data.data)
      return res.data?.data
    },
    async loadRiskMetrics({ commit }, id) {
      const res = await fetchRiskMetrics(id)
      if (res.data?.success) commit('SET_RISK', res.data.data)
      return res.data?.data
    },
    async loadLogs({ commit }, { id, debug }) {
      const res = await fetchLogs(id, { debug: debug ? 'true' : 'false' })
      if (res.data?.success) commit('SET_LOGS', res.data.data)
      return res.data?.data
    }
  }
}
