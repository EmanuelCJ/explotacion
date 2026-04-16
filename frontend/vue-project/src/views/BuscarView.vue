<script setup lang="ts">
import { ref } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { buscarProducto } from '@/api/inventario'
import type { ProductoStock, AppMessage as Msg } from '@/types'
import { EstadoStock } from '@/types'

const texto = ref('')
const resultados = ref<ProductoStock[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)
let debounceTimer: ReturnType<typeof setTimeout>

function rowClass(p: ProductoStock): string {
  if (p.estado === EstadoStock.SIN_STOCK) return 'row-zero'
  if (p.estado === EstadoStock.BAJO) return 'row-low'
  return ''
}

async function buscar() {
  if (!texto.value.trim()) {
    resultados.value = []
    msg.value = null
    return
  }
  try {
    cargando.value = true
    msg.value = null
    resultados.value = await buscarProducto(texto.value)
    if (resultados.value.length === 0) {
      msg.value = { text: 'No se encontraron productos con ese criterio.', type: 'warning' }
    }
  } catch {
    msg.value = { text: 'Error al buscar productos.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

function buscarEnTiempoReal() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(buscar, 350)
}

function limpiar() {
  texto.value = ''
  resultados.value = []
  msg.value = null
}
</script>

<template>
  <div class="card">
    <div class="card-header">🔍 Buscar Productos</div>
    <div class="card-body">

      <div class="form-grid">
        <div class="form-group search-group">
          <label>Buscar por código, nombre o grupo</label>
          <input
            v-model="texto"
            type="text"
            placeholder="Escriba para buscar..."
            @keyup="buscarEnTiempoReal"
            @keyup.enter="buscar"
          />
        </div>
      </div>

      <div class="actions">
        <button class="btn btn-primary" :disabled="cargando" @click="buscar">
          {{ cargando ? 'Buscando...' : '🔍 Buscar' }}
        </button>
        <button class="btn btn-secondary" @click="limpiar">🗑 Limpiar</button>
      </div>

      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <div v-if="resultados.length > 0" class="table-container">
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
            <tr v-for="p in resultados" :key="p.codigo" :class="rowClass(p)">
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

    </div>
  </div>
</template>

<style scoped>
.search-group { grid-column: 1 / -1; }
</style>
