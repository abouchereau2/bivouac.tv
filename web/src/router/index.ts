import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/Home.vue'),
    },
    {
      path: '/browse',
      name: 'browse',
      component: () => import('@/pages/Browse.vue'),
    },
    {
      path: '/doc/:slug',
      name: 'documentary',
      component: () => import('@/pages/DocDetail.vue'),
      props: true,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/auth/Login.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/pages/auth/Register.vue'),
      meta: { guest: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/pages/Profile.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/watchlist',
      name: 'watchlist',
      component: () => import('@/pages/Watchlist.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/watched',
      name: 'watched',
      component: () => import('@/pages/Watched.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('@/pages/Favorites.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('@/pages/Notifications.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/submit',
      name: 'submit',
      component: () => import('@/pages/Submit.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/pages/Admin.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    // Redirect old language-prefixed URLs to new paths
    {
      path: '/:lang(en|fr)/:pathMatch(.*)*',
      redirect: (to) => {
        const pathAfterLang = to.params.pathMatch
        if (Array.isArray(pathAfterLang)) {
          return '/' + pathAfterLang.join('/')
        }
        return '/' + (pathAfterLang || '')
      },
    },
    {
      path: '/:lang(en|fr)',
      redirect: '/',
    },
    // 404 for unknown paths
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/NotFound.vue'),
    },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Initialize auth state if needed
  if (!authStore.user && localStorage.getItem('access_token')) {
    await authStore.initialize()
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route is for guests only
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  // Check if route requires admin
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
