import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/workspace' },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: 'workspace', name: 'workspace', component: () => import('../views/WorkspaceView.vue') },
      { path: 'strategies', name: 'strategies', component: () => import('../views/StrategyResearch.vue') },
      { path: 'strategies/:id', name: 'strategy-detail', component: () => import('../views/StrategyResearch.vue') },
      { path: 'backtest', name: 'backtest', component: () => import('../views/BacktestCenter.vue') },
      { path: 'backtest/:id', name: 'backtest-detail', component: () => import('../views/BacktestCenter.vue') },
      { path: 'data', name: 'data', component: () => import('../views/DataCenter.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/SystemSettings.vue') }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  if (to.meta.requiresAuth && !isAuthenticated) next('/login')
  else next()
})

export default router
