<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { useInventarioStore } from '@/stores/inventario'
import { registrarProducto } from '@/api/inventario'
import type { NuevoProductoPayload, AppMessage as Msg } from '@/types'

const store = useInventarioStore()
const msg = ref<Msg | null>(null)
const cargando = ref(false)

const form = ref<NuevoProductoPayload>({
  codigo: '',
  nombre: '',
  unidad: '',
  grupo: '',
  stockMin: 0
})

const unidades = computed(() => store.listas.unidades)
const grupos = computed(() => store.listas.grupos)

onMounted(async () => {
  await store.cargarListas()
  if (unidades.value.length) form.value.unidad = unidades.value[0]
  if (grupos.value.length) form.value.grupo = grupos.value[0]
})

async function submitForm() {
  msg.value = null
  if (!form.value.codigo.trim() || !form.value.nombre.trim()) {
    msg.value = { text: 'Código y nombre son obligatorios.', type: 'warning' }
    return
  }
  try {
    cargando.value = true
    const respuesta = await registrarProducto(form.value)
    const esOk = respuesta.toLowerCase().includes('correctamente')
    msg.value = { text: respuesta, type: esOk ? 'success' : 'error' }
    if (esOk) limpiar()
  } catch (e) {
    msg.value = { text: 'Error al conectar con el servidor.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

function limpiar() {
  form.value = {
    codigo: '',
    nombre: '',
    unidad: unidades.value[0] ?? '',
    grupo: grupos.value[0] ?? '',
    stockMin: 0
  }
  msg.value = null
}
</script>

<template>
  <div class="card">
    <div class="card-header">📦 Registrar Nuevo Producto</div>
    <div class="card-body">

      <form @submit.prevent="submitForm">
        <div class="form-grid">
          <div class="form-group">
            <label for="codigo">Código *</label>
            <input
              id="codigo"
              v-model="form.codigo"
              type="text"
              placeholder="Código único del producto"
              required
            />
          </div>

          <div class="form-group">
            <label for="nombre">Nombre *</label>
            <input
              id="nombre"
              v-model="form.nombre"
              type="text"
              placeholder="Nombre del producto"
              required
            />
          </div>

          <div class="form-group">
            <label for="unidad">Unidad de Medida</label>
            <select id="unidad" v-model="form.unidad">
              <option v-for="u in unidades" :key="u" :value="u">{{ u }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="grupo">Grupo</label>
            <select id="grupo" v-model="form.grupo">
              <option v-for="g in grupos" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="stockMin">Stock Mínimo</label>
            <input
              id="stockMin"
              v-model.number="form.stockMin"
              type="number"
              min="0"
            />
          </div>
        </div>

        <div class="actions">
          <button type="submit" class="btn btn-success" :disabled="cargando">
            {{ cargando ? 'Guardando...' : '✔ Registrar Producto' }}
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
