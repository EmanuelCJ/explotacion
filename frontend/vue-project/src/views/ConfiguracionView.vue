<script setup lang="ts">
import { ref } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { inicializarSistema, validarIntegridad } from '@/api/inventario'
import { useInventarioStore } from '@/stores/inventario'
import type { AppMessage as Msg } from '@/types'

const store = useInventarioStore()
const msg = ref<Msg | null>(null)
const errores = ref<string[]>([])
const cargando = ref(false)

async function inicializar() {
  if (!confirm('¿Inicializar el sistema? Se crearán las estructuras necesarias si no existen.')) return
  try {
    cargando.value = true
    msg.value = null
    const respuesta = await inicializarSistema()
    const esOk = respuesta.toLowerCase().includes('correctamente')
    msg.value = { text: respuesta, type: esOk ? 'success' : 'error' }
    if (esOk) {
      // Forzar recarga de listas y resumen tras inicializar
      store.listas.unidades = []
      await store.cargarListas()
      await store.cargarResumen()
    }
  } catch {
    msg.value = { text: 'Error al conectar con el servidor.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

async function validar() {
  try {
    cargando.value = true
    msg.value = null
    errores.value = []
    const resultado = await validarIntegridad()
    errores.value = resultado.errores
    if (errores.value.length === 0) {
      msg.value = { text: 'Todos los datos están correctos. El sistema está íntegro.', type: 'success' }
    }
  } catch {
    msg.value = { text: 'Error al validar integridad.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

function confirmarReset() {
  if (confirm('⚠️ ADVERTENCIA: Esta acción eliminará TODOS los datos del sistema.\n¿Está completamente seguro?')) {
    if (confirm('Esta es su última oportunidad para cancelar.\n¿Proceder con el reset completo?')) {
      msg.value = { text: 'Funcionalidad de reset no implementada por seguridad. Contacte al administrador.', type: 'warning' }
    }
  }
}
</script>

<template>
  <div class="card">
    <div class="card-header">⚙️ Herramientas de Administración</div>
    <div class="card-body">

      <div class="actions">
        <button class="btn btn-info" :disabled="cargando" @click="validar">
          🔍 Validar Integridad
        </button>
        <button class="btn btn-success" :disabled="cargando" @click="inicializar">
          🚀 Inicializar Sistema
        </button>
        <button class="btn btn-danger" @click="confirmarReset">
          🗑 Reset Sistema
        </button>
      </div>

      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <div v-if="errores.length > 0" class="errores-card">
        <h4 class="errores-titulo">Se encontraron {{ errores.length }} error(es):</h4>
        <ul class="errores-lista">
          <li v-for="(err, i) in errores" :key="i" class="text-danger">{{ err }}</li>
        </ul>
      </div>

    </div>
  </div>
</template>

<style scoped>
.errores-card {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}
.errores-titulo {
  color: #856404;
  margin-bottom: 10px;
  font-size: 0.95rem;
}
.errores-lista {
  padding-left: 20px;
  list-style: disc;
}
.errores-lista li {
  margin-bottom: 4px;
  font-size: 0.875rem;
}
</style>
