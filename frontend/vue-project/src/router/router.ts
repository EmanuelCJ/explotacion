import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore' // Asegúrate de tener esta tienda para la autenticación
import HomeView from '@/views/HomeView.vue' // El nuevo archivo que creaste con el contenido anterior de App.vue
import LoginView from '@/views/LoginView.vue' // Asegúrate de tener esta vista para el login

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
      meta: { title: 'Acceso al Sistema' }
    },
    {
      path: '/home',
      name: 'home',
      meta: { requiresAuth: true },
      component: HomeView,
      redirect: '/home/productos',
      children: [
        {
          path: 'inventario',
          name: 'inventario',
          component: () => import('@/views/InventarioView.vue'),
          meta: { requiresAuth: true, title: 'Control de Inventario', icon: '📊' }
        },
        {
          path: 'dashboard', // Ruta raíz (redirecciona o muestra dashboard)
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { requiresAuth: true, title: 'Dashboard General', icon: '📊' }
        },
        {
          path: 'productos',
          name: 'productos',
          component: () => import('@/views/ProductosView.vue'),
          meta: { requiresAuth: true, title: 'Gestión de Productos', icon: '📦' }
        },
        {
          path: 'movimientos',
          name: 'movimientos',
          component: () => import('@/views/MovimientosView.vue'),
          meta: { requiresAuth: true, title: 'Movimientos', icon: '📋' }
        },
        {
          path: 'reportes',
          name: 'reportes',
          component: () => import('@/views/ReportesView.vue'),
          meta: { requiresAuth: true, title: 'Reportes y Análisis', icon: '📈' }
        },
        {
          path: 'buscar',
          name: 'buscar',
          component: () => import('@/views/BuscarView.vue'),
          meta: { requiresAuth: true, title: 'Búsqueda de Productos', icon: '🔍' }
        },
        {
          path: 'configuracion',
          name: 'configuracion',
          component: () => import('@/views/ConfiguracionView.vue'),
          meta: { requiresAuth: true, title: 'Configuración del Sistema', icon: '⚙️' }
        },
        {
          path: 'usuarios',
          name: 'usuarios',
          component: () => import('@/views/UsuariosView.vue'),
          meta: { requiresAuth: true, title: 'Gestión de Usuarios', icon: '👥' }
        },

      ]
    }
  ]
})

router.beforeEach(async (to) => {

  const auth = useAuthStore()

  if (!auth.initialized) {
    await auth.fetchUser()
  }

  // 2. Si la ruta requiere auth y NO está logueado → afuera
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/'
  }

  // 3. Si está logueado y quiere ir a login → redirigir
  if (to.path === '/' && auth.isAuthenticated) {
    return '/home'
  }

  return true
})

export default router