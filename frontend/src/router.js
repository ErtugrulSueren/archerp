import { createRouter, createWebHistory } from 'vue-router'
import { call } from 'frappe-ui'

const routes = [
  {
    path: '/',
    redirect: '/workspace'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/workspace',
    name: 'Workspace',
    component: () => import('@/pages/Workspace.vue'),
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/design',
    name: 'DesignSystem',
    component: () => import('@/pages/DesignSystem.vue'),
  },
  {
    path: '/auto/:doctype',
    name: 'DocTypeList',
    component: () => import('@/components/DocTypeList.vue'),
    props: true
  },
  {
    path: '/auto/:doctype/new',
    name: 'NewDocType',
    component: () => import('./pages/Form.vue'), // Geçici olarak mevcut bir form veya yenisini yapacağız
    props: true
  },
  {
    path: '/auto/:doctype/:id',
    name: 'AutoDetail',
    component: () => import('@/pages/Form.vue'),
    props: true
  },
  {
    path: '/report/:reportName',
    name: 'Report',
    component: () => import('@/pages/Report.vue'),
    props: true,
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  try {
    const user = await call('frappe.auth.get_logged_user')
    const isLoggedIn = user !== 'Guest'

    if (to.name === 'Login') {
      if (isLoggedIn) {
        next({ name: 'Workspace' })
      } else {
        next()
      }
      return
    }

    if (!isLoggedIn) {
      next({ name: 'Login' })
      return
    }

    next()
  } catch (error) {
    // Hata durumunda login'e at (en güvenli)
    if (to.name !== 'Login') {
      next({ name: 'Login' })
    } else {
      next()
    }
  }
})

export default router
