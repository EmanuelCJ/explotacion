<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppMessage from '@/components/AppMessage.vue'
import { obtenerUsuarios, updateUsuario, obtenerLocalidades, obtenerRoles, crearUsuarios, rolAsignar as RolAsignar, rolQuitar, newPassword } from '@/api/inventario'
import type { UsuarioData, Usuario_Model, AppMessage as Msg, localidad, roles } from '@/types'
import RoleGuard from '@/components/RoleGuard.vue'

const usuarios = ref<UsuarioData[]>([])
const msg = ref<Msg | null>(null)
const errorMsg = ref('')
const cargando = ref(false)
const crear_cargando = ref(false)


const busqueda = ref('')
const localidades = ref<localidad[]>([])
const roles = ref<roles[]>([])

const usuarioSeleccionado = ref<UsuarioData | null>(null)
let usuarioOriginal: UsuarioData | null = null


const nuevoUsuario = ref<Usuario_Model | null>(null)

// ===============================
// GESTION ROL
// ===============================

const usuarioRolSeleccionado = ref<UsuarioData | null>(null)
const nuevoRolId = ref<number>(0)

// ===============================
// CAMBIAR PASSWORD
// ===============================

const usuarioPasswordSeleccionado = ref<UsuarioData | null>(null)
const nuevaPassword = ref('')


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

