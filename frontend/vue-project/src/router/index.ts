import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: 'Dashboard General', icon: '📊' }
    },
    {
      path: '/productos',
      name: 'productos',
      component: () => import('@/views/ProductosView.vue'),
      meta: { title: 'Gestión de Productos', icon: '📦' }
    },
    {
      path: '/movimientos',
      name: 'movimientos',
      component: () => import('@/views/MovimientosView.vue'),
      meta: { title: 'Movimientos', icon: '📋' }
    },
    {
      path: '/inventario',
      name: 'inventario',
      component: () => import('@/views/InventarioView.vue'),
      meta: { title: 'Control de Inventario', icon: '📊' }
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: () => import('@/views/ReportesView.vue'),
      meta: { title: 'Reportes y Análisis', icon: '📈' }
    },
    {
      path: '/buscar',
      name: 'buscar',
      component: () => import('@/views/BuscarView.vue'),
      meta: { title: 'Búsqueda de Productos', icon: '🔍' }
    },
    {
      path: '/configuracion',
      name: 'configuracion',
      component: () => import('@/views/ConfiguracionView.vue'),
      meta: { title: 'Configuración del Sistema', icon: '⚙️' }
    }
  ]
})

export default router
