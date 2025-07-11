import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/Login.vue'
import RegisterPage from '../views/Register.vue'
import DataTablePage from '../views/DataTable.vue'
import ChartViewPage from '../views/ChartView.vue'
import MainLayout from '../views/MainLayout.vue'

// 请确保 ../views/Login.vue、Register.vue、UserInfo.vue、DataTable.vue、ChartView.vue 文件已创建
const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/user', component: MainLayout, meta: { requiresAuth: true } },
  { path: '/table', component: DataTablePage, meta: { requiresAuth: true } },
  { path: '/chart', component: ChartViewPage, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫实现权限管理
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 