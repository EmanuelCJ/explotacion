import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore' // Asegúrate de tener esta tienda para la autenticación

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: {
        title: 'Acceso al Sistema'
      }
    },
    {
      path: '/403',
      name: '403',
      component: () => import('@/views/Error403View.vue'),
      meta: {
        requiresAuth: false,
        title: 'Error de Permisos',
        icon: '❌',
      }
    },
    {
      path: '/home',
      name: 'home',
      meta: {
        requiresAuth: true,
        roles: ['admin', 'maestro', 'supervisor', 'usuario']
      },
      component: () => import('@/views/HomeView.vue'),
      redirect: '/home/dashboard',
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
            roles: ['admin', 'maestro']
          }
        },
        {
          path: 'gestor',
          name: 'gestor',
          component: () => import('@/views/GestorUsuariosView.vue'),
          meta: {
            requiresAuth: true,
            title: 'Gestión de Usuarios',
            icon: '👥',
            roles: ['admin', 'maestro']
          }
        },
      ]
    }
  ]
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Inicializar sesión
  if (!auth.initialized) {
    await auth.fetchUser()
  }

  // Si está logueado y quiere ir al login
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'home' }
  }

  // Rutas públicas
  if (to.name === 'login' || to.name === '403') {
    return true
  }

  // Verificar autenticación
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  // Verificar roles
  if (to.meta.roles) {
    const rolesPermitidos = to.meta.roles as string[]

    // ⚠️ Esperar a que exista rol
    if (!auth.rol) {
      await auth.fetchMe()
    }

    if (!auth.hasRoles(rolesPermitidos)) {
      return { name: '403' }
    }
  }

  return true
})

export default router