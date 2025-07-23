import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import UserDashboardView from '../views/UserDashboardView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import ParkingLotsView from '../views/ParkingLotsView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guest: true }
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/dashboard',
      name: 'user-dashboard',
      component: UserDashboardView,
      meta: { requiresAuth: true, role: 'user' }
    },
    {
      path: '/profile',
      name: 'user-profile',
      component: UserProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/parking-lots',
      name: 'parking-lots',
      component: ParkingLotsView
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if user is authenticated
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.user?.role
  
  // If route requires authentication and user is not authenticated
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
    return
  }
  
  // If route is for guests only and user is authenticated
  if (to.meta.guest && isAuthenticated) {
    // Redirect based on user role
    if (userRole === 'admin') {
      next({ name: 'admin-dashboard' })
    } else {
      next({ name: 'user-dashboard' })
    }
    return
  }
  
  // Check role-based access
  if (to.meta.role && to.meta.role !== userRole) {
    if (userRole === 'admin') {
      next({ name: 'admin-dashboard' })
    } else if (userRole === 'user') {
      next({ name: 'user-dashboard' })
    } else {
      next({ name: 'home' })
    }
    return
  }
  
  // Allow navigation
  next()
})


export default router
