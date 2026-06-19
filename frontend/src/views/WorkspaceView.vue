<template>
  <div class="workspace">
    <div class="stat-grid">
      <el-card v-for="s in stats" :key="s.label" shadow="hover" :class="s.color" @click="s.link && $router.push(s.link)">
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-value">{{ s.value }}</div>
        <div class="stat-sub">{{ s.sub }}</div>
      </el-card>
    </div>
    <div class="row-2">
      <el-card header="最近回测"><el-table :data="recentBacktests" size="small"><el-table-column prop="strategy_name" label="策略" /><el-table-column label="状态"><template #default="{row}"><el-tag :type="row.status==='completed'?'success':'warning'" size="small">{{ row.status }}</el-tag></template></el-table-column><el-table-column label="收益"><template #default="{row}"><span :class="row.total_return>0?'green':'red'">{{ row.total_return ? (row.total_return*100).toFixed(1)+'%' : '-' }}</span></template></el-table-column><el-table-column prop="created_at" label="时间" /></el-table></el-card>
      <el-card header="策略概览"><el-table :data="recentStrategies" size="small"><el-table-column prop="name" label="策略" /><el-table-column prop="latest_version" label="版本" /><el-table-column prop="status" label="状态" /><el-table-column prop="updated_at" label="更新" /></el-table></el-card>
    </div>
  </div>
</template>

<script>
import axios from '@/config/axios'
export default {
  name: 'WorkspaceView',
  data() {
    return {
      stats: [{ label:'回测总数',value:'...',sub:'加载中',color:'blue',link:'/backtest'},{ label:'运行中',value:'...',sub:'',color:'orange'},{ label:'策略总数',value:'...',sub:'',color:'green',link:'/strategies'},{ label:'数据覆盖',value:'...',sub:'',color:'purple' }],
      recentBacktests: [], recentStrategies: []
    }
  },
  async mounted() {
    try { const r = await axios.get('/api/backtests',{params:{page_size:5}}); if(r.data?.success){ this.recentBacktests=r.data.data?.items||[]; this.stats[0].value=r.data.data?.total||0; this.stats[1].value=this.recentBacktests.filter(b=>b.status==='running').length } } catch(e){ console.error(e) }
    try { const r = await axios.get('/api/strategies',{params:{page_size:5}}); if(r.data?.success){ this.recentStrategies=r.data.data?.items||[]; this.stats[2].value=r.data.data?.total||0 } } catch(e){ console.error(e) }
    try { const r = await axios.get('/api/data/overview'); if(r.data?.success){ const d=r.data.data; this.stats[3].value=d.total_stocks||0; this.stats[3].sub=d.date_range_start?`${d.date_range_start} ~ ${d.latest_trade_date}`:'' } } catch(e){ console.error(e) }
  }
}
</script>

<style scoped>
.workspace { padding: 20px; }
.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 20px; }
.stat-grid .el-card { cursor: pointer; }
.stat-label { font-size: 13px; color: #666; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-sub { font-size: 12px; color: #999; margin-top: 4px; }
.blue .stat-value { color: #1890ff; } .green .stat-value { color: #52c41a; }
.orange .stat-value { color: #faad14; } .purple .stat-value { color: #6f42c1; }
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.green { color: #52c41a; font-weight: 600; } .red { color: #ff4d4f; font-weight: 600; }
</style>
