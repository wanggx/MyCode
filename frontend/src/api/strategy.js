import axios from '@/config/axios'

export function fetchStrategies(params = {}) {
  return axios.get('/api/strategies', { params })
}

export function fetchStrategy(id) {
  return axios.get(`/api/strategies/${id}`)
}

export function createStrategy(data) {
  return axios.post('/api/strategies', data)
}

export function updateStrategy(id, data) {
  return axios.put(`/api/strategies/${id}`, data)
}

export function patchStrategyStatus(id, status) {
  return axios.patch(`/api/strategies/${id}/status`, { status })
}

export function deleteStrategy(id) {
  return axios.delete(`/api/strategies/${id}`)
}

export function fetchVersions(strategyId) {
  return axios.get(`/api/strategies/${strategyId}/versions`)
}

export function createVersion(strategyId, data) {
  return axios.post(`/api/strategies/${strategyId}/versions`, data)
}

export function fetchVersion(strategyId, version) {
  return axios.get(`/api/strategies/${strategyId}/versions/${version}`)
}
