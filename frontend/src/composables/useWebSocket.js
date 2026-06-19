import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

const WS_URL = process.env.VUE_APP_WS_URL || 'http://localhost:5000'

export function useBacktestSocket(backtestId) {
  const progress = ref(null)
  const connected = ref(false)
  let socket = null

  function connect() {
    if (socket) return
    socket = io(WS_URL, { transports: ['websocket'] })
    socket.on('connect', () => { connected.value = true })
    socket.on('disconnect', () => { connected.value = false })
    socket.on('backtest_progress', (data) => {
      if (data.backtest_id === backtestId) progress.value = data
    })
    socket.on('backtest_completed', (data) => {
      if (data.backtest_id === backtestId) progress.value = { ...data, completed: true }
    })
    socket.on('backtest_failed', (data) => {
      if (data.backtest_id === backtestId) progress.value = { ...data, failed: true }
    })
  }

  function disconnect() {
    if (socket) { socket.disconnect(); socket = null }
  }

  onUnmounted(disconnect)

  return { progress, connected, connect, disconnect }
}
