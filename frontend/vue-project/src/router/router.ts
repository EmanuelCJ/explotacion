import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore' // Asegúrate de tener esta tienda para la autenticación
import { useUsuarioStore } from '@/stores/UsuarioStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: 'Acceso al Sistema' }
    },
    {
      path: '/home',
      name: 'home',
      meta: {
        requiresAuth: true,
        roles: ['admin', 'maestro', 'supervisor', 'usuario']
      },
      component: () => import('@/views/HomeView.vue'),
      redirect: '/home/productos',
      children: [
        {
          path: 'inventario',
          name: 'inventario',
          component: () => import('@/views/InventarioView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Control de Inventario',
            icon: '📊',
            roles: ['admin', 'maestro', 'supervisor', 'usuario']
          }
        },
        {
          path: 'dashboard', // Ruta raíz (redirecciona o muestra dashboard)
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Dashboard General',
            icon: '📊',
            roles: ['admin', 'maestro', 'supervisor', 'usuario']
          }
        },
        {
          path: 'productos',
          name: 'productos',
          component: () => import('@/views/ProductosView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Gestión de Productos',
            icon: '📦',
            roles: ['admin', 'maestro', 'supervisor', 'usuario']
          }
        },
        {
          path: 'movimientos',
          name: 'movimientos',
          component: () => import('@/views/MovimientosView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Movimientos',
            icon: '📋',
            roles: ['admin', 'maestro', 'supervisor', 'usuario']
          }
        },
        {
          path: 'reportes',
          name: 'reportes',
          component: () => import('@/views/ReportesView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Reportes y Análisis',
            icon: '📈',
            roles: ['admin', 'maestro']
          }
        },
        {
          path: 'buscar',
          name: 'buscar',
          component: () => import('@/views/BuscarView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Búsqueda de Productos',
            icon: '🔍',
            roles: ['admin', 'maestro', 'supervisor', 'usuario']
          }
        },
        {
          path: 'configuracion',
          name: 'configuracion',
          component: () => import('@/views/ConfiguracionView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Configuración del Sistema',
            icon: '⚙️',
            roles: ['admin', 'maestro', 'supervisor', 'usuario']
          }
        },
        {
          path: 'usuarios',
          name: 'usuarios',
          component: () => import('@/views/UsuariosView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Gestión de Usuarios',
            icon: '👥',
            roles: ['admin']
          }
        },
        {
          path: '/403',
          name: '403',
          component: () => import('@/views/Error403View.vue'),
          meta: {
            title: 'Error de Permisos',
            icon: '❌',
          }
        },
      ]
    }
  ]
})

router.beforeEach(async (to) => {

  const auth = useAuthStore()
  const usuario = useUsuarioStore()

  if (!auth.initialized) {
    await auth.fetchUser()
  }

  // 2. Si la ruta requiere auth y NO está logueado → afuera
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/'
  }

  //  // 🔐 validar roles
  // if (to.meta.roles && !usuario.hasRole(to.meta.roles as string[])) {
  //   return '/home'
  // }

  // 3. Si está logueado y quiere ir a login → redirigir
  if (to.path === '/' && auth.isAuthenticated) {
    return '/home'
  }

  return true
})

export default router