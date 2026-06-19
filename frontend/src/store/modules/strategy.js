import { fetchStrategies, fetchStrategy, createStrategy, updateStrategy, deleteStrategy, patchStrategyStatus, fetchVersions, createVersion, fetchVersion } from '@/api/strategy'

export default {
  namespaced: true,
  state: () => ({
    list: [],
    total: 0,
    current: null,
    versions: [],
    currentVersionCode: '',
    loading: false
  }),
  mutations: {
    SET_LIST(state, { items, total }) { state.list = items; state.total = total },
    SET_CURRENT(state, s) { state.current = s },
    SET_VERSIONS(state, v) { state.versions = v },
    SET_VERSION_CODE(state, code) { state.currentVersionCode = code },
    SET_LOADING(state, v) { state.loading = v }
  },
  actions: {
    async loadList({ commit }, params = {}) {
      commit('SET_LOADING', true)
      try {
        const res = await fetchStrategies(params)
        if (res.data?.success) commit('SET_LIST', res.data.data)
      } finally { commit('SET_LOADING', false) }
    },
    async loadDetail({ commit }, id) {
      const res = await fetchStrategy(id)
      if (res.data?.success) commit('SET_CURRENT', res.data.data)
      return res.data?.data
    },
    async create({ dispatch }, data) {
      const res = await createStrategy(data)
      if (res.data?.success) await dispatch('loadList')
      return res.data
    },
    async update({ dispatch }, { id, data }) {
      const res = await updateStrategy(id, data)
      if (res.data?.success) await dispatch('loadList')
      return res.data
    },
    async remove({ dispatch }, id) {
      const res = await deleteStrategy(id)
      if (res.data?.success) await dispatch('loadList')
      return res.data
    },
    async changeStatus({ dispatch }, { id, status }) {
      await patchStrategyStatus(id, status)
      await dispatch('loadList')
    },
    async loadVersions({ commit }, strategyId) {
      const res = await fetchVersions(strategyId)
      if (res.data?.success) commit('SET_VERSIONS', res.data.data)
      return res.data?.data
    },
    async saveVersion({ dispatch }, { strategyId, sourceCode, changeLog }) {
      const res = await createVersion(strategyId, { source_code: sourceCode, change_log: changeLog })
      if (res.data?.success) {
        await dispatch('loadList')
        await dispatch('loadVersions', strategyId)
      }
      return res.data
    },
    async loadVersionCode({ commit }, { strategyId, version }) {
      const res = await fetchVersion(strategyId, version)
      if (res.data?.success) commit('SET_VERSION_CODE', res.data.data?.source_code || '')
      return res.data?.data
    }
  }
}
