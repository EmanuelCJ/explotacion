<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { mostrarUsuario } from '@/api/inventario'
import type { Usuario, AppMessage as Msg } from '@/types'

const usuarios = ref<Usuario[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const soloAlertas = ref(false)

const usuariosFiltrados = computed(() =>
  soloAlertas.value
    ? usuarios.value.filter(u => u.estado !== EstadoUsuario.NORMAL)
    : usuarios.value
)

function rowClass(u: Usuario): string {
  if (u.estado === EstadoUsuario.SIN_STOCK) return 'row-zero'
  if (u.estado === EstadoUsuario.BAJO) return 'row-low'
  return ''
}

onMounted(() => cargarStock())

async function cargarStock() {
  try {
    cargando.value = true
    msg.value = null
    usuarios.value = await mostrarUsuario()
  } catch {
    msg.value = { text: 'Error al cargar el inventario.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

async function exportar() {
  // try {
  //   const url = await exportarStockCSV()
  //   if (url) {
  //     window.open(url, '_blank')
  //     msg.value = { text: 'Stock exportado exitosamente.', type: 'success' }
  //   } else {
  //     msg.value = { text: 'Error al generar el archivo de exportación.', type: 'error' }
  //   }
  // } catch {
  //   msg.value = { text: 'Error al exportar.', type: 'error' }
  // }
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

      <div v-else-if="usuariosFiltrados.length > 0" class="table-container">
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
            <tr v-for="u in usuariosFiltrados" :key="u.codigo" :class="rowClass(u)">
              <td>{{ u.codigo }}</td>
              <td>{{ u.nombre }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.roles }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.apellido }}</td>
              <td>{{ u.created_at }}</td>
              <td>{{ u.activo }}</td>
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