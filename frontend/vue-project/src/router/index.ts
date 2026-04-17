import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue' // El nuevo archivo que creaste con el contenido anterior de App.vue
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: 'Acceso al Sistema' }
    },
    {
      path: '/',
      component: HomeView, // Este actúa como contenedor con Sidebar
      children: [
        {
          path: '', // Ruta raíz (redirecciona o muestra dashboard)
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: 'Dashboard General', icon: '📊' }
        },
        {
          path: 'productos',
          name: 'productos',
          component: () => import('@/views/ProductosView.vue'),
          meta: { title: 'Gestión de Productos', icon: '📦' }
        },
        {
          path: 'movimientos',
          name: 'movimientos',
          component: () => import('@/views/MovimientosView.vue'),
          meta: { title: 'Movimientos', icon: '📋' }
        },
        {
          path: 'inventario',
          name: 'inventario',
          component: () => import('@/views/InventarioView.vue'),
          meta: { title: 'Control de Inventario', icon: '📊' }
        },
        {
          path: 'reportes',
          name: 'reportes',
          component: () => import('@/views/ReportesView.vue'),
          meta: { title: 'Reportes y Análisis', icon: '📈' }
        },
        {
          path: 'buscar',
          name: 'buscar',
          component: () => import('@/views/BuscarView.vue'),
          meta: { title: 'Búsqueda de Productos', icon: '🔍' }
        },
        {
          path: 'configuracion',
          name: 'configuracion',
          component: () => import('@/views/ConfiguracionView.vue'),
          meta: { title: 'Configuración del Sistema', icon: '⚙️' }
        }
      ]
    }
  ]
})

// Opcional: Guardia de navegación para proteger las rutas de ARSA
router.beforeEach((to, from, next) => {
  
  const authRequired = localStorage.getItem('refresh_token');
  const loggedIn = localStorage.getItem('access_token'); // O tu lógica de Pinia

  if (to.path === '/login' && authRequired && loggedIn) {
    return next('/dashboard'); // Redirige al dashboard si ya estás autenticado
  }
  next();
});

export default router