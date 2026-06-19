import axios from '@/config/axios'

export function fetchBacktests(params = {}) {
  return axios.get('/api/backtests', { params })
}

export function fetchBacktest(id) {
  return axios.get(`/api/backtests/${id}`)
}

export function createBacktest(data) {
  return axios.post('/api/backtests', data)
}

export function cancelBacktest(id) {
  return axios.post(`/api/backtests/${id}/cancel`)
}

export function deleteBacktest(id) {
  return axios.delete(`/api/backtests/${id}`)
}

export function fetchNav(id, params = {}) {
  return axios.get(`/api/backtests/${id}/nav`, { params })
}

export function fetchTrades(id, params = {}) {
  return axios.get(`/api/backtests/${id}/trades`, { params })
}

export function fetchPositions(id, params = {}) {
  return axios.get(`/api/backtests/${id}/positions`, { params })
}

export function fetchRiskMetrics(id) {
  return axios.get(`/api/backtests/${id}/risk-metrics`)
}

export function fetchLogs(id, params = {}) {
  return axios.get(`/api/backtests/${id}/logs`, { params })
}

export function fetchReport(id) {
  return axios.get(`/api/backtests/${id}/report`)
}
