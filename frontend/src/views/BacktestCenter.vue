<template>
  <div class="bt-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <div class="panel-header"><span>回测列表</span><div style="display:flex;gap:6px;"><el-button size="small" @click="loadListData" :icon="Refresh">🔄</el-button><el-button type="primary" size="small" @click="showCreateDialog">+ 新建回测</el-button></div></div>
      <el-select v-model="statusFilter" placeholder="状态筛选" size="small" clearable class="bt-filter" @change="onFilterChange">
        <el-option label="全部" value="" /><el-option label="运行中" value="running" /><el-option label="已完成" value="completed" /><el-option label="失败" value="failed" />
      </el-select>
      <el-tag
        v-if="strategyFilterName"
        closable size="small" type="info" class="bt-filter-tag"
        @close="clearStrategyFilter"
      >📝 {{ strategyFilterName }}</el-tag>
      <div class="bt-list">
        <div v-for="bt in backtests" :key="bt.id" class="bt-item" :class="{ active: selected?.id === bt.id }" @click="selectBacktest(bt)">
          <div class="item-title">
            <span>{{ statusIcon(bt.status) }}</span>
            <span class="item-name">{{ bt.strategy_name || 'BT#'+bt.id }}</span>
            <el-tag v-if="bt.strategy_version" size="small" :type="bt.status==='completed'?'success':bt.status==='running'?'warning':'info'" class="item-version">v{{ bt.strategy_version }}</el-tag>
          </div>
          <div class="item-meta">{{ bt.created_at?.slice(0,19) }}<template v-if="bt.duration_ms"> · {{ (bt.duration_ms/1000).toFixed(1) }}秒</template></div>
          <div class="item-stats" v-if="bt.status==='completed'">
            <span :class="(bt.total_return??0)>0?'green':'red'">{{ ((bt.total_return??0)*100).toFixed(1)+'%' }}</span>
            <span class="stat-div">·</span>
            <span>夏普 {{ (bt.sharpe_ratio??0).toFixed(2) }}</span>
            <span class="stat-div">·</span>
            <span class="red">{{ ((bt.max_drawdown??0)*100).toFixed(1)+'%' }}</span>
          </div>
          <div class="item-stats" v-else-if="bt.status==='running'">
            <span class="blue">{{ bt.progress?.toFixed(0) || 0 }}%</span>
          </div>
        </div>
        <el-empty v-if="backtests.length===0" description="暂无回测记录" :image-size="60" />
      </div>
      <el-pagination
        v-if="total > 0"
        small layout="total, sizes, prev, pager, next"
        :total="total" :page-sizes="[5,10,20]" :page-size="btPageSize" :current-page="btPage"
        @size-change="onBtSizeChange" @current-change="onBtPageChange"
        style="padding:8px;justify-content:center;display:flex;flex-shrink:0;border-top:1px solid #eee"
      />
    </div>

    <!-- Right Panel -->
    <div class="right-panel" v-if="selected">
      <!-- Progress Bar (visible during running) -->
      <div class="run-bar" v-if="selected.status==='running'">
        <div class="run-bar-left">
          <div class="run-track"><div class="run-fill" :style="{width:(selected.progress||0)+'%'}"></div></div>
          <div class="run-text">
            <span>{{ selected.progress?.toFixed(0) || 0 }}%</span><span>·</span>
            <span>{{ selected.current_date || '运行中...' }}</span><span>·</span>
            <span>{{ selected.config?.start_date }} ~ {{ selected.config?.end_date }}</span>
          </div>
        </div>
        <el-button type="danger" size="small" @click="handleCancel">取消</el-button>
      </div>

      <!-- Summary Card -->
      <div class="summary-card">
        <div class="summary-row">
          <div>
            <span class="summary-title">{{ selected.strategy_name || '回测 #'+selected.id }}</span>
            <el-tag :type="selected.status==='completed'?'success':selected.status==='running'?'warning':selected.status==='failed'?'danger':'info'" size="small" style="margin-left:8px">{{ statusText(selected.status) }}</el-tag>
            <el-tooltip v-if="selected.status==='failed' && selected.error_message" effect="dark" :content="selected.error_message" placement="bottom-start" raw-content>
              <span class="error-help-icon">❓</span>
            </el-tooltip>
          </div>
          <div class="summary-actions">
            <el-switch v-model="debugEnabled" active-text="Debug" inline-prompt size="small" style="--el-switch-on-color:#6f42c1;margin-right:8px;" />
            <el-button v-if="selected.status==='completed' || selected.status==='failed'" size="small" type="primary" @click="handleRerun">🔄 重新运行</el-button>
            <el-button v-if="selected.status==='completed'" size="small" @click="handleExport">📥 导出报告</el-button>
            <el-button v-if="selected.status!=='running'" size="small" type="danger" @click="handleDelete">🗑 删除</el-button>
          </div>
        </div>
        <div class="summary-meta">
          回测区间: {{ selected.config?.start_date || '-' }} ~ {{ selected.config?.end_date || '-' }}
          <span class="sep">·</span> 初始资金: ¥{{ (selected.config?.initial_capital || 100000).toLocaleString() }}
          <span class="sep">·</span> 基准: {{ selected.config?.benchmark || '沪深300' }}
          <span v-if="selected.duration_ms" class="sep">·</span> 耗时: {{ (selected.duration_ms/1000).toFixed(1) }}s
        </div>
      </div>

      <!-- Metrics Grid (12 items, always visible) -->
      <div class="metrics">
        <div class="m-item" v-for="m in metricItems" :key="m.label">
          <div class="m-val" :class="m.cls">{{ m.val }}</div>
          <div class="m-label">{{ m.label }}</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tab-bar">
        <div v-for="t in tabs" :key="t.key" class="tab-item" :class="{ active: activeTab===t.key }" @click="switchTab(t.key)">{{ t.icon }} {{ t.label }}</div>
      </div>
      <div class="tab-content">
        <div v-show="activeTab==='nav'" ref="navChart" class="chart-box"></div>
        <div v-show="activeTab==='trades'">
          <div class="tab-header">共 {{ trades?.total || 0 }} 笔交易</div>
          <el-table :data="trades?.items||[]" size="small" max-height="320" stripe style="width:100%">
            <el-table-column prop="ts_code" label="股票" min-width="100" />
            <el-table-column prop="buy_date" label="操作时间" min-width="150" />
            <el-table-column prop="sell_reason" label="方向" width="60" />
            <el-table-column prop="order_type" label="订单类型" width="75" />
            <el-table-column prop="buy_price" label="价格" min-width="80" />
            <el-table-column prop="quantity" label="数量" min-width="80" />
          </el-table>
          <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0">
            <el-button size="small" @click="exportTrades">📥 导出交易记录</el-button>
            <el-pagination
              v-if="trades?.total > 0"
              small layout="total, sizes, prev, pager, next" :page-sizes="[5,10,20,100]"
              :total="trades?.total||0" :page-size="tradePageSize" :current-page="tradePage"
              @size-change="onTradeSizeChange" @current-change="onTradePageChange"
            />
          </div>
        </div>
        <div v-show="activeTab==='positions'" class="row-2">
          <div ref="pieChart" class="chart-sm"></div>
          <div ref="indChart" class="chart-sm"></div>
        </div>
        <div v-show="activeTab==='risk'">
          <div ref="ddChart" class="chart-box" style="height:260px"></div>
          <el-table :data="riskTable" size="small" class="mt-8" stripe>
            <el-table-column prop="k" label="指标" width="180" /><el-table-column prop="v" label="值" />
          </el-table>
        </div>
        <div v-show="activeTab==='distribution'" class="row-2">
          <div ref="histChart" class="chart-sm"></div>
          <div ref="heatChart" class="chart-sm"></div>
        </div>
        <div v-show="activeTab==='logs'" class="log-panel">
          <div class="log-header">
            <span class="log-path">📄 logs/{{ selected.strategy_key || 'unknown' }}/{{ selected.id }}.log</span>
            <el-button size="small" @click="copyLogs">📥 下载</el-button>
          </div>
          <pre class="log-body">{{ logs?.lines?.join('') || '暂无日志' }}</pre>
        </div>
        <div v-show="activeTab==='code'" class="code-panel">
          <div class="code-header">
            <span class="code-title">💻 {{ selected.strategy_name || '策略' }} v{{ selected.strategy_version }}</span>
            <el-button size="small" @click="copyCode">📋 复制代码</el-button>
          </div>
          <pre class="code-body" v-text="sourceCode || '加载中...'"></pre>
        </div>
      </div>
    </div>
    <div class="right-panel empty" v-else><el-empty description="选择一个回测查看详情" /></div>

    <!-- New Backtest Dialog -->
    <el-dialog v-model="newBtVisible" title="⚡ 新建回测" width="540px">
      <div class="bt-strategy-banner">
        <div class="st-icon">📝</div>
        <div class="st-info">
          <div class="st-name">{{ currentStrategy?.name || selected?.strategy_name }} <el-tag size="small" type="success">v{{ currentStrategy?.latest_version || selected?.strategy_version }}</el-tag></div>
          <div class="st-meta">股票策略 · 选择回测参数</div>
        </div>
      </div>
      <el-form :model="btForm" label-width="80px" style="margin-top:16px">
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="起始日期"><el-date-picker v-model="btForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col><el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="btForm.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col></el-row>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="起始资金"><el-input-number v-model="btForm.initial_capital" :min="10000" :step="10000" style="width:100%" /></el-form-item></el-col><el-col :span="12"><el-form-item label="基准"><el-select v-model="btForm.benchmark" style="width:100%"><el-option label="无" value="" /><el-option label="沪深300" value="000300.XSHG" /><el-option label="中证500" value="000905.XSHG" /></el-select></el-form-item></el-col></el-row>
        <el-row :gutter="12"><el-col :span="12"><el-form-item label="频率"><el-select v-model="btForm.frequency" style="width:100%"><el-option label="日线" value="1d" /><el-option label="分钟" value="1m" /></el-select></el-form-item></el-col><el-col :span="12"><el-form-item label="手续费"><el-input-number v-model="btForm.commission" :min="0" :step="0.0001" :precision="4" style="width:100%" /></el-form-item></el-col></el-row>
      </el-form>
      <template #footer><el-button @click="newBtVisible=false">取消</el-button><el-button type="primary" @click="runBacktest">⚡ 开始回测</el-button></template>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { mapState, mapActions } from 'vuex'
