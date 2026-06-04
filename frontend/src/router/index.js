import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/Login.vue'
import RegisterPage from '../views/Register.vue'
import MainLayout from '../views/MainLayout.vue'
import StockListPage from '../views/StockList.vue'
import ChartViewPage from '../views/ChartView.vue'
import StockSelectPage from '../views/StockSelect.vue'
import UserInfoPage from '../views/UserInfo.vue'

import DashboardView from '../views/DashboardView.vue'
import DataCenterView from '../views/DataCenterView.vue'
import FactorLabView from '../views/FactorLabView.vue'
import StrategyWorkspaceView from '../views/StrategyWorkspaceView.vue'
import BacktestCenterView from '../views/BacktestCenterView.vue'
import StockSignalsView from '../views/StockSignalsView.vue'
import PortfolioRiskView from '../views/PortfolioRiskView.vue'
import TaskCenterView from '../views/TaskCenterView.vue'
import SystemSettingsView from '../views/SystemSettingsView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  {
    path: '/dashboard',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'dashboard-view' } },
      { path: 'overview', name: 'dashboard-view', component: DashboardView },
      { path: 'data', name: 'data-center', component: DataCenterView },
      { path: 'factors', name: 'factor-lab', component: FactorLabView },
      { path: 'strategies', name: 'strategy-workspace', component: StrategyWorkspaceView },
      { path: 'backtest', name: 'backtest-center', component: BacktestCenterView },
      { path: 'signals', name: 'stock-signals', component: StockSignalsView },
      { path: 'portfolio', name: 'portfolio-risk', component: PortfolioRiskView },
      { path: 'tasks', name: 'task-center', component: TaskCenterView },
      { path: 'settings', name: 'system-settings', component: SystemSettingsView }
    ]
  },
  { path: '/table', component: StockListPage, meta: { requiresAuth: true } },
  { path: '/chart', component: ChartViewPage, meta: { requiresAuth: true } },
  { path: '/stockselect', component: StockSelectPage, meta: { requiresAuth: true } },
  { path: '/userinfo', component: UserInfoPage, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
