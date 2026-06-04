<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-row">
        <div>
          <h2>任务中心</h2>
          <p class="page-desc">统一查看数据同步、策略运行、回测和通知任务。</p>
        </div>
        <el-button type="primary" @click="handleRunTaskNow">立即执行</el-button>
      </div>
    </div>
    <el-card>
      <el-table :data="taskList" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="task_name" label="任务名" min-width="160" />
        <el-table-column prop="task_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTagMap[row.task_type] || 'info'">{{ row.task_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="计划时间" width="160" />
        <el-table-column prop="last_run_at" label="最近运行" width="180">
          <template #default="{ row }">{{ row.last_run_at || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusTagMap[row.status] || 'info'" effect="dark">
              {{ statusLabelMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">{{ row.duration ? row.duration + 's' : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showLog(row)">日志</el-button>
            <el-button size="small" type="primary" @click="handleRetry(row)" :disabled="row.status === 'running'" :loading="retryingId === row.id">立即执行</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper" v-if="total > pageSize">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" :current-page="currentPage" @current-change="handlePageChange" />
      </div>
    </el-card>

    <el-drawer v-model="drawerVisible" :title="'任务日志 - ' + (currentTask ? currentTask.task_name : '')" size="520px" direction="rtl">
      <div v-if="stepsLoading" style="text-align: center; padding: 40px;">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
      <el-timeline v-else-if="taskSteps.length > 0">
        <el-timeline-item v-for="(step, idx) in taskSteps" :key="idx" :timestamp="step.started_at || ''" placement="top" :type="stepStatusType(step.status)">
          <el-card shadow="never" class="step-card">
            <div class="step-header">
              <span class="step-name">{{ step.step_name }}</span>
              <el-tag size="small" :type="statusTagMap[step.status] || 'info'">{{ statusLabelMap[step.status] || step.status }}</el-tag>
            </div>
            <div v-if="step.message" class="step-message">{{ step.message }}</div>
            <div v-if="step.duration" class="step-duration">耗时: {{ step.duration }}s</div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无步骤记录" />
    </el-drawer>
  </div>
</template>

<script>
import { Loading } from '@element-plus/icons-vue'
import axios from '@/config/axios'

export default {
  name: 'TaskCenterView',
  components: { Loading },
  data() {
    return {
      taskList: [],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      drawerVisible: false,
      currentTask: null,
      taskSteps: [],
      stepsLoading: false,
      retryingId: null,
      statusTagMap: {
        pending: 'info',
        running: '',
        success: 'success',
        failed: 'danger',
        cancelled: 'warning'
      },
      statusLabelMap: {
        pending: '待执行',
        running: '运行中',
        success: '成功',
        failed: '失败',
        cancelled: '已取消'
      },
      typeTagMap: {
        data_sync: '',
        strategy: 'success',
        backtest: 'warning',
        notification: 'danger'
      }
    }
  },
  methods: {
    async fetchTasks() {
      this.loading = true
      try {
        const res = await axios.get('/api/tasks', {
          params: { page: this.currentPage, page_size: this.pageSize }
        })
        if (res.data && res.data.data) {
          this.taskList = res.data.data.items || res.data.data || []
          this.total = res.data.data.total || this.taskList.length
        } else if (Array.isArray(res.data)) {
          this.taskList = res.data
          this.total = res.data.length
        }
      } catch (e) {
        console.error('获取任务列表失败:', e)
        this.$message.error('获取任务列表失败')
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchTasks()
    },
    async showLog(task) {
      this.currentTask = task
      this.drawerVisible = true
      this.taskSteps = []
      this.stepsLoading = true
      try {
        const res = await axios.get(`/api/tasks/${task.id}`)
        if (res.data && res.data.data && res.data.data.steps) {
          this.taskSteps = res.data.data.steps
        } else if (res.data && res.data.steps) {
          this.taskSteps = res.data.steps
        }
      } catch (e) {
        console.error('获取任务详情失败:', e)
        this.$message.error('获取任务详情失败')
      } finally {
        this.stepsLoading = false
      }
    },
    async handleRetry(task) {
      this.retryingId = task.id
      try {
        const res = await axios.post(`/api/tasks/${task.id}/retry`)
        if (res.data && res.data.success) {
          this.$message.success('任务已提交执行')
          this.fetchTasks()
        } else {
          this.$message.error(res.data.message || '执行失败')
        }
      } catch (e) {
        console.error('执行任务失败:', e)
        this.$message.error('执行任务失败')
      } finally {
        this.retryingId = null
      }
    },
    stepStatusType(status) {
      const map = { success: 'success', failed: 'danger', running: 'primary', pending: 'info' }
      return map[status] || 'info'
    },
    async handleRunTaskNow() {
      try {
        await axios.post('/api/tasks/run-now')
        this.$message.success('任务已开始执行')
        this.fetchTasks()
      } catch {
        const now = new Date()
        const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
        this.taskList.unshift({
          id: Date.now(),
          task_name: '手动任务',
          task_type: '策略',
          schedule: '立即',
          last_run_at: timeStr,
          status: 'running',
          duration: null
        })
        this.$message.success('任务已开始执行')
      }
    }
  },
  mounted() {
    this.fetchTasks()
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; color: #303133; }
.page-header-row { display: flex; justify-content: space-between; align-items: flex-start; }
.page-desc { margin: 0; color: #909399; font-size: 14px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
.step-card { margin-bottom: 0; }
.step-header { display: flex; justify-content: space-between; align-items: center; }
.step-name { font-weight: 500; font-size: 14px; }
.step-message { margin-top: 8px; color: #606266; font-size: 13px; word-break: break-all; }
.step-duration { margin-top: 4px; color: #909399; font-size: 12px; }
</style>
