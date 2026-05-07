<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerUsuarios, updateUsuario, obtenerLocalidades, obtenerRoles } from '@/api/inventario'
import type { UsuarioData, usuariomodel as usuarioModelCreate, AppMessage as Msg, localidad, roles } from '@/types'


const usuarios = ref<UsuarioData[]>([])
const msg = ref<Msg | null>(null)
const cargando = ref(false)

const busqueda = ref('')
const localidades = ref<localidad[]>([])
const roles = ref<roles[]>([])

const usuarioSeleccionado = ref<UsuarioData | null>(null)
let usuarioOriginal: UsuarioData | null = null

  
const nuevoUsuario = ref<usuarioModelCreate | null>(null)


// ===============================
// CARGAR USUARIOS y TRAE LOCALIDADES
// ===============================
onMounted(() => {
  mostrarUsuarios()
  cargarLocalidades()
  cargarRoles()
})

async function mostrarUsuarios() {
  try {
    cargando.value = true
    msg.value = null

    const response = await obtenerUsuarios()

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

async function crearNuevoUsuario() {

  //Para cuando hace click para desplegar el formulario

}

async function cargarLocalidades() {
  try {
    const response = await obtenerLocalidades()

    if (Array.isArray(response)) {
      localidades.value = response
    } else {
      console.error(response.error)
      localidades.value = [] // evita que quede undefined
    }
  } catch {
    msg.value = { text: 'Error al cargar localidades', type: 'error' }
    localidades.value = []
  }
}

async function cargarRoles() {
  try {
    const response = await obtenerRoles()

    if (Array.isArray(response)) {
      roles.value = response
    } else {
      console.error(response.error)
      roles.value = [] // evita que quede undefined
    }
  } catch {
    msg.value = { text: 'Error al cargar roles', type: 'error' }
    roles.value = []
  }
}


// ===============================
// EDITAR USUARIO
// ===============================
function editarUsuario(u: UsuarioData) {
  usuarioOriginal = JSON.parse(JSON.stringify(u))
  usuarioSeleccionado.value = JSON.parse(JSON.stringify(u))
}

// ===============================
// GUARDAR CAMBIOS
// ===============================
async function guardarCambios() {
  if (!usuarioSeleccionado.value || !usuarioOriginal) return

  const confirmar = confirm(
    `¿Actualizar usuario "${usuarioOriginal.nombre}"?`
  )
  if (!confirmar) return

  const cambios: Partial<UsuarioData> = {}

  let hayCambios = false

  // Son los campos posible habilitados por el backend
  const camposAEditar = [
    'nombre',
    'apellido',
    'username',
    'email',
    'legajo',
    'id_localidad',
    'id_rol'
  ] as const

  camposAEditar.forEach(campo => {
    if (usuarioSeleccionado.value![campo] !== usuarioOriginal![campo]) {
      cambios[campo] = usuarioSeleccionado.value![campo] as any
      hayCambios = true
    }
  })

  if (!hayCambios) {
    msg.value = { text: 'No se detectaron cambios.', type: 'info' }
    usuarioSeleccionado.value = null
    return
  }

  try {
    cargando.value = true

    await updateUsuario(usuarioSeleccionado.value.id_usuario, cambios)

    msg.value = { text: 'Usuario actualizado correctamente.', type: 'success' }

    usuarioSeleccionado.value = null
    await mostrarUsuarios()

  } catch {
    msg.value = { text: 'Error al actualizar usuario.', type: 'error' }
  } finally {
    cargando.value = false
  }
}

// ===============================
// GUARDAR CAMBIOS
// ===============================
async function crearUsuario() {
  if (!usuarioSeleccionado.value || !usuarioOriginal) return

  const confirmar = confirm(
    `¿Actualizar usuario "${usuarioOriginal.nombre}"?`
  )
  if (!confirmar) return

  const cambios: Partial<UsuarioData> = {}

  let hayCambios = false

  // Son los campos posible habilitados por el backend
  const camposAEditar = [
    'nombre',
    'apellido',
    'username',
    'email',
    'legajo',
    'id_localidad',
    'id_rol'
  ] as const

  camposAEditar.forEach(campo => {
    if (usuarioSeleccionado.value![campo] !== usuarioOriginal![campo]) {
      cambios[campo] = usuarioSeleccionado.value![campo] as any
      hayCambios = true
    }
  })

  if (!hayCambios) {
    msg.value = { text: 'No se detectaron cambios.', type: 'info' }
    usuarioSeleccionado.value = null
    return
  }

  try {
    cargando.value = true

    await updateUsuario(usuarioSeleccionado.value.id_usuario, cambios)

    msg.value = { text: 'Usuario actualizado correctamente.', type: 'success' }

    usuarioSeleccionado.value = null
    await mostrarUsuarios()

  } catch {
    msg.value = { text: 'Error al actualizar usuario.', type: 'error' }
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
        <!-- <RoleGuard :roles="['admin']"> -->
        <button class="btn btn-primary" @click="crearNuevoUsuario" :disabled="cargando">
          {{ cargando ? 'Cargando...' : '👥 Crear Usuario' }}
        </button>
        <!-- </RoleGuard> -->

        <button class="btn btn-primary" @click="mostrarUsuarios" :disabled="cargando">
          {{ cargando ? 'Cargando...' : '🔄 Actualizar' }}
        </button>

        <input v-model="busqueda" type="text" placeholder="🔍 Buscar usuario..." class="input-search" />
      </div>

      <!-- MENSAJES -->
      <AppMessage v-if="msg" :text="msg.text" :type="msg.type" />

      <!-- Este form es para editar un usuario -->
      <div v-if="usuarioSeleccionado" class="edit-overlay">
        <div class="edit-card">
          <h3>Editar Usuario: {{ usuarioSeleccionado.nombre }}</h3>

          <div class="grid-form">

            <div class="form-group">
              <label>Nombre:</label>
              <input v-model="usuarioSeleccionado.nombre" type="text" />
            </div>

            <div class="form-group">
              <label>Apellido:</label>
              <input v-model="usuarioSeleccionado.apellido" type="text" />
            </div>

            <div class="form-group">
              <label>Username:</label>
              <input v-model="usuarioSeleccionado.username" type="text" />
            </div>

            <div class="form-group">
              <label>Email:</label>
              <input v-model="usuarioSeleccionado.email" type="email" />
            </div>

            <div class="form-group">
              <label>Legajo:</label>
              <input v-model.number="usuarioSeleccionado.legajo" type="number" />
            </div>

            <div class="form-group">
              <label>Localidad: {{ usuarioSeleccionado.localidad_nombre }}</label>
              <select v-model="usuarioSeleccionado.id_localidad">
                <option disabled value="">Seleccione una localidad</option>
                <option v-for="loc in localidades" :key="loc.id_localidad" :value="loc.id_localidad">
                  {{ loc.nombre }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Estado:</label>
              <select v-model="usuarioSeleccionado.activo">
                <option :value="1">Activo</option>
                <option :value="0">Inactivo</option>
              </select>
            </div>

          </div>

          <div class="edit-actions">
            <button class="btn btn-success" :disabled="cargando" @click="guardarCambios">
              {{ cargando ? 'Guardando...' : '✅ Confirmar Cambios' }}
            </button>

            <button class="btn btn-secondary" @click="usuarioSeleccionado = null">
              ❌ Cancelar
            </button>
          </div>
        </div>
      </div>

      <!-- este form es para crear un nuevo usuario -->

      <div v-if="nuevoUsuario" class="edit-overlay">
        <div class="edit-card">
          <h3>Crear Nuevo Usuario</h3>

          <div class="grid-form">
            <div class="form-group">
              <label>Nombre:</label>
              <input v-model="nuevoUsuario.nombre" type="text" />
            </div>

            <div class="form-group">
              <label>Apellido:</label>
              <input v-model.number="nuevoUsuario.apellido" type="text" />
            </div>

            <div class="form-group">
              <label>Username:</label>
              <input v-model.number="nuevoUsuario.username" type="text" />
            </div>

            <div class="form-group">
              <label>Legajo:</label>
              <input v-model.number="nuevoUsuario.legajo" type="number" />
            </div>

            <div class="form-group">
              <label>Email:</label>
              <input v-model.number="nuevoUsuario.email" type="text" />
            </div>

            <div class="form-group">
              <label>Localidad: </label>
              <select v-model="nuevoUsuario.id_localidad">
                <option disabled value="">Seleccione una localidad</option>
                <option v-for="loc in localidades" :key="loc.id_localidad" :value="loc.id_localidad">
                  {{ loc.nombre }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Rol: </label>
              <select v-model="nuevoUsuario.id_rol">
                <option disabled value="">Seleccione un ROL</option>
                <option v-for="loc in roles" :key="loc.id_rol" :value="loc.id_rol">
                  {{ loc.nombre }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Password:</label>
              <input v-model="nuevoUsuario.password" type="text" />
            </div>

          </div>

          <div class="edit-actions">
            <button class="btn btn-success" :disabled="cargando" @click="crearUsuario">
              {{ cargando ? 'Guardando...' : '✅ Confirmar Cambios' }}
            </button>
            <button class="btn btn-secondary" @click="nuevoUsuario = null">
              ❌ Cancelar
            </button>
          </div>
        </div>
      </div>

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
</style>