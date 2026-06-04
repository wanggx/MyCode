<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h2>策略工作台</h2>
        <p class="page-desc">配置策略参数、查看运行记录和版本，不做在线代码 IDE。</p>
      </div>
      <el-button type="primary" @click="handleCreate"><el-icon><Plus /></el-icon>新建策略</el-button>
    </div>
    <el-row :gutter="16" class="workspace-layout">
      <el-col :span="14">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-card class="strategy-list-card">
              <template #header><span class="card-title">策略列表</span></template>
              <div class="strategy-list">
                <div
                  v-for="s in strategies"
                  :key="s.id"
                  class="strategy-card"
                  :class="{ active: selectedId === s.id }"
                  @click="selectStrategy(s.id)"
                >
                  <div class="card-top">
                    <span class="card-name">{{ s.name }}</span>
                    <el-tag
                      :type="s.enabled ? 'success' : 'danger'"
                      size="small"
                      effect="dark"
                    >{{ s.enabled ? '运行中' : '已停止' }}</el-tag>
                  </div>
                  <div class="card-version">v{{ s.version || '1.0' }}</div>
                </div>
                <el-empty v-if="strategies.length === 0" description="暂无策略" :image-size="60" />
              </div>
            </el-card>
          </el-col>
          <el-col :span="16">
            <el-card v-if="!currentStrategy" class="placeholder-card">
              <div class="skeleton-placeholder">
                <el-icon :size="48" color="#c0c4cc"><SetUp /></el-icon>
                <p>请选择或创建一个策略</p>
              </div>
            </el-card>
            <el-card v-else class="detail-card">
              <template #header><span class="card-title">策略设置 - {{ currentStrategy.name }}</span></template>
              <el-form label-width="90px" size="default">
                <el-form-item label="策略名称">
                  <el-input v-model="form.name" placeholder="请输入策略名称" />
                </el-form-item>
                <el-form-item label="策略类型">
                  <el-select v-model="form.strategy_type" placeholder="请选择策略类型" style="width:100%">
                    <el-option label="放量突破" value="volume_breakout" />
                    <el-option label="均线趋势" value="ma_trend" />
                    <el-option label="MACD+KDJ共振" value="macd_kdj_resonance" />
                    <el-option label="港股趋势" value="hk_trend" />
                    <el-option label="自定义组合" value="custom_combo" />
                  </el-select>
                </el-form-item>
                <el-form-item label="描述">
                  <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入策略描述" />
                </el-form-item>
                <el-form-item label="启用状态">
                  <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
                </el-form-item>
                <el-divider content-position="left">交易参数</el-divider>
                <el-row :gutter="16">
                  <el-col :span="12">
                    <el-form-item label="股票池">
                      <el-select v-model="form.stock_pool" style="width:100%">
                        <el-option label="沪深A股（剔除ST）" value="hs_a_ex_st" />
                        <el-option label="港股通" value="hk_connect" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="调仓周期">
                      <el-select v-model="form.rebalance_cycle" style="width:100%">
                        <el-option label="周" value="week" />
                        <el-option label="日" value="day" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="16">
                  <el-col :span="8">
                    <el-form-item label="最大持仓">
                      <el-input-number v-model="form.max_positions" :min="1" :max="100" style="width:100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="手续费">
                      <el-input v-model="form.commission" placeholder="0.03">
                        <template #append>%</template>
                      </el-input>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="滑点">
                      <el-input v-model="form.slippage" placeholder="0.02">
                        <template #append>%</template>
                      </el-input>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="买入条件">
                      <el-input v-model="form.buy_condition" type="textarea" :rows="4" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="卖出条件">
                      <el-input v-model="form.sell_condition" type="textarea" :rows="4" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item>
                  <el-button @click="handleSaveDraft">保存草稿</el-button>
                  <el-button type="primary" @click="handleSaveAndRun">保存并运行</el-button>
                  <el-button @click="handleBacktest">回测</el-button>
                  <el-button type="danger" @click="handleDelete">删除</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-col>
      <el-col :span="10">
        <el-card class="runs-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">最近运行</span>
              <el-button type="primary" link>更多 ›</el-button>
            </div>
          </template>
          <el-table v-if="currentStrategy" :data="runs" size="small" stripe>
            <el-table-column prop="run_time" label="运行时间" min-width="140" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="runStatusType(row.status)"
                  size="small"
                  effect="dark"
                >{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="return_rate" label="收益率" width="90">
              <template #default="{ row }">
                <span :style="{ color: row.return_rate && row.return_rate.startsWith('-') ? '#0f9f6e' : row.return_rate ? '#d84a57' : '#909399' }">{{ row.return_rate || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="max_drawdown" label="最大回撤" width="90">
              <template #default="{ row }">
                <span :style="{ color: '#0f9f6e' }">{{ row.max_drawdown || '--' }}</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="请先选择策略" :image-size="60" />
        </el-card>
        <el-card class="versions-card">
          <template #header><span class="card-title">参数版本</span></template>
          <div class="version-list">
            <div
              v-for="v in versions"
              :key="v.id"
              class="version-item"
              :class="{ active: v.id === 1 }"
            >
              <div class="version-top">
                <span class="version-name">v{{ v.version }}</span>
                <span v-if="v.desc" class="version-badge">{{ v.desc }}</span>
              </div>
              <div class="version-note">{{ v.note }}</div>
              <div class="version-time">{{ v.updated_at }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { Plus, SetUp } from '@element-plus/icons-vue'
import axios from '@/config/axios'

const TYPE_MAP = {
  volume_breakout: '放量突破',
  ma_trend: '均线趋势',
  macd_kdj_resonance: 'MACD+KDJ共振',
  hk_trend: '港股趋势',
  custom_combo: '自定义组合'
}

const BUY_CONDITIONS = {
  volume_breakout: '当日成交量 > 过去20日均量 * 2.0；收盘价突破近20日最高价；成交额 > 1亿元；换手率 > 3%。',
  ma_trend: '5日均线上穿20日均线；股价站上60日均线；MACD > 0',
  macd_kdj_resonance: 'MACD在零轴上方金叉；KDJ同时金叉；成交量放大',
  hk_trend: '港股通资金持续流入；股价突破20日均线；成交量放大'
}

const SELL_CONDITIONS = {
  volume_breakout: '收盘价跌破10日均线；盈利回撤超8%；持仓超过20个交易日；触发组合风险线。',
  ma_trend: '5日均线下穿20日均线；收盘跌破60日均线；MACD < 0',
  macd_kdj_resonance: 'MACD出现顶背离；KDJ死叉；单日跌幅>5%',
  hk_trend: '股价跌破60日均线；南向资金连续3日流出；单月涨幅>30%'
}

const MOCK_STRATEGIES = [
  { id: 1, name: '放量突破', strategy_type: 'volume_breakout', description: '基于成交量异动的突破策略', enabled: true, version: '2.1' },
  { id: 2, name: '均线趋势', strategy_type: 'ma_trend', description: '多周期均线趋势跟踪', enabled: true, version: '3.4' },
  { id: 3, name: 'MACD/KDJ共振', strategy_type: 'macd_kdj_resonance', description: 'MACD与KDJ指标共振信号', enabled: true, version: '1.8' },
  { id: 4, name: '港股趋势', strategy_type: 'hk_trend', description: '港股市场趋势跟踪', enabled: false, version: '2.0' }
]

const MOCK_RUNS = {
  1: [
    { id: 101, run_time: '2026-06-04 09:10', status: '运行中', return_rate: null, max_drawdown: null },
    { id: 102, run_time: '2026-06-03 09:05', status: '完成', return_rate: '1.32%', max_drawdown: '-2.11%' },
    { id: 103, run_time: '2026-06-02 09:05', status: '完成', return_rate: '-0.43%', max_drawdown: '-2.87%' }
  ],
  2: [
    { id: 201, run_time: '2026-06-04 09:10', status: '运行中', return_rate: null, max_drawdown: null },
    { id: 202, run_time: '2026-06-03 09:05', status: '完成', return_rate: '0.85%', max_drawdown: '-1.56%' }
  ],
  3: [
    { id: 301, run_time: '2026-06-04 09:10', status: '运行中', return_rate: null, max_drawdown: null },
    { id: 302, run_time: '2026-06-03 09:05', status: '完成', return_rate: '-0.12%', max_drawdown: '-1.89%' }
  ],
  4: [
    { id: 401, run_time: '2026-06-03 09:05', status: '完成', return_rate: '2.15%', max_drawdown: '-3.42%' }
  ]
}

const MOCK_VERSIONS = [
  { id: 1, version: '2.1', desc: '当前版本', note: '优化止损保护线', updated_at: '2026-06-01 14:20' },
  { id: 2, version: '2.0', desc: '', note: '优化止损保护线', updated_at: '2026-06-01 10:00' },
  { id: 3, version: '1.0', desc: '', note: '初始版本', updated_at: '2026-05-15 09:00' }
]

export default {
  name: 'StrategyWorkspaceView',
  components: { Plus, SetUp },
  data() {
    return {
      strategies: [],
      selectedId: null,
      form: {
        name: '', strategy_type: '', description: '', enabled: false,
        stock_pool: 'hs_a_ex_st', rebalance_cycle: 'week', max_positions: 20,
        commission: '0.03', slippage: '0.02',
        buy_condition: '', sell_condition: ''
      },
      runs: [],
      versions: JSON.parse(JSON.stringify(MOCK_VERSIONS))
    }
  },
  computed: {
    currentStrategy() {
      return this.strategies.find(s => s.id === this.selectedId) || null
    }
  },
  methods: {
    strategyTypeLabel(type) {
      return TYPE_MAP[type] || type
    },
    runStatusType(status) {
      if (status === '完成' || status === '成功') return 'success'
      if (status === '失败') return 'danger'
      if (status === '超时') return 'warning'
      if (status === '运行中') return ''
      return 'info'
    },
    async fetchStrategies() {
      try {
        const res = await axios.get('/api/strategies', { params: { page: 1, page_size: 100 } })
        this.strategies = res.data?.data?.items || res.data?.items || res.data || []
      } catch {
        this.strategies = JSON.parse(JSON.stringify(MOCK_STRATEGIES))
      }
    },
    async fetchRuns(strategyId) {
      try {
        const res = await axios.get(`/api/strategies/${strategyId}/runs`, { params: { page: 1, page_size: 20 } })
        this.runs = res.data?.data?.items || res.data?.items || res.data || []
      } catch {
        this.runs = MOCK_RUNS[strategyId] ? JSON.parse(JSON.stringify(MOCK_RUNS[strategyId])) : []
      }
    },
    selectStrategy(id) {
      this.selectedId = id
      const s = this.currentStrategy
      if (s) {
        this.form = {
          name: s.name, strategy_type: s.strategy_type, description: s.description || '', enabled: s.enabled,
          stock_pool: s.stock_pool || 'hs_a_ex_st', rebalance_cycle: s.rebalance_cycle || 'week',
          max_positions: s.max_positions || 20, commission: s.commission || '0.03', slippage: s.slippage || '0.02',
          buy_condition: s.buy_condition || BUY_CONDITIONS[s.strategy_type] || '',
          sell_condition: s.sell_condition || SELL_CONDITIONS[s.strategy_type] || ''
        }
      }
      this.fetchRuns(id)
    },
    handleCreate() {
      const newId = Date.now()
      const newStrategy = {
        id: newId, name: '新策略', strategy_type: 'volume_breakout', description: '',
        enabled: false, version: '1.0'
      }
      this.strategies.unshift(newStrategy)
      this.selectStrategy(newId)
    },
    async handleSaveDraft() {
      if (!this.selectedId) return
      const id = this.selectedId
      const payload = {
        name: this.form.name, strategy_type: this.form.strategy_type,
        description: this.form.description, enabled: this.form.enabled,
        stock_pool: this.form.stock_pool, rebalance_cycle: this.form.rebalance_cycle,
        max_positions: this.form.max_positions, commission: this.form.commission,
        slippage: this.form.slippage, buy_condition: this.form.buy_condition,
        sell_condition: this.form.sell_condition
      }
      try {
        await axios.put(`/api/strategies/${id}`, payload)
        this.$message.success('草稿已保存')
      } catch {
        const idx = this.strategies.findIndex(s => s.id === id)
        if (idx !== -1) Object.assign(this.strategies[idx], payload)
        this.$message.success('草稿已保存（本地）')
      }
    },
    async handleSaveAndRun() {
      await this.handleSaveDraft()
      await this.triggerRun(this.selectedId)
    },
    handleBacktest() {
      this.$message.info('回测功能开发中')
    },
    async handleDelete() {
      if (!this.selectedId) return
      const id = this.selectedId
      try {
        await this.$confirm('确认删除该策略？', '提示', { type: 'warning' })
        try {
          await axios.delete(`/api/strategies/${id}`)
        } catch { /* fallback: remove locally */ }
        this.strategies = this.strategies.filter(s => s.id !== id)
        this.selectedId = null
        this.form = {
          name: '', strategy_type: '', description: '', enabled: false,
          stock_pool: 'hs_a_ex_st', rebalance_cycle: 'week', max_positions: 20,
          commission: '0.03', slippage: '0.02', buy_condition: '', sell_condition: ''
        }
        this.runs = []
        this.$message.success('已删除')
      } catch { /* cancelled */ }
    },
    async triggerRun(strategyId) {
      try {
        await axios.post(`/api/strategies/${strategyId}/run`)
        this.$message.success('策略已触发运行')
        this.fetchRuns(strategyId)
      } catch {
        const now = new Date()
        const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
        this.runs.unshift({ id: Date.now(), run_time: timeStr, status: '运行中', return_rate: null, max_drawdown: null })
        this.$message.success('策略已触发运行（模拟）')
      }
    }
  },
  mounted() {
    this.fetchStrategies()
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.workspace-layout { margin-top: 0; }
.strategy-list-card { height: 100%; }
.strategy-list { max-height: 360px; overflow-y: auto; }
.strategy-card {
  padding: 12px 14px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}
.strategy-card:hover { border-color: #007f7a; }
.strategy-card.active { border-color: #007f7a; background: #e6f7f6; }
.card-top { display: flex; align-items: center; justify-content: space-between; }
.card-name { font-weight: 600; font-size: 14px; color: #303133; }
.card-version { margin-top: 4px; font-size: 12px; color: #909399; }
.placeholder-card { min-height: 300px; }
.skeleton-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; color: #c0c4cc; }
.skeleton-placeholder p { margin: 12px 0 4px; font-size: 16px; color: #909399; }
.card-title { font-weight: 600; font-size: 15px; }
.detail-card :deep(.el-card__body) { padding-bottom: 0; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.runs-card { margin-bottom: 16px; }
.versions-card { }
.version-list { max-height: 240px; overflow-y: auto; }
.version-item {
  padding: 10px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s;
}
.version-item.active { border-color: #007f7a; background: #e6f7f6; }
.version-top { display: flex; align-items: center; gap: 8px; }
.version-name { font-weight: 600; font-size: 14px; color: #303133; }
.version-badge {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: #007f7a;
  color: #fff;
}
.version-note { margin-top: 4px; font-size: 13px; color: #606266; }
.version-time { margin-top: 2px; font-size: 12px; color: #c0c4cc; }
</style>
