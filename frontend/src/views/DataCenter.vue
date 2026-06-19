<template>
  <div class="data-page">
    <div class="stat-grid">
      <el-card v-for="s in stats" :key="s.label" shadow="hover"><div class="stat-label">{{ s.label }}</div><div class="stat-value">{{ s.value }}</div><div class="stat-sub">{{ s.sub }}</div></el-card>
    </div>
    <el-card header="数据源管理">
      <el-table :data="sources" size="small"><el-table-column prop="display_name" label="数据源" /><el-table-column prop="status" label="状态"><template #default="{row}"><el-tag :type="row.status==='active'?'success':'warning'" size="small">{{ row.status }}</el-tag></template></el-table-column><el-table-column label="操作"><template #default="{row}"><el-button size="small" @click="syncSource(row.name)">🔄 同步</el-button></template></el-table-column></el-table>
    </el-card>
  </div>
</template>

<script>
import axios from '@/config/axios'
export default {
  name: 'DataCenter',
  data() { return { stats: [{label:'A股总数',value:'...',sub:''},{label:'最新日期',value:'...',sub:''},{label:'数据源',value:'...',sub:''}], sources: [] } },
  async mounted() {
    try { const r = await axios.get('/api/data/overview'); if(r.data?.success){ const d=r.data.data; this.stats[0].value=d.total_stocks||0; this.stats[1].value=d.latest_trade_date||'N/A' } } catch(e){ console.error(e) }
    try { const r = await axios.get('/api/data/sources'); if(r.data?.success) this.sources=r.data.data||[]; this.stats[2].value=this.sources.filter(s=>s.status==='active').length } catch(e){ console.error(e) }
  },
  methods: {
    async syncSource(name) { try { await axios.post('/api/data/sync',{source:name,data_type:'daily'}); this.$message.success('同步任务已创建') } catch(e) { this.$message.error('同步失败') } }
  }
}
</script>

<style scoped>
.data-page { padding: 20px; }
.stat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 20px; }
.stat-label { font-size: 13px; color: #666; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #1890ff; }
.stat-sub { font-size: 12px; color: #999; margin-top: 4px; }
</style>