function abrirCrearUsuario() {
  nuevoUsuario.value = {
    nombre: '',
    apellido: '',
    username: '',
    email: '',
    legajo: 0,
    password: '',
    id_localidad: 0,
    id_rol: 0,
    activo: 1
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
// CREAR USUARIO
// ===============================
// 
async function crearUsuario() {

  if (!nuevoUsuario.value) return

  errorMsg.value = ''

  // =========================
  // VALIDACIONES
  // =========================

  if (!nuevoUsuario.value.nombre.trim()) {
    errorMsg.value = 'El nombre es obligatorio'
    return
  }

  if (!nuevoUsuario.value.apellido.trim()) {
    errorMsg.value = 'El apellido es obligatorio'
    return
  }

  if (!nuevoUsuario.value.username.trim()) {
    errorMsg.value = 'El username es obligatorio'
    return
  }

  if (!nuevoUsuario.value.email.trim()) {
    errorMsg.value = 'El email es obligatorio'
    return
  }

  // Validación email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!emailRegex.test(nuevoUsuario.value.email)) {
    errorMsg.value = 'El formato del email es inválido'
    return
  }

  if (!nuevoUsuario.value.password.trim()) {
    errorMsg.value = 'La contraseña es obligatoria'
    return
  }

  if (nuevoUsuario.value.password.length < 6) {
    errorMsg.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }

  if (!nuevoUsuario.value.legajo || nuevoUsuario.value.legajo <= 0) {
    errorMsg.value = 'El legajo es obligatorio'
    return
  }

  if (!nuevoUsuario.value.id_localidad || nuevoUsuario.value.id_localidad <= 0) {
    errorMsg.value = 'Debe seleccionar una localidad'
    return
  }

  if (!nuevoUsuario.value.id_rol || nuevoUsuario.value.id_rol <= 0) {
    errorMsg.value = 'Debe seleccionar un rol'
    return
  }

  // =========================
  // CONFIRMAR
  // =========================

  const confirmar = confirm(
    '¿Confirmar desea crear usuario?'
  )

  if (!confirmar) return

  const data: Usuario_Model = {
    nombre: nuevoUsuario.value.nombre.trim(),
    apellido: nuevoUsuario.value.apellido.trim(),
    username: nuevoUsuario.value.username.trim(),
    email: nuevoUsuario.value.email.trim(),
    legajo: nuevoUsuario.value.legajo,
    password: nuevoUsuario.value.password.trim(),
    id_localidad: nuevoUsuario.value.id_localidad,
    id_rol: nuevoUsuario.value.id_rol,
  }

  try {

    crear_cargando.value = true

    const response = await crearUsuarios(data)

    if (response) {

      msg.value = {
        text: 'Usuario creado correctamente.',
        type: 'success'
      }

      nuevoUsuario.value = null

      await mostrarUsuarios()
    }

  } catch (err: any) {

    const serverError = err.response?.data?.detail

    errorMsg.value = serverError || 'Error inesperado'

  } finally {

    crear_cargando.value = false

  }
}

// ===============================
// ABRIR MODAL ROL
// ===============================

function abrirAsignarRol(usuario: UsuarioData) {

  usuarioRolSeleccionado.value = usuario

  nuevoRolId.value = usuario.id_rol || 0
}

// ===============================
// ASIGNAR / CAMBIAR ROL
// ===============================

async function asignarRol() {

  if (!usuarioRolSeleccionado.value) return

  if (!nuevoRolId.value) {

    errorMsg.value = 'Debe seleccionar un rol'

    return
  }

  try {

    cargando.value = true

    const response = await RolAsignar({usuario_id:usuarioRolSeleccionado.value.id_usuario,rol_id: nuevoRolId.value})

    if (!response) {
      throw new Error()
    }

    msg.value = {
      text: 'Rol actualizado correctamente.',
      type: 'success'
    }

    usuarioRolSeleccionado.value = null

    await mostrarUsuarios()

  } catch {

    msg.value = {
      text: 'Error al actualizar rol.',
      type: 'error'
    }

  } finally {

    cargando.value = false
  }
}

// ===============================
// QUITAR ROL
// ===============================

async function quitarRol() {

  if (!usuarioRolSeleccionado.value) return

  const confirmar = confirm(
    `¿Quitar rol a ${usuarioRolSeleccionado.value.nombre}?`
  )

  if (!confirmar) return

  try {

    cargando.value = true

    const response = await rolQuitar({usuario_id: usuarioRolSeleccionado.value.id_usuario})

    if (!response) {
      throw new Error()
    }

    msg.value = {
      text: 'Rol eliminado correctamente.',
      type: 'success'
    }

    usuarioRolSeleccionado.value = null

    await mostrarUsuarios()

  } catch {

    msg.value = {
      text: 'Error al quitar rol.',
      type: 'error'
    }

  } finally {

    cargando.value = false
  }
}

// ===============================
// ABRIR MODAL PASSWORD
// ===============================

function abrirCambiarPassword(usuario: UsuarioData) {

  usuarioPasswordSeleccionado.value = usuario

  nuevaPassword.value = ''
}

// ===============================
// CAMBIAR PASSWORD
// ===============================

async function cambiarPassword() {

  if (!usuarioPasswordSeleccionado.value) return

  errorMsg.value = ''

  if (!nuevaPassword.value.trim()) {

    errorMsg.value = 'La contraseña es obligatoria'

    return
  }

  if (nuevaPassword.value.length < 6) {

    errorMsg.value = 'La contraseña debe tener al menos 6 caracteres'

    return
  }

  try {

    cargando.value = true

    const response = await newPassword({usuario_id:usuarioPasswordSeleccionado.value.id_usuario,new_password: nuevaPassword.value}) 
      
    

    if (!response) {
      throw new Error()
    }

    msg.value = {
      text: 'Password actualizada correctamente.',
      type: 'success'
    }

    usuarioPasswordSeleccionado.value = null

  } catch {

    msg.value = {
      text: 'Error al cambiar password.',
      type: 'error'
    }

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
        <RoleGuard :roles="['admin']">
          <button class="btn btn-primary" @click="abrirCrearUsuario" :disabled="crear_cargando">
            {{ crear_cargando ? 'Cargando...' : '👥 Crear Usuario' }}
          </button>
        </RoleGuard>

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
            <transition name="fade-slide">
              <div v-if="errorMsg" class="error-banner" role="alert">
                <svg viewBox="0 0 20 20" fill="currentColor" class="error-icon" aria-hidden="true">
                  <path fill-rule="evenodd"
                    d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clip-rule="evenodd" />
                </svg>
                <span>{{ errorMsg }}</span>
              </div>
            </transition>
          </div>

          <div class="form-group">
            <label>Nombre:</label>

            <input v-model="nuevoUsuario.nombre" type="text" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.nombre }" />
          </div>

          <div class="form-group">
            <label>Apellido:</label>

            <input v-model="nuevoUsuario.apellido" type="text" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.apellido }" />
          </div>

          <div class="form-group">
            <label>Username:</label>

            <input v-model="nuevoUsuario.username" type="text" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.username }" />
          </div>

          <div class="form-group">
            <label>Legajo:</label>

            <input v-model.number="nuevoUsuario.legajo" type="number" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.legajo }" />
          </div>

          <div class="form-group">
            <label>Email:</label>

            <input v-model="nuevoUsuario.email" type="email" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.email }" />
          </div>

          <div class="form-group">
            <label>Localidad:</label>

            <select v-model.number="nuevoUsuario.id_localidad" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.id_localidad }">
              <option disabled :value="0">
                Seleccione una localidad
              </option>

              <option v-for="loc in localidades" :key="loc.id_localidad" :value="loc.id_localidad">
                {{ loc.nombre }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Rol:</label>

            <select v-model.number="nuevoUsuario.id_rol" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.id_rol }">
              <option disabled :value="0">
                Seleccione un ROL
              </option>

              <option v-for="loc in roles" :key="loc.id_rol" :value="loc.id_rol">
                {{ loc.descripcion }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Password:</label>

            <input v-model="nuevoUsuario.password" type="password" required
              :class="{ 'input-error': errorMsg && !nuevoUsuario.password }" />
          </div>

          <div class="edit-actions">
            <button class="btn btn-success" :disabled="crear_cargando" @click="crearUsuario">
              {{ crear_cargando ? 'Guardando...' : '✅ Confirmar Cambios' }}
            </button>
            <button class="btn btn-secondary" @click="nuevoUsuario = null">
              ❌ Cancelar
            </button>
          </div>
        </div>
      </div>

      <div v-if="usuarioRolSeleccionado" class="edit-overlay">

        <div class="edit-card">

          <h3>
            Gestionar Rol:
            {{ usuarioRolSeleccionado.nombre }}
          </h3>

          <div class="form-group">

            <label>Rol:</label>

            <select v-model.number="nuevoRolId">

              <option disabled :value="0">
                Seleccione un rol
              </option>

              <option v-for="rol in roles" :key="rol.id_rol" :value="rol.id_rol">
                {{ rol.descripcion }}
              </option>

            </select>
          </div>

          <div class="edit-actions">

            <button class="btn btn-success" @click="asignarRol">
              ✅ Guardar
            </button>

            <button class="btn btn-danger" @click="quitarRol">
              ❌ Quitar Rol
            </button>

            <button class="btn btn-secondary" @click="usuarioRolSeleccionado = null">
              Cancelar
            </button>

          </div>

        </div>
      </div>


      <div v-if="usuarioPasswordSeleccionado" class="edit-overlay">

        <div class="edit-card">

          <h3>
            Cambiar Password:
            {{ usuarioPasswordSeleccionado.nombre }}
          </h3>

          <div class="form-group">

            <label>Nueva Password:</label>

            <input v-model="nuevaPassword" type="password" placeholder="Nueva contraseña" />
          </div>

          <div class="edit-actions">

            <button class="btn btn-success" @click="cambiarPassword">
              ✅ Guardar
            </button>

            <button class="btn btn-secondary" @click="usuarioPasswordSeleccionado = null">
              Cancelar
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

          <RoleGuard :roles="['admin']">
            <div class="user-actions">

              <button class="btn-edit" @click="editarUsuario(u)">
                ✏️ Editar
              </button>

              <button class="btn-role" @click="abrirAsignarRol(u)">
                🛡️ Rol
              </button>

              <button class="btn-password" @click="abrirCambiarPassword(u)">
                🔑 Password
              </button>

            </div>
          </RoleGuard>
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