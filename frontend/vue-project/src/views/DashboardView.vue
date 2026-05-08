<script setup lang="ts">
import { onMounted, ref } from 'vue'
import StatCard from '@/components/StatCard.vue'
import AppMessage from '@/components/AppMessage.vue'
import { useInventarioStore } from '@/stores/inventario'
import { obtenerStock } from '@/api/inventario'
import type { ProductoStock, AppMessage as Msg } from '@/types'
import { condicion_producto } from '@/types'

const store = useInventarioStore()
const alertas = ref<ProductoStock[]>([])
const msg = ref<Msg | null>(null)
const cargandoAlertas = ref(false)

onMounted(() => {
  store.cargarResumen()
})

async function recargarDashboard() {
  msg.value = null
  await store.cargarResumen()
}

async function verAlertas() {
  try {
    cargandoAlertas.value = true
    msg.value = null
    const stock = await obtenerStock()
    alertas.value = stock.filter(
      p => p.estado === condicion_producto.BAJO || p.estado === condicion_producto.SIN_STOCK
    )
    if (alertas.value.length === 0) {
      msg.value = { text: 'No hay alertas de stock activas. ¡Todo en orden!', type: 'success' }
    }
  } catch {
    msg.value = { text: 'Error al cargar alertas.', type: 'error' }
  } finally {
    cargandoAlertas.value = false
  }
}
</script>

<template>
  <div>
    <!-- Estadísticas -->
    <div class="stats-grid">
      <StatCard
        :value="store.resumen.totalProductos"
        label="Total Productos"
        color="#2e86ab"
      />
      <StatCard
        :value="store.resumen.totalMovimientos"
        label="Total Movimientos"
        color="#17a2b8"
      />
      <StatCard
        :value="store.resumen.sinStock"
        label="Sin Stock"
        color="#dc3545"
      />
      <StatCard
        :value="store.resumen.stockBajo"
        label="Stock Bajo"
        color="#ffc107"
      />
      <StatCard
        :value="store.resumen.movimientosUltimoMes"
        label="Movim. Último Mes"
        color="#28a745"
      />
    </div>

    <!-- Alertas de stock -->
    <div class="card">
      <div class="card-header">⚠️ Alertas de Stock</div>
      <div class="card-body">
        <div class="actions">
          <button class="btn btn-primary" :disabled="store.cargandoResumen" @click="recargarDashboard">
            🔄 Actualizar Dashboard
          </button>
          <button class="btn btn-warning" :disabled="cargandoAlertas" @click="verAlertas">
            {{ cargandoAlertas ? 'Cargando...' : '📋 Ver Alertas de Stock' }}
          </button>
        </div>

        <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

        <div v-if="alertas.length > 0" class="table-container">
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Stock Actual</th>
                <th>Stock Mínimo</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="p in alertas"
                :key="p.codigo"
                :class="p.estado === condicion_producto.SIN_STOCK ? 'row-zero' : 'row-low'"
              >
                <td>{{ p.codigo }}</td>
                <td>{{ p.nombre }}</td>
                <td>{{ p.cantidad }}</td>
                <td>{{ p.stockMin }}</td>
                <td>{{ p.estado }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 18px;
  margin-bottom: 28px;
}
</style>
