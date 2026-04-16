import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Listas, Resumen } from '@/types'
import { obtenerListas, obtenerResumen } from '@/api/inventario'

export const useInventarioStore = defineStore('inventario', () => {
  // ─── State ──────────────────────────────────────────────────────────────────
  const listas = ref<Listas>({ unidades: [], grupos: [] })
  const resumen = ref<Resumen>({
    totalProductos: 0,
    totalMovimientos: 0,
    sinStock: 0,
    stockBajo: 0,
    valorTotalInventario: 0,
    movimientosUltimoMes: 0
  })
  const cargandoListas = ref(false)
  const cargandoResumen = ref(false)

  // ─── Actions ─────────────────────────────────────────────────────────────────
  async function cargarListas() {
    if (listas.value.unidades.length > 0) return
    try {
      cargandoListas.value = true
      listas.value = await obtenerListas()
    } finally {
      cargandoListas.value = false
    }
  }

  async function cargarResumen() {
    try {
      cargandoResumen.value = true
      resumen.value = await obtenerResumen()
    } finally {
      cargandoResumen.value = false
    }
  }

  return { listas, resumen, cargandoListas, cargandoResumen, cargarListas, cargarResumen }
})
