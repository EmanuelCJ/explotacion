import { createRouter, createWebHistory } from 'vue-router'

// IMPORTACIONES DE VISTAS
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/Home',
      name: 'home',
      component: HomeView,
    },
  ],
})

export default router
