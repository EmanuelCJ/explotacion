<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerUsuarios } from '@/api/inventario'
import type { UsuarioData, AppMessage as Msg } from '@/types'

const usuarios = ref<UsuarioData[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)
const busqueda = ref('')

// ===============================
// CARGAR USUARIOS
// ===============================
onMounted(() => {
  mostrarUsuarios()
})

async function mostrarUsuarios() {
  try {
    cargando.value = true
    msg.value = null

    const response = await obtenerUsuarios()

    if ("usuarios" in response) {
      usuarios.value = response.usuarios   // 👈 array de usuarios
    } else {
      usuarios.value = []
      msg.value = { text: response.error ?? "Error desconocido", type: "error" }
    }

  } catch (error) {
    usuarios.value = []
    msg.value = { text: "Error al cargar usuarios.", type: "error" }
  } finally {
    cargando.value = false
  }
}

// ===============================
// FILTRO BUSQUEDA
// ===============================
const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u =>
    `${u.nombre} ${u.apellido} ${u.username} ${u.legajo}`
      .toLowerCase()
      .includes(busqueda.value.toLowerCase()))
})

// ===============================
// EDITAR (placeholder por ahora)
// ===============================
function editarUsuario(u: UsuarioData) {
  console.log('Editar usuario:', u)
  // después lo conectamos con FormCard
}
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

          <!-- HEADER -->
          <div class="user-header">
            <h3>{{ u.nombre }} {{ u.apellido }}</h3>

            <span class="badge" :class="u.activo ? 'activo' : 'inactivo'">
              {{ u.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </div>

          <!-- BODY -->
          <div class="user-body">
            <p><strong>Usuario:</strong> {{ u.username }}</p>
            <p><strong>Email:</strong> {{ u.email }}</p>
            <p><strong>Legajo:</strong> {{ u.legajo }}</p>
            <p><strong>Rol:</strong> {{ u.roles }}</p>
            <p><strong>Localidad:</strong> {{ u.localidad_nombre}}</p>
          </div>

          <!-- ACTIONS -->
          <div class="user-actions">
            <button class="btn-edit" @click="editarUsuario(u)">
              ✏️ Editar
            </button>
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
/* =========================
   GENERALES
========================= */
.loading,
.empty {
  text-align: center;
  padding: 24px;
  color: #6c757d;
  font-style: italic;
}

/* =========================
   ACCIONES
========================= */
.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.input-search {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
  flex: 1;
}

/* =========================
   GRID
========================= */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

/* =========================
   CARD
========================= */
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

/* =========================
   HEADER
========================= */
.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-header h3 {
  font-size: 16px;
}

/* =========================
   BODY
========================= */
.user-body p {
  margin: 4px 0;
  font-size: 14px;
}

/* =========================
   BADGE
========================= */
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

/* =========================
   ACTIONS
========================= */
.user-actions {
  margin-top: 10px;
  text-align: right;
}

.btn-edit {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-edit:hover {
  background: #0056b3;
}
</style>