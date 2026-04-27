<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerStock, exportarStockCSV } from '@/api/inventario'
import type { ProductoStock, AppMessage as Msg } from '@/types'
import { activo } from '@/types'

const stock = ref([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const soloAlertas = ref(false)


const productos = [
    {
        "nombre": "Filtro de agua doméstico",
        "codigo": "HIDFIL1234",
        "descripcion": "Filtro para purificación de agua en hogares",
        "id_categoria": 1,
        "costo": 2500.50,
        "unidad_medida": "unidad",
        "stock_minimo": 10
    },
    {
        "nombre": "Tanque de almacenamiento 500L",
        "codigo": "HIDTAN5678",
        "descripcion": "Tanque plástico para almacenamiento de agua potable",
        "id_categoria": 2,
        "costo": 12000.00,
        "unidad_medida": "litros",
        "stock_minimo": 5
    },
    {
        "nombre": "Bomba sumergible",
        "codigo": "HIDBOM4321",
        "descripcion": "Bomba eléctrica para extracción de agua subterránea",
        "id_categoria": 3,
        "costo": 8500.75,
        "unidad_medida": "unidad",
        "stock_minimo": 3
    },
    {
        "nombre": "Manguera reforzada 20m",
        "codigo": "HIDMAN8765",
        "descripcion": "Manguera flexible para riego y conducción de agua",
        "id_categoria": 4,
        "costo": 3200.00,
        "unidad_medida": "metro",
        "stock_minimo": 15
    },
    {
        "nombre": "Purificador portátil",
        "codigo": "HIDPUR1357",
        "descripcion": "Dispositivo portátil para potabilizar agua en viajes",
        "id_categoria": 5,
        "costo": 1800.00,
        "unidad_medida": "unidad",
        "stock_minimo": 8
    },
    {
        "nombre": "Bidón de agua 20L",
        "codigo": "HIDBID2468",
        "descripcion": "Bidón plástico reutilizable para transporte de agua",
        "id_categoria": 6,
        "costo": 600.00,
        "unidad_medida": "litros",
        "stock_minimo": 20
    },
    {
        "nombre": "Regador manual",
        "codigo": "HIDREG9753",
        "descripcion": "Regador de mano para jardinería",
        "id_categoria": 7,
        "costo": 450.00,
        "unidad_medida": "unidad",
        "stock_minimo": 12
    },
    {
        "nombre": "Canilla metálica",
        "codigo": "HIDCAN8642",
        "descripcion": "Grifo metálico para instalaciones de agua",
        "id_categoria": 8,
        "costo": 750.00,
        "unidad_medida": "unidad",
        "stock_minimo": 25
    },
    {
        "nombre": "Kit de riego por goteo",
        "codigo": "HIDKIT7531",
        "descripcion": "Sistema completo de riego eficiente para huertas",
        "id_categoria": 9,
        "costo": 5400.00,
        "unidad_medida": "unidad",
        "stock_minimo": 6
    },
    {
        "nombre": "Medidor de caudal",
        "codigo": "HIDMED1597",
        "descripcion": "Instrumento para medir el flujo de agua",
        "id_categoria": 10,
        "costo": 2200.00,
        "unidad_medida": "unidad",
        "stock_minimo": 4
    }
]



const stockFiltrado = computed(() =>
  soloAlertas.value
    ? stock.value.filter(p => p.estado !== activo.NORMAL)
    : stock.value
)

function rowClass(p: ProductoStock): string {
  if (p.estado === activo.SIN_STOCK) return 'row-zero'
  if (p.estado === activo.BAJO) return 'row-low'
  return ''
}

onMounted(() => cargarStock())

async function cargarStock() {
  try {
    cargando.value = true
    msg.value = null
    stock.value = productos.map(p => ({
      ...p,
      cantidad: Math.floor(Math.random() * 20), // Simula stock actual
      estado: p.stock_minimo === 0 ? activo.NORMAL :
              (Math.floor(Math.random() * 20) < p.stock_minimo ? activo.SIN_STOCK :
              (Math.floor(Math.random() * 20) < p.stock_minimo * 2 ? activo.BAJO : activo.NORMAL))
    }))
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
              <th>Descripción</th>
              <th>Stock Mín.</th>
              <th>Stock Actual</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in stockFiltrado" :key="p.codigo" :class="rowClass(p)">
              <td>{{ p.codigo }}</td>
              <td>{{ p.nombre }}</td>
              <td>{{ p.unidad_medida }}</td>
              <td>{{ p.descripcion }}</td>
              <td>{{ p.stock_minimo }}</td>
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
