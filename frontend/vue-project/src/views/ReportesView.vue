<script setup lang="ts">
import { ref } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerHistorial } from '@/api/inventario'
import { TipoMovimiento } from '@/types'
import type { Movimiento, FiltrosHistorial, AppMessage as Msg } from '@/types'

const movimientos = ref<Movimiento[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)

function hoy(): string { return new Date().toISOString().split('T')[0] }
function haceUnMes(): string {
  const d = new Date(); d.setMonth(d.getMonth() - 1)
  return d.toISOString().split('T')[0]
}

const filtros = ref<FiltrosHistorial>({
  fechaDesde: haceUnMes(),
  fechaHasta: hoy(),
  tipo: ''
})

const tiposOpciones = [
  { value: '',                             label: 'Todos los movimientos' },
  { value: TipoMovimiento.INGRESO,         label: 'Solo Ingresos' },
  { value: TipoMovimiento.SALIDA,          label: 'Solo Salidas' },
  { value: TipoMovimiento.AJUSTE_POSITIVO, label: 'Solo Ajustes Positivos' },
  { value: TipoMovimiento.AJUSTE_NEGATIVO, label: 'Solo Ajustes Negativos' }
]

function tipoClass(tipo: string): string {
  if (tipo === 'INGRESO' || tipo === 'AJUSTE_POSITIVO') return 'text-success'
  if (tipo === 'SALIDA'  || tipo === 'AJUSTE_NEGATIVO') return 'text-danger'
  return 'text-warning'
}

function tipoLabel(tipo: string): string {
  const map: Record<string, string> = {
    INGRESO: 'Ingreso', SALIDA: 'Salida',
    AJUSTE_POSITIVO: 'Ajuste +', AJUSTE_NEGATIVO: 'Ajuste -', AJUSTE: 'Ajuste'
  }
  return map[tipo] ?? tipo
}

async function generar() {
  if (!filtros.value.fechaDesde || !filtros.value.fechaHasta) {
    msg.value = { text: 'Seleccione las fechas de consulta.', type: 'warning' }
    return
  }
  try {
    cargando.value = true
    msg.value = null
    movimientos.value = await obtenerHistorial(filtros.value)
    if (movimientos.value.length === 0) {
      msg.value = { text: 'No hay movimientos en el período seleccionado.', type: 'warning' }
    }
  } catch {
    msg.value = { text: 'Error al obtener el historial.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

function exportarCSV() {
  if (movimientos.value.length === 0) {
    msg.value = { text: 'No hay datos para exportar.', type: 'warning' }
    return
  }
  let csv = 'Fecha,Código,Producto,Tipo,Cantidad,Observaciones\n'
  movimientos.value.forEach(m => {
    csv += `"${m.fecha}","${m.codigo}","${m.producto}","${m.tipo}","${m.cantidad}","${m.observaciones}"\n`
  })
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Reporte_${filtros.value.fechaDesde}_${filtros.value.fechaHasta}.csv`
  a.click()
  URL.revokeObjectURL(url)
  msg.value = { text: 'Reporte exportado correctamente.', type: 'success' }
}
</script>

<template>
  <div class="card">
    <div class="card-header">📈 Historial de Movimientos</div>
    <div class="card-body">

      <div class="form-grid">
        <div class="form-group">
          <label>Fecha Desde</label>
          <input v-model="filtros.fechaDesde" type="date" />
        </div>
        <div class="form-group">
          <label>Fecha Hasta</label>
          <input v-model="filtros.fechaHasta" type="date" />
        </div>
        <div class="form-group">
          <label>Filtrar por Tipo</label>
          <select v-model="filtros.tipo">
            <option v-for="t in tiposOpciones" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
      </div>

      <div class="actions">
        <button class="btn btn-primary" :disabled="cargando" @click="generar">
          {{ cargando ? 'Cargando...' : '📊 Generar Reporte' }}
        </button>
        <button class="btn btn-success" :disabled="movimientos.length === 0" @click="exportarCSV">
          📥 Exportar CSV
        </button>
      </div>

      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <div v-if="movimientos.length > 0">
        <p class="resultado-info">Se encontraron {{ movimientos.length }} movimientos.</p>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Código</th>
                <th>Producto</th>
                <th>Tipo</th>
                <th>Cantidad</th>
                <th>Observaciones</th>
                <th>Usuario</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(m, i) in movimientos" :key="i">
                <td>{{ m.fecha }}</td>
                <td>{{ m.codigo }}</td>
                <td>{{ m.producto }}</td>
                <td :class="tipoClass(m.tipo)">{{ tipoLabel(m.tipo) }}</td>
                <td>{{ m.cantidad }}</td>
                <td>{{ m.observaciones }}</td>
                <td>{{ m.usuario }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.resultado-info {
  color: #2e86ab;
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 0.9rem;
}
</style>
