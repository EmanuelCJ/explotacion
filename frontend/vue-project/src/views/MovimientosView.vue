<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AutocompleteInput from '@/components/AutocompleteInput.vue'
import AppMessage from '@/components/AppMessage.vue'
import { registrarMovimiento } from '@/api/inventario'
import { TipoMovimiento } from '@/types'
import type { NuevoMovimientoPayload, ProductoSugerencia, AppMessage as Msg } from '@/types'

const msg = ref<Msg | null>(null)
const cargando = ref(false)

const form = ref<NuevoMovimientoPayload>({
  codigo: '',
  fecha: hoy(),
  tipo: TipoMovimiento.INGRESO,
  cantidad: 0,
  observaciones: ''
})

const nombreProducto = ref('')

const tiposMovimiento = [
  { value: TipoMovimiento.INGRESO,         label: 'Ingreso' },
  { value: TipoMovimiento.SALIDA,          label: 'Salida' },
  { value: TipoMovimiento.AJUSTE_POSITIVO, label: 'Ajuste Positivo' },
  { value: TipoMovimiento.AJUSTE_NEGATIVO, label: 'Ajuste Negativo' }
]

function hoy(): string {
  return new Date().toISOString().split('T')[0]
}

onMounted(() => {
  form.value.fecha = hoy()
})

function onSelectProducto(p: ProductoSugerencia) {
  form.value.codigo = p.codigo
  nombreProducto.value = p.nombre
}

async function submitForm() {
  msg.value = null
  if (!form.value.codigo.trim()) {
    msg.value = { text: 'Ingrese el código del producto.', type: 'warning' }
    return
  }
  if (!form.value.cantidad || form.value.cantidad <= 0) {
    msg.value = { text: 'La cantidad debe ser mayor a 0.', type: 'warning' }
    return
  }
  try {
    cargando.value = true
    const respuesta = await registrarMovimiento(form.value)
    const esOk = respuesta.toLowerCase().includes('correctamente')
    msg.value = { text: respuesta, type: esOk ? 'success' : 'error' }
    if (esOk) limpiar()
  } catch {
    msg.value = { text: 'Error al conectar con el servidor.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

function limpiar() {
  form.value = { codigo: '', fecha: hoy(), tipo: TipoMovimiento.INGRESO, cantidad: 0, observaciones: '' }
  nombreProducto.value = ''
  msg.value = null
}
</script>

<template>
  <div class="card">
    <div class="card-header">📋 Registrar Movimiento</div>
    <div class="card-body">
      <form @submit.prevent="submitForm">
        <div class="form-grid">

          <div class="form-group">
            <label>Código del Producto *</label>
            <AutocompleteInput
              v-model="form.codigo"
              placeholder="Buscar por código..."
              @select="onSelectProducto"
            />
            <span v-if="nombreProducto" class="producto-nombre">{{ nombreProducto }}</span>
          </div>

          <div class="form-group">
            <label for="fechaMov">Fecha *</label>
            <input id="fechaMov" v-model="form.fecha" type="date" required />
          </div>

          <div class="form-group">
            <label for="tipoMov">Tipo de Movimiento *</label>
            <select id="tipoMov" v-model="form.tipo" required>
              <option v-for="t in tiposMovimiento" :key="t.value" :value="t.value">
                {{ t.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="cantMov">Cantidad *</label>
            <input
              id="cantMov"
              v-model.number="form.cantidad"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="Cantidad"
              required
            />
          </div>

          <div class="form-group span-full">
            <label for="obsMov">Observaciones</label>
            <textarea
              id="obsMov"
              v-model="form.observaciones"
              placeholder="Observaciones opcionales"
              rows="3"
            />
          </div>
        </div>

        <div class="actions">
          <button type="submit" class="btn btn-success" :disabled="cargando">
            {{ cargando ? 'Guardando...' : '✔ Guardar Movimiento' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="limpiar">
            🗑 Limpiar
          </button>
        </div>
      </form>

      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />
    </div>
  </div>
</template>

<style scoped>
.producto-nombre {
  margin-top: 4px;
  font-size: 0.8rem;
  color: #2e86ab;
  font-weight: 600;
}
.span-full { grid-column: 1 / -1; }
</style>
