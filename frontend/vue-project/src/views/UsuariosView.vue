<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerUsuariosPorLocalidad } from '@/api/inventario'
import type { UsuarioData, AppMessage as Msg, roles } from '@/types'


const usuarios = ref<UsuarioData[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const busqueda = ref('')
const roles = ref<roles[]>([])


// ===============================
// CARGAR USUARIOS, TRAE LOCALIDADES y Cargar Roles
// ===============================
onMounted(() => {
  mostrarUsuarios()
})

async function mostrarUsuarios() {
  try {
    cargando.value = true
    msg.value = null

    const response = await obtenerUsuariosPorLocalidad()

    if ('usuarios' in response) {
      usuarios.value = response.usuarios
    } else {
      usuarios.value = []
      msg.value = { text: response.error ?? 'Error desconocido', type: 'error' }
    }

  } catch {
    usuarios.value = []
    msg.value = { text: 'Error al cargar usuarios.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

// ===============================
// FILTRO
// ===============================
const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u =>
    `${u.nombre} ${u.apellido} ${u.username} ${u.legajo} ${u.localidad_nombre}`
      .toLowerCase()
      .includes(busqueda.value.toLowerCase())
  )
})

</script>

<template>
  <div class="card">
    <div class="card-header">
      👥 Gestión de Usuarios
    </div>

    <div class="card-body">

      <!-- ACCIONES -->
      <div class="actions">
        <button class="btn btn-primary" @click="mostrarUsuarios" :disabled="cargando">
          {{ cargando ? 'Cargando...' : '🔄 Actualizar' }}
        </button>
        <input v-model="busqueda" type="text" placeholder="🔍 Buscar usuario..." class="input-search" />
      </div>

      <!-- MENSAJES -->
      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <!-- LOADING -->
      <p v-if="cargando" class="loading">
        Cargando usuarios...
      </p>

      <!-- GRID -->
      <div v-else-if="usuariosFiltrados.length > 0" class="card-grid">
        <div v-for="u in usuariosFiltrados" :key="u.id_usuario" class="user-card">

          <div class="user-header">
            <h3>{{ u.nombre }} {{ u.apellido }}</h3>

            <span class="badge" :class="u.activo ? 'activo' : 'inactivo'">
              {{ u.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </div>

          <div class="user-body">
            <p><strong>Usuario: </strong> {{ u.username }}</p>
            <p><strong>Email: </strong> {{ u.email }}</p>
            <p><strong>Legajo: </strong> {{ u.legajo }}</p>
            <p><strong>Rol: </strong> {{ u.rol }}</p>
            <p><strong>Localidad: </strong> {{ u.localidad_nombre }}</p>
          </div>
        </div>
      </div>

      <!-- EMPTY -->
      <div v-else class="empty">
        No hay usuarios registrados.
      </div>

    </div>
  </div>
</template>

<style scoped>
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

.btn-role {
  background: #6f42c1;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-password {
  background: #fd7e14;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.user-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  justify-content: flex-end;
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

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.user-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: 0.2s;
}

.user-card:hover {
  transform: translateY(-3px);
}

.user-header {
  display: flex;
  justify-content: space-between;
}

.user-body p {
  margin: 4px 0;
  font-size: 14px;
}

.badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  color: white;
}

.badge.activo {
  background: #28a745;
}

.badge.inactivo {
  background: #dc3545;
}

.user-actions {
  margin-top: 10px;
  text-align: right;
}

.edit-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  min-width: 320px;
  max-width: 400px;
  width: 100%;
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
  justify-content: flex-end;
}

/* ─── Error ──────────────────────────────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(239, 68, 68, 0.25);
  border: 1px solid rgba(252, 165, 165, 0.5);
  border-radius: 10px;
  padding: 10px 13px;
  margin: 15px 0px;
  font-size: clamp(0.78rem, 1.8vw, 0.84rem);
  color: black !important;
  line-height: 1.45;
  word-break: break-word;
}

.error-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  margin-top: 2px;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.input-error {
  border: 1px solid #dc3545 !important;
  background: #fff5f5;
}
</style>