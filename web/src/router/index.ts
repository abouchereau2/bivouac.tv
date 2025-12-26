import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { setLocale, SUPPORTED_LOCALES, DEFAULT_LOCALE, type SupportedLocale } from '@/i18n'

// Define routes without language prefix - will be wrapped
const appRoutes = [
  {
    path: '',
    name: 'home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: 'browse',
    name: 'browse',
    component: () => import('@/pages/Browse.vue'),
  },
  {
    path: 'doc/:slug',
    name: 'documentary',
    component: () => import('@/pages/DocDetail.vue'),
    props: true,
  },
  {
    path: 'login',
    name: 'login',
    component: () => import('@/pages/auth/Login.vue'),
    meta: { guest: true },
  },
  {
    path: 'register',
    name: 'register',
    component: () => import('@/pages/auth/Register.vue'),
    meta: { guest: true },
  },
  {
    path: 'profile',
    name: 'profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: 'watchlist',
    name: 'watchlist',
    component: () => import('@/pages/Watchlist.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: 'watched',
    name: 'watched',
    component: () => import('@/pages/Watched.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: 'favorites',
    name: 'favorites',
    component: () => import('@/pages/Favorites.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: 'submit',
    name: 'submit',
    component: () => import('@/pages/Submit.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Language-prefixed routes
    {
      path: '/:lang(en|fr)',
      component: () => import('@/layouts/LangLayout.vue'),
      children: appRoutes,
    },
    // Redirect root to default language
    {
      path: '/',
      redirect: () => {
        // Check stored preference or browser language
        const stored = localStorage.getItem('locale')
        if (stored && SUPPORTED_LOCALES.includes(stored as SupportedLocale)) {
          return `/${stored}`
        }
        const browserLang = navigator.language.split('-')[0]
        if (SUPPORTED_LOCALES.includes(browserLang as SupportedLocale)) {
          return `/${browserLang}`
        }
        return `/${DEFAULT_LOCALE}`
      },
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

  // Set locale from route param
  const lang = to.params.lang as SupportedLocale
  if (lang && SUPPORTED_LOCALES.includes(lang)) {
    setLocale(lang)
  }

  // Initialize auth state if needed
  if (!authStore.user && localStorage.getItem('access_token')) {
    await authStore.initialize()
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    const lang = to.params.lang || DEFAULT_LOCALE
    next({ name: 'login', params: { lang }, query: { redirect: to.fullPath } })
    return
  }

  // Check if route is for guests only
  if (to.meta.guest && authStore.isAuthenticated) {
    const lang = to.params.lang || DEFAULT_LOCALE
    next({ name: 'home', params: { lang } })
    return
  }

  next()
})

export default router
