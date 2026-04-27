<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerStock, exportarStockCSV } from '@/api/inventario'
import type { ProductoStock, AppMessage as Msg } from '@/types'
import { EstadoStock } from '@/types'

const stock = ref<ProductoStock[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const soloAlertas = ref(false)

const stockFiltrado = computed(() =>
  soloAlertas.value
    ? stock.value.filter(p => p.estado !== EstadoStock.NORMAL)
    : stock.value
)

function rowClass(p: ProductoStock): string {
  if (p.estado === EstadoStock.SIN_STOCK) return 'row-zero'
  if (p.estado === EstadoStock.BAJO) return 'row-low'
  return ''
}

onMounted(() => cargarStock())

async function cargarStock() {
  try {
    cargando.value = true
    msg.value = null
    stock.value = await obtenerStock()
  } catch {
    msg.value = { text: 'Error al cargar el inventario.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

async function exportar() {
  try {
    const url = await exportarStockCSV()
    if (url) {
      window.open(url, '_blank')
      msg.value = { text: 'Stock exportado exitosamente.', type: 'success' }
    } else {
      msg.value = { text: 'Error al generar el archivo de exportación.', type: 'error' }
    }
  } catch {
    msg.value = { text: 'Error al exportar.', type: 'error' }
  }
}
</script>

<template>
  <div class="card">
    <div class="card-header">🗃️ Stock Actual</div>
    <div class="card-body">
      <div class="actions">
        <button class="btn btn-primary" :disabled="cargando" @click="cargarStock">
          {{ cargando ? 'Cargando...' : '🔄 Actualizar' }}
        </button>
        <button class="btn btn-success" @click="exportar">
          📥 Exportar CSV
        </button>
        <button
          class="btn"
          :class="soloAlertas ? 'btn-warning' : 'btn-secondary'"
          @click="soloAlertas = !soloAlertas"
        >
          {{ soloAlertas ? '📋 Mostrar Todo' : '⚠️ Solo Alertas' }}
        </button>
      </div>

      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <p v-if="cargando" class="loading">Cargando inventario...</p>

      <div v-else-if="stockFiltrado.length > 0" class="table-container">
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Unidad</th>
              <th>Grupo</th>
              <th>Stock Mín.</th>
              <th>Stock Actual</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in stockFiltrado" :key="p.codigo" :class="rowClass(p)">
              <td>{{ p.codigo }}</td>
              <td>{{ p.nombre }}</td>
              <td>{{ p.unidad }}</td>
              <td>{{ p.grupo }}</td>
              <td>{{ p.stockMin }}</td>
              <td>{{ p.cantidad }}</td>
              <td>{{ p.estado }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="!cargando" class="empty">
        {{ soloAlertas ? 'No hay alertas de stock activas.' : 'No hay productos registrados.' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading, .empty {
  text-align: center;
  padding: 24px;
  color: #6c757d;
  font-style: italic;
}
</style>