import axios from '@/config/axios'
import { fetchSource } from '@/api/backtest'

export default {
  name: 'BacktestCenter',
  data() {
    return {
      statusFilter: '', selected: null, activeTab: 'nav',
      debugEnabled: false, strategyFilterName: '',
      btPage: 1, btPageSize: 20,
      tradePage: 1, tradePageSize: 20,
      trades: null, positions: null, risk: null, logs: null,
      navData: null, sourceCode: null,
      newBtVisible: false, currentStrategy: null,
      btForm: { start_date:'2024-01-01', end_date:'2024-12-31', initial_capital:100000, benchmark:'', frequency:'1d', commission:0.0003 },
      tabs: [
        { key:'nav', icon:'📊', label:'净值曲线' },
        { key:'trades', icon:'📋', label:'交易记录' },
        { key:'positions', icon:'📈', label:'持仓分析' },
        { key:'risk', icon:'📉', label:'风险分析' },
        { key:'distribution', icon:'📊', label:'收益分布' },
        { key:'logs', icon:'📝', label:'日志' },
        { key:'code', icon:'💻', label:'代码' }
      ]
    }
  },
  computed: {
    ...mapState('backtest', ['list', 'total']),
    backtests() { return this.list },
    metricItems() {
      const s = this.selected
      if (!s) return []
      const tr = s.total_return ?? 0
      return [
        { label:'总收益率', val: (tr*100).toFixed(2)+'%', cls: tr>0?'green':tr<0?'red':'' },
        { label:'年化收益率', val: ((s.annualized_return??0)*100).toFixed(2)+'%', cls: (s.annualized_return??0)>0?'green':'' },
        { label:'最大回撤', val: ((s.max_drawdown??0)*100).toFixed(2)+'%', cls: 'red' },
        { label:'夏普比率', val: (s.sharpe_ratio??0).toFixed(2) },
        { label:'索提诺比率', val: (s.sortino_ratio??0).toFixed(2) },
        { label:'胜率', val: ((s.win_rate??0)*100).toFixed(1)+'%' },
        { label:'盈亏比', val: (s.profit_loss_ratio??0).toFixed(2) },
        { label:'年化波动率', val: ((s.annual_volatility??0)*100).toFixed(1)+'%' },
        { label:'Alpha', val: ((s.alpha??0)*100).toFixed(1)+'%' },
        { label:'Beta', val: (s.beta??0).toFixed(2) },
        { label:'最终资产', val: '¥'+(s.final_value??0).toLocaleString() },
        { label:'总交易笔数', val: s.total_trades || 0 }
      ]
    },
    riskTable() {
      if (!this.risk) return []
      return Object.entries(this.risk).filter(([k])=>!k.startsWith('_')&&!k.endsWith('_start')&&!k.endsWith('_end')&&!k.endsWith('_recovery')&&!k.endsWith('_days')).map(([k,v])=>({k,v:v!=null?(typeof v==='number'?v.toFixed(4):v):'0'}))
    }
  },
  methods: {
    ...mapActions('backtest', ['loadList','loadDetail','cancel','loadTrades','loadPositions','loadRiskMetrics','loadLogs','loadNav']),
    statusIcon(s) { return s==='completed'?'✅':s==='running'?'⚡':s==='failed'?'❌':s==='cancelled'?'🚫':'⏳' },
    statusText(s) { return s==='completed'?'已完成':s==='running'?'运行中':s==='failed'?'失败':s==='cancelled'?'已取消':'等待中' },
    safeNum(v) { return (v != null && isFinite(v)) ? Number(v) : 0 },
    async loadListData() {
      const strategyId = this.$route.query.strategy_id ? Number(this.$route.query.strategy_id) : null
      await this.loadList({ status: this.statusFilter || undefined, strategy_id: strategyId || undefined, page: this.btPage, page_size: this.btPageSize })
      if (strategyId) {
        this.strategyFilterName = this.backtests[0]?.strategy_name || this.strategyFilterName || `策略 #${strategyId}`
      } else {
        this.strategyFilterName = ''
      }
      if (this.backtests.length > 0 && !this.selected) {
        this.selectBacktest(this.backtests[0])
      }
    },
    async selectBacktest(bt) {
      // Parse config if it's a string (from DB)
      if (bt.config && typeof bt.config === 'string') {
        try { bt.config = JSON.parse(bt.config) } catch(e) { bt.config = {} }
      }
      this.selected = bt; this.activeTab = 'nav'; this.tradePage = 1; this.trades = null; this.risk = null; this.logs = null; this.navData = null; this.sourceCode = null
      // Read debug flag from config (per-backtest-instance)
      this.debugEnabled = !!(bt.config && bt.config.debug)

      // Always refresh detail from server (gets latest error_message, metrics, etc.)
      try {
        const detail = await this.loadDetail(bt.id)
        if (detail) {
          if (detail.config && typeof detail.config === 'string') {
            try { detail.config = JSON.parse(detail.config) } catch { /* ignore parse error */ }
          }
          this.selected = detail
        }
      } catch(e) { console.error('loadDetail failed:', e) }

      // Load logs for ALL statuses (useful for debugging) — pass debug flag
      try {
        this.logs = await this.loadLogs({ id: bt.id, debug: this.debugEnabled })
      } catch(e) { console.error('loadLogs failed:', e) }

      // Load detail data for completed/failed backtests
      if (bt.status === 'completed' || bt.status === 'failed') {
        try {
          const [nav, trades, risk] = await Promise.all([
            this.loadNav(bt.id),
            this.loadTrades({ id: bt.id, page: this.tradePage, pageSize: this.tradePageSize }),
            this.loadRiskMetrics(bt.id)
          ])
          this.trades = trades; this.risk = risk; this.navData = nav
          this.$nextTick(() => { this.renderAllCharts() })
        } catch(e) { console.error('loadDetailData failed:', e) }
      }
      if (bt.status === 'running') {
        try { this.navData = await this.loadNav(bt.id) } catch { /* ignore */ }
        this.startPolling(bt.id)
      }
    },
    switchTab(key) {
      this.activeTab = key
      this.$nextTick(() => { this.renderAllCharts() })
      // Reload NAV when switching to nav tab (especially for running backtests)
      if (key === 'nav' && this.selected) {
        this.loadNav(this.selected.id).then(nav => {
          if (nav) { this.navData = nav; this.$nextTick(() => this.renderNavChart()) }
        }).catch(() => {})
      }
      // Trigger trades API on tab switch
      if (key === 'trades' && this.selected) {
        this.reloadTrades()
      }
      // Lazy-load logs when switching to logs tab
      if (key === 'logs' && !this.logs && this.selected) {
        this.loadLogs(this.selected.id).then(logs => { this.logs = logs }).catch(() => {})
      }
      // Lazy-load source code when switching to code tab
      if (key === 'code' && !this.sourceCode && this.selected) {
        fetchSource(this.selected.id).then(res => {
          if (res.data?.success) this.sourceCode = res.data.data?.source_code
        }).catch(() => {})
      }
    },
    renderAllCharts() {
      if (this.activeTab==='nav' && this.navData) this.renderNavChart()
      if (this.activeTab==='positions') { this.renderPieChart(); this.renderIndustryChart() }
      if (this.activeTab==='risk') this.renderDrawdownChart()
      if (this.activeTab==='distribution') { this.renderHistChart(); this.renderHeatmapChart() }
    },
    renderNavChart() {
      const el = this.$refs.navChart; if (!el) return
      const chart = echarts.init(el)
      const d = this.navData; const dates = d?.dates || []; const nav = d?.nav || []; const bench = d?.benchmark_nav || []
      chart.setOption({
        tooltip:{trigger:'axis'}, legend:{data:['策略收益','基准收益','超额收益'],top:5},
        grid:{left:50,right:20,top:40,bottom:50},
        xAxis:{type:'category',data:dates,axisLabel:{interval:Math.max(1,Math.floor(dates.length/6)),formatter:v=>v?.slice(5)}},
        yAxis:{type:'value',axisLabel:{formatter:'{value}%'}},
        dataZoom:[{type:'slider',bottom:10},{type:'inside'}],
        series:[
          {name:'策略收益',type:'line',data:nav.map(v=>((v-1)*100).toFixed(2)),smooth:true,lineStyle:{color:'#1890ff',width:2},areaStyle:{color:'rgba(24,144,255,.15)'},symbol:'none'},
          {name:'基准收益',type:'line',data:bench.map(v=>((v-1)*100).toFixed(2)),smooth:true,lineStyle:{color:'#faad14',width:2,type:'dashed'},symbol:'none'},
          {name:'超额收益',type:'line',data:nav.map((v,i)=>((v-(bench[i]||v))*100).toFixed(2)),smooth:true,lineStyle:{color:'#52c41a',width:1,opacity:.6},symbol:'none'}
        ]
      }); chart.resize()
    },
    renderPieChart() {
      const el = this.$refs.pieChart; if (!el) return
      const chart = echarts.init(el)
      const posData = this.positions || []
      const pieData = posData.slice(0,10).map(p=>({name:p.ts_code||p.symbol,value:Math.abs(p.market_value||p.weight||0)}))
      chart.setOption({title:{text:'持仓集中度',left:'center',textStyle:{fontSize:13}},series:[{type:'pie',radius:['40%','70%'],center:['50%','55%'],data:pieData.length?pieData:[{name:'无数据',value:1}],label:{formatter:'{b}\n{d}%'}}]}); chart.resize()
    },
    renderIndustryChart() {
      const el = this.$refs.indChart; if (!el) return
      const chart = echarts.init(el)
      chart.setOption({title:{text:'行业分布',left:'center',textStyle:{fontSize:13}},xAxis:{type:'category',data:['银行','科技','消费','医药','其他']},yAxis:{type:'value'},series:[{type:'bar',data:[45,25,15,10,5],itemStyle:{color:'#1890ff'},barWidth:'50%'}]}); chart.resize()
    },
    renderDrawdownChart() {
      const el = this.$refs.ddChart; if (!el) return
      const chart = echarts.init(el)
      const dates = this.navData?.dates || []
      const nav = this.navData?.nav || []
      const ddData = []; let peak = nav[0]||1
      for (let i=0;i<nav.length;i++) { if(nav[i]>peak) peak=nav[i]; ddData.push(((nav[i]-peak)/peak*100).toFixed(2)) }
      chart.setOption({
        tooltip:{trigger:'axis'},grid:{left:50,right:20,top:10,bottom:50},
        xAxis:{type:'category',data:dates,axisLabel:{interval:Math.max(1,Math.floor(dates.length/6)),formatter:v=>v?.slice(5)}},
        yAxis:{type:'value',axisLabel:{formatter:'{value}%'},max:0},
        dataZoom:[{type:'slider',bottom:10}],
        series:[{type:'line',data:ddData,smooth:true,symbol:'none',lineStyle:{color:'#ff4d4f',width:1.5},areaStyle:{color:'rgba(255,77,79,.2)'}}]
      }); chart.resize()
    },
    renderHistChart() {
      const el = this.$refs.histChart; if (!el) return
      const chart = echarts.init(el)
      const bins = ['-6%','-4%','-3%','-2%','-1%','0%','+1%','+2%','+3%','+4%','+6%']
      const counts = bins.map(()=>Math.floor(Math.random()*15+3))
      chart.setOption({title:{text:'日收益分布',left:'center',textStyle:{fontSize:13}},xAxis:{type:'category',data:bins},yAxis:{type:'value'},series:[{type:'bar',data:counts,itemStyle:{color:p=>parseFloat(p.name)<0?'#ff4d4f':'#52c41a'},barWidth:'80%'}]}); chart.resize()
    },
    renderHeatmapChart() {
      const el = this.$refs.heatChart; if (!el) return
      const chart = echarts.init(el)
      const months = ['01','02','03','04','05','06','07','08','09','10','11','12']
      const data = []; for(let m=0;m<12;m++) for(let w=0;w<5;w++) data.push([w,m,((Math.random()-.45)*8).toFixed(2)])
      chart.setOption({
        title:{text:'周收益热力图',left:'center',textStyle:{fontSize:13}},
        tooltip:{formatter:p=>'W'+(p.data[0]+1)+' M'+months[p.data[1]]+'<br/>收益: '+p.data[2]+'%'},
        xAxis:{type:'category',data:['W1','W2','W3','W4','W5']},yAxis:{type:'category',data:months},
        visualMap:{min:-4,max:4,calculable:true,orient:'vertical',left:'right',top:'center',inRange:{color:['#ff4d4f','#fff','#52c41a']}},
        series:[{type:'heatmap',data,label:{show:false}}]
      }); chart.resize()
    },
    startPolling(btId) {
      this._pollTimer = setInterval(async () => {
        try {
          const r = await axios.get(`/api/backtests/${btId}`)
          if (r.data?.success) {
            const bt = r.data.data
            if (bt.config && typeof bt.config === 'string') { try { bt.config = JSON.parse(bt.config) } catch(e) { bt.config = {} } }
            this.selected = bt
            // 动态加载净值曲线
            try {
              this.navData = await this.loadNav(btId)
              if (this.activeTab === 'nav') this.$nextTick(() => this.renderNavChart())
            } catch { /* ignore */ }
            if (bt.status !== 'running') { clearInterval(this._pollTimer); this.selectBacktest(bt) }
          }
        } catch { clearInterval(this._pollTimer) }
      }, 2000)
    },
    async handleCancel() { if (this.selected) { await this.cancel(this.selected.id); clearInterval(this._pollTimer); this.$message.info('已取消'); this.loadListData() } },
    async handleRerun() {
      if (!this.selected) return
      const s = this.selected
      try {
        // 复用原配置，创建一条新回测记录（携带当前 debug 开关状态）
        const cfg = { ...(s.config || {}), _backtest_id: undefined, debug: this.debugEnabled }
        const res = await this.$store.dispatch('backtest/create', {
          strategy_id: s.strategy_id,
          version: s.strategy_version,
          config: cfg
        })
        if (res?.success) {
          this.$message.success('回测已创建')
          this.loadListData()
        } else {
          this.$message.error(res?.message || res?.error || '重新运行失败')
        }
      } catch (e) {
        this.$message.error(e.response?.data?.message || e.response?.data?.error || e.message || '重新运行失败')
      }
    },
    handleExport() { this.$message.success('报告已导出（功能开发中）') },
    async handleDelete() {
      if (!this.selected) return
      try {
        await this.$confirm('确认删除该回测及所有关联数据？', '警告', { type:'warning' })
        await axios.delete(`/api/backtests/${this.selected.id}`)
        this.selected = null; this.$message.success('已删除'); this.loadListData()
      } catch { /* cancelled */ }
    },
    showCreateDialog() {
      // Use selected backtest's strategy as default
      if (this.selected?.strategy_id) {
        this.currentStrategy = { name: this.selected.strategy_name, latest_version: this.selected.strategy_version }
      }
      this.newBtVisible = true
    },
    async runBacktest() {
      const sid = this.selected?.strategy_id
      if (!sid) { this.$message.warning('请先选择一个回测或策略'); return }
      try {
        const res = await this.$store.dispatch('backtest/create', { strategy_id: sid, version: this.selected.strategy_version, config: this.btForm })
        if (res?.success) { this.newBtVisible = false; this.$message.success('回测已创建'); this.loadListData() }
        else { this.$message.error(res?.message || '创建失败') }
      } catch(e) { this.$message.error(e.response?.data?.message || e.response?.data?.error || '创建失败') }
    },
    copyLogs() {
      if (this.logs?.lines) { const text = this.logs.lines.join(''); navigator.clipboard?.writeText(text); this.$message.success('日志已复制') }
    },
    copyCode() {
      if (this.sourceCode) { navigator.clipboard?.writeText(this.sourceCode); this.$message.success('代码已复制') }
    },
    onFilterChange() { this.btPage = 1; this.loadListData() },
    onBtSizeChange(s) { this.btPageSize = s; this.btPage = 1; this.loadListData() },
    onBtPageChange(p) { this.btPage = p; this.loadListData() },
    async onTradeSizeChange(s) { this.tradePageSize = s; this.tradePage = 1; await this.reloadTrades() },
    async onTradePageChange(p) { this.tradePage = p; await this.reloadTrades() },
    async reloadTrades() {
      if (!this.selected) return
      try {
        const trades = await this.loadTrades({ id: this.selected.id, page: this.tradePage, pageSize: this.tradePageSize })
        if (trades) this.trades = trades
      } catch { /* ignore */ }
    },
    exportTrades() {
      if (!this.trades?.items?.length) return this.$message.warning('无交易记录')
      const rows = this.trades.items
      const csv = ['股票,操作时间,方向,价格,数量']
      rows.forEach(r => {
        csv.push([r.ts_code||'', r.buy_date||'', r.sell_reason||'', r.buy_price||'', r.quantity||''].join(','))
      })
      const blob = new Blob(['﻿' + csv.join('\n')], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url; a.download = `trades_${this.selected?.id || 'export'}.csv`
      a.click(); URL.revokeObjectURL(url); this.$message.success('已导出')
    },
    clearStrategyFilter() {
      this.strategyFilterName = ''
      this.btPage = 1
      this.$router.replace({ query: {} })
      this.loadListData()
    },
  },
  watch: {
    async debugEnabled(v) {
      if (!this.selected) return
      // 切换 Debug 开关时重新加载日志
      try { this.logs = await this.loadLogs({ id: this.selected.id, debug: v }) } catch(e) { console.error(e) }
    },
  },
  mounted() { this.loadListData() },
  beforeUnmount() { clearInterval(this._pollTimer) }
}
</script>

<style scoped>
.bt-page { display: flex; height: calc(100vh - 96px); gap: 16px; }
.left-panel { width: 340px; flex-shrink: 0; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); display: flex; flex-direction: column; overflow: visible; }
.panel-header { padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; font-weight: 600; font-size: 14px; flex-shrink: 0; }
.bt-filter { margin: 8px 12px; flex-shrink: 0; }
.bt-filter-tag { margin: 0 12px 8px; flex-shrink: 0; }
.bt-list { flex: 1; overflow-y: auto; min-height: 0; }
.bt-list .el-pagination { flex-shrink: 0; }
.bt-item { padding: 12px 16px; border-bottom: 1px solid #f5f5f5; cursor: pointer; transition: background .2s; text-align: left; }
.bt-item:hover { background: #fafafa; }
.bt-item.active { background: #e6f7ff; border-left: 3px solid #1890ff; padding-left: 13px; }
.item-title { display: flex; align-items: center; gap: 6px; font-weight: 500; font-size: 14px; }
.item-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.item-version { margin-left: auto; flex-shrink: 0; }
.item-meta { font-size: 12px; color: #999; margin-top: 4px; }
.item-stats { margin-top: 4px; font-size: 13px; display: flex; gap: 6px; }
.stat-div { color: #ddd; }
.green { color: #52c41a; font-weight: 600; } .red { color: #ff4d4f; font-weight: 600; } .blue { color: #1890ff; font-weight: 600; }

.right-panel { flex: 1; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); display: flex; flex-direction: column; overflow: hidden; }
.right-panel.empty { align-items: center; justify-content: center; }

.run-bar { display: flex; align-items: center; gap: 12px; padding: 12px 20px; background: linear-gradient(135deg, #e6f7ff, #f0f5ff); border-bottom: 2px solid #91d5ff; flex-shrink: 0; }
.run-bar-left { flex: 1; }
.run-track { background: #e8e8e8; border-radius: 6px; height: 8px; overflow: hidden; }
.run-fill { height: 100%; background: linear-gradient(90deg,#1890ff,#6f42c1); border-radius: 6px; transition: width .3s; }
.run-text { font-size: 12px; color: #666; margin-top: 4px; display: flex; gap: 6px; }

.summary-card { padding: 14px 20px; border-bottom: 1px solid #eee; }
.summary-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.summary-title { font-size: 15px; font-weight: 600; }
.summary-meta { font-size: 12px; color: #999; }
.summary-meta .sep { margin: 0 4px; color: #ddd; }
.summary-actions { display: flex; gap: 6px; }
.summary-error { margin-top: 8px; padding: 6px 12px; background: #fff2f0; border: 1px solid #ffccc7; border-radius: 4px; font-size: 12px; color: #ff4d4f; }
.error-help-icon { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; background: #ffccc7; color: #ff4d4f; font-size: 12px; cursor: help; margin-left: 6px; transition: all .2s; flex-shrink: 0; }
.error-help-icon:hover { background: #ff4d4f; color: #fff; transform: scale(1.1); }

.metrics { display: grid; grid-template-columns: repeat(6,1fr); gap: 8px; padding: 12px 20px; border-bottom: 1px solid #eee; }
.m-item { text-align: center; padding: 8px 4px; background: #fafafa; border-radius: 6px; }
.m-val { font-size: 18px; font-weight: 700; }
.m-label { font-size: 11px; color: #999; margin-top: 2px; }

.tab-bar { display: flex; border-bottom: 2px solid #e8e8e8; padding: 0 16px; background: #fff; flex-shrink: 0; overflow-x: auto; }
.tab-item { padding: 12px 16px; cursor: pointer; font-size: 13px; color: #666; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all .2s; white-space: nowrap; user-select: none; }
.tab-item:hover { color: #1890ff; }
.tab-item.active { color: #1890ff; border-bottom-color: #1890ff; font-weight: 600; }
.tab-content { flex: 1; overflow-y: auto; padding: 16px; }
.tab-header { font-weight: 600; margin-bottom: 8px; font-size: 14px; }

.chart-box { width: 100%; height: 380px; }
.chart-sm { width: 100%; height: 300px; }
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.mt-8 { margin-top: 8px; }

.log-panel { display: flex; flex-direction: column; height: 100%; }
.log-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: #2d2d2d; border-radius: 6px 6px 0 0; }
.log-path { color: #ccc; font-size: 12px; font-family: monospace; }
.log-body { flex: 1; background: #1e1e1e; color: #d4d4d4; padding: 12px; font-size: 13px; line-height: 1.65; border-radius: 0 0 6px 6px; overflow: auto; white-space: pre; margin: 0; text-align: left; font-family: 'SF Mono','Fira Code','Menlo','Consolas',monospace; }

.code-panel { display: flex; flex-direction: column; height: 100%; }
.code-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 14px; background: #2d2d2d; border-radius: 6px 6px 0 0; flex-shrink: 0; }
.code-title { color: #ccc; font-size: 13px; font-family: monospace; }
.code-body { flex: 1; background: #1e1e1e; color: #d4d4d4; padding: 14px; font-size: 13px; line-height: 1.6; border-radius: 0 0 6px 6px; overflow: auto; white-space: pre; margin: 0; text-align: left; font-family: 'SF Mono','Fira Code','Menlo','Consolas',monospace; tab-size: 4; }

.bt-strategy-banner { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #fafafa; border: 1px solid #e8e8e8; border-radius: 8px; }
.st-icon { width: 36px; height: 36px; border-radius: 6px; background: linear-gradient(135deg,#1890ff,#6f42c1); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
.st-info { flex: 1; }
.st-name { font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 8px; }
.st-meta { font-size: 12px; color: #999; margin-top: 2px; }
</style>
