<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerStock, exportarStockCSV, actualizarProducto } from '@/api/inventario'
import type { Producto, AppMessage as Msg } from '@/types'
import { activo_producto } from '@/types'
import { useUsuarioStore } from '@/stores/UsuarioStore'

const data = ref<{ stock: Producto[] }>({ stock: [] })
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const soloAlertas = ref(false)
const productoSeleccionado = ref<Producto | null>(null)
let productoOriginal: Producto | null = null // Para comparar cambios

const usuarioStore = useUsuarioStore()
const usuario = computed(() => usuarioStore.usuario)

function rowClass(p: Producto): string {
  if (p.activo === activo_producto.Activo) return 'row-normal'
  if (p.activo === activo_producto.NoActivo) return 'row-zero'
  return ''
}

function seleccionarParaEditar(p: Producto) {
  // Guardamos una copia limpia para comparar después
  productoOriginal = JSON.parse(JSON.stringify(p))
  // Clonamos para la edición reactiva
  productoSeleccionado.value = JSON.parse(JSON.stringify(p))
}

// info del usuario al montar el componente
onMounted(() => {
  usuarioStore.fetchUsuario()
})

// carga los datos al montar la vista
onMounted(() => cargarStock())

async function cargarStock() {
  try {
    cargando.value = true
    msg.value = null
    const respuesta = await obtenerStock()
    data.value = respuesta
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

// Función para guardar (esto llamaría API para actualizar el producto)
async function guardarCambios() {
  if (!productoSeleccionado.value || !productoOriginal) return

  // 1. Confirmación
  const confirmar = confirm(`¿Estás seguro de que deseas actualizar el producto "${productoOriginal.nombre}"?`)
  if (!confirmar) return

  // 2. Identificar solo lo que cambió
  const cambios: Partial<Producto> = {
    id_producto: productoSeleccionado.value.id_producto // El ID siempre es necesario
  }

  let hayCambios = false
  
  //estos son los campos posibles para editar
  const camposAEditar = ['nombre', 'descripcion', 'id_categoria', 'costo', 'unidad_medida', 'stock_minimo', 'activo'] as const

  camposAEditar.forEach(campo => {
    if (productoSeleccionado.value![campo] !== productoOriginal![campo]) {
      cambios[campo] = productoSeleccionado.value![campo] as any
      hayCambios = true
    }
  })
  if (!hayCambios) {
    msg.value = { text: 'No se detectaron cambios para guardar.', type: 'info' }
    productoSeleccionado.value = null
    return
  }

  try {
    cargando.value = true
    // Enviamos solo el objeto con los cambios (dentro del array que pide tu API)
    await actualizarProducto(cambios.id_producto!, cambios)

    msg.value = { text: 'Producto actualizado con éxito', type: 'success' }

    productoSeleccionado.value = null

    await cargarStock()
  } catch (error) {
    msg.value = { text: 'Error al actualizar el producto.', type: 'error' }
  } finally {
    cargando.value = false
  }
}


</script>

<template>
  <div class="card">
    <div class="card-header">🗃️ Stock Actual - localidad {{ usuario?.localidad_nombre }} </div>
    <div class="card-body">
      <div class="actions">
        <button class="btn btn-primary" :disabled="cargando" @click="cargarStock">
          {{ cargando ? 'Cargando...' : '🔄 Actualizar' }}
        </button>
        <button class="btn btn-success" @click="exportar">
          📥 Exportar CSV
        </button>
        <button class="btn" :class="soloAlertas ? 'btn-warning' : 'btn-secondary'" @click="soloAlertas = !soloAlertas">
          {{ soloAlertas ? '📋 Mostrar Todo' : '⚠️ Solo Alertas' }}
        </button>

      </div>

      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <p v-if="cargando" class="loading">Cargando inventario...</p>

      <div v-else-if="data.stock.length > 0" class="table-container">
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>categoria</th>
              <th>Unidad</th>
              <th>Ubicación</th>
              <th>Stock Minimo</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in data.stock" :key="p.codigo" :class="rowClass(p)">
              <td>{{ p.codigo }}</td>
              <td>{{ p.nombre }}</td>
              <td>{{ p.nombre_categoria }}</td>
              <td>{{ p.unidad_medida }}</td>
              <td>{{ p.descripcion_lugar }}</td>
              <td>{{ p.stock_minimo }}</td>
              <td>{{ p.activo ? 'Activo' : 'Inactivo' }}</td>
              <td>
                <button class="btn-edit" @click="seleccionarParaEditar(p)">
                  ✏️ Editar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!cargando" class="empty">
        {{ soloAlertas ? 'No hay alertas de stock activas.' : 'No hay productos registrados.' }}
      </div>
      
      <div v-if="productoSeleccionado" class="edit-overlay">
        <div class="edit-card">
          <h3>Editar Producto: {{ productoSeleccionado.nombre }}</h3>

          <div class="grid-form">
            <div class="form-group">
              <label>Nombre:</label>
              <input v-model="productoSeleccionado.nombre" type="text" />
            </div>

            <div class="form-group">
              <label>Costo:</label>
              <input v-model.number="productoSeleccionado.costo" type="number" step="0.01" />
            </div>

            <div class="form-group">
              <label>Stock Mínimo:</label>
              <input v-model.number="productoSeleccionado.stock_minimo" type="number" />
            </div>

            <div class="form-group">
              <label>Unidad:</label>
              <input v-model="productoSeleccionado.unidad_medida" type="text" />
            </div>

            <div class="form-group">
              <label>Ubicación (Descripción):</label>
              <input v-model="productoSeleccionado.descripcion" type="text" />
            </div>

            <div class="form-group">
              <label>Estado:</label>
              <select v-model="productoSeleccionado.activo">
                <option :value="activo_producto.Activo">Activo</option>
                <option :value="activo_producto.NoActivo">Inactivo</option>
              </select>
            </div>
          </div>

          <div class="edit-actions">
            <button class="btn btn-success" :disabled="cargando" @click="guardarCambios">
              {{ cargando ? 'Guardando...' : '✅ Confirmar Cambios' }}
            </button>
            <button class="btn btn-secondary" @click="productoSeleccionado = null">
              ❌ Cancelar
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Algunas propiedades de estilo estan en el main.css */

.loading,
.empty {
  text-align: center;
  padding: 24px;
  color: #6c757d;
  font-style: italic;
}

.btn-edit {
  background: #007bff;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.edit-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.edit-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  min-width: 300px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.edit-actions {
  display: flex;
  gap: 10px;
  margin-top: 1.5rem;
}
</style>
