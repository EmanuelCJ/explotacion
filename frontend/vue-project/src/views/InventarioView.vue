<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerStock, exportarStockCSV , actualizarProducto} from '@/api/inventario'
import type { Producto, AppMessage as Msg } from '@/types'
import { activo_producto } from '@/types'

const data = ref<{ stock: Producto[] }>({ stock: [] })
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const soloAlertas = ref(false)
const productoSeleccionado = ref<Producto | null>(null)


function rowClass(p: Producto): string {
  if (p.activo === activo_producto.Activo) return 'row-normal'
  if (p.activo === activo_producto.NoActivo) return 'row-zero'
  return ''
}

// Función para seleccionar
function seleccionarParaEditar(p: Producto) {
  // Clonamos el objeto para no editar directamente la fila de la tabla 
  // hasta que confirmemos los cambios
  productoSeleccionado.value = { ...p }
  console.log('Editando producto:', productoSeleccionado.value)
}

onMounted(() => cargarStock())

async function cargarStock() {
  try {
    cargando.value = true
    msg.value = null
    const respuesta = await obtenerStock()
    data.value = respuesta
    console.log('Stock actual:', data.value)
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
  if (!productoSeleccionado.value) return

  try {
    cargando.value = true
    await actualizarProducto(productoSeleccionado.value)
    msg.value = { text: 'Producto actualizado con éxito', type: 'success' }
    productoSeleccionado.value = null // Cerramos el formulario
    await cargarStock() // Refrescamos la lista
  } catch {
    msg.value = { text: 'Error al actualizar', type: 'error' }
  } finally {
    cargando.value = false
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
              <th>ID</th>
              <th>Código</th>
              <th>Nombre</th>
              <th>Unidad</th>
              <th>Ubicación</th>
              <th>Stock Actual</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in data.stock" :key="p.codigo" :class="rowClass(p)">
              <td>{{ p.id_producto }}</td>
              <td>{{ p.codigo }}</td>
              <td>{{ p.nombre }}</td>
              <td>{{ p.unidad_medida }}</td>
              <td>{{ p.descripcion }}</td>
              <td>{{ p.stock }}</td>
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

          <div class="form-group">
            <label>Nombre:</label>
            <input v-model="productoSeleccionado.nombre" type="text" />
          </div>
          <div class="form-group">
            <label>Unidad de Medida:</label>
            <input v-model="productoSeleccionado.unidad_medida" type="text" />
          </div>
          <div class="form-group">
            <label>Ubicación:</label>
            <input v-model="productoSeleccionado.descripcion" type="text" />
          </div>
          <div class="form-group">
            <label>Stock Actual:</label>
            <input v-model="productoSeleccionado.stock" type="number" />
          </div>

          <div class="form-group">
            <label>Estado:</label>
            <select v-model="productoSeleccionado.activo">
              <option :value="activo_producto.Activo">Activo</option>
              <option :value="activo_producto.NoActivo">Inactivo</option>
            </select>
          </div>

          <div class="edit-actions">
            <button class="btn btn-success" @click="guardarCambios">Guardar</button>
            <button class="btn btn-secondary" @click="productoSeleccionado = null">Cancelar</button>
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
