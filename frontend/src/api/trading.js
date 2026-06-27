import axios from '@/config/axios'

// 大盘指数
export function getMarketIndices() {
  return axios.get('/api/market/indices')
}

// 策略运行列表（支持 mode 过滤：paper / live）
export function getLiveRuns(page = 1, pageSize = 20, mode = null) {
  const params = { page, page_size: pageSize }
  if (mode) params.mode = mode
  return axios.get('/api/trading/live-runs', { params })
}

// 单个实盘运行详情
export function getLiveRunDetail(runId) {
  return axios.get(`/api/trading/live-runs/${runId}`)
}

// 实盘交易记录
export function getLiveRunTrades(runId, page = 1, pageSize = 20) {
  return axios.get(`/api/trading/live-runs/${runId}/trades`, { params: { page, page_size: pageSize } })
}

// 当前持仓
export function getLiveRunPositions(runId) {
  return axios.get(`/api/trading/live-runs/${runId}/positions`)
}

// 运行日志
export function getLiveRunLogs(runId, page = 1, pageSize = 50) {
  return axios.get(`/api/trading/live-runs/${runId}/logs`, { params: { page, page_size: pageSize } })
}

// 风控指标
export function getLiveRunMetrics(runId) {
  return axios.get(`/api/trading/live-runs/${runId}/metrics`)
}

// 交易信号
export function getTradingSignals(page = 1, pageSize = 20) {
  return axios.get('/api/trading/signals', { params: { page, page_size: pageSize } })
}

// 风控概览
export function getRiskOverview() {
  return axios.get('/api/trading/risk-overview')
}

// ===== 模拟盘管理 =====
export function createPaperRun(strategyId, initialCapital = 100000, autoStart = true) {
  return axios.post('/api/trading/paper-runs', {
    strategy_id: strategyId, initial_capital: initialCapital, auto_start: autoStart,
  })
}
export function startPaperRun(runId) {
  return axios.post(`/api/trading/paper-runs/${runId}/start`)
}
export function stopPaperRun(runId) {
  return axios.post(`/api/trading/paper-runs/${runId}/stop`)
}
export function deletePaperRun(runId) {
  return axios.delete(`/api/trading/paper-runs/${runId}`)
}
export function promotePaperRun(runId, broker, capital) {
  return axios.post(`/api/trading/paper-runs/${runId}/promote`, { broker, capital })
}
