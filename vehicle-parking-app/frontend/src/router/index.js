import Vue from 'vue'
import Router from 'vue-router'
import Home from '../views/Home.vue'
import Admin from '../views/Admin.vue'
import User from '../views/User.vue'

Vue.use(Router)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin
  },
  {
    path: '/user',
    name: 'User',
    component: User
  }
]

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router