/**
  * Archivo: src/api/inventario.ts
 */

import axios from 'axios'

// ─── Tipos de datos ───────────────────────────────────────────────────────────

import type {
  AuthResponse,
  RefreshResponse,
  MeResponse,
  VerificarResponse,
  LogoutResponse,
  editarProducto,
  UsuariosResponse,
  CreateResponse,
  UpdateResponse,
  Resumen,
  Producto,
  ProductoSugerencia,
  Listas,
  Movimiento,
  ValidacionIntegridad,
  NuevoProductoPayload,
  NuevoMovimientoPayload,
  FiltrosHistorial,
  UsuarioData,
  localidadesResponse
} from '@/types'


const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // guarda cookies para sesiones autenticadas
})

// ─── Autenticación (si se implementa) ─────────────────────────────────────── 
export async function auth(username: string, password: string): Promise<AuthResponse> {
  const { data } = await http.post<AuthResponse>('/api/auth/login', {
    username,
    password
  })
  return data
}

// ─── Cerrar sesión ─────────────────────────────────────────────────────────
export async function logout(): Promise<LogoutResponse> {
  const { data } = await http.post('/api/auth/logout')
  return data
}

// ─── Info del Usuario actual ───────────────────────────────
export async function me(): Promise<MeResponse> {
  const { data } = await http.get<MeResponse>('/api/auth/me')
  return data
}

// ─── Verificar sesión activa (para proteger rutas) ─────────────────────────
export async function verificar(): Promise<VerificarResponse> {
  const { data } = await http.get('/api/auth/verify')
  return data
}
// ─── Cambio de contraseña ─────────────────────────────────────────────────
export async function cambioPassword(oldPassword: string, newPassword: string): Promise<void> {
  const { data } = await http.post('/api/auth/password', { oldPassword, newPassword })
  return data
}
// ─── Refrescar token de sesión (si se implementa refresh tokens cada vez que expire) ─────────────
export async function refresh(): Promise<RefreshResponse> {
  return await http.post('/api/auth/refresh')
}


// ─── Dashboard ────────────────────────────────────────────────────────────────

export async function obtenerResumen(): Promise<Resumen> {
  const { data } = await http.get<Resumen>('/resumen')
  return data
}

// ─── Stock / Inventario ───────────────────────────────────────────────────────

export async function obtenerStock(): Promise<{ stock: Producto[] }> {
  const { data } = await http.get<{ stock: Producto[] }>('/api/productos/stock')
  return data
}

export async function exportarStockCSV(): Promise<string | null> {
  const { data } = await http.get<{ url: string }>('/exportar-stock')
  return data?.url ?? null
}

// ─── Productos ────────────────────────────────────────────────────────────────

export async function registrarProducto(payload: NuevoProductoPayload): Promise<string> {
  const { data } = await http.post<{ mensaje: string }>('/productos', payload)
  return data.mensaje
}

// export async function buscarProducto(texto: string): Promise<editarProducto> {
//   const { data } = await http.get<ProductoStock[]>('/productos/buscar', {
//     params: { q: texto }
//   })
//   return data
// }

export async function buscarProductoPorCodigo(codigo: string): Promise<ProductoSugerencia[]> {
  const { data } = await http.get<ProductoSugerencia[]>('/productos/buscar-codigo', {
    params: { codigo }
  })
  return data
}

export async function actualizarProducto(id_producto: number, cambios: editarProducto): Promise<boolean> {
  const { data } = await http.put(`/api/productos/editar/${id_producto}`, cambios)
  return data
}


// ─── Movimientos ──────────────────────────────────────────────────────────────

export async function registrarMovimiento(payload: NuevoMovimientoPayload): Promise<string> {
  const { data } = await http.post<{ mensaje: string }>('/movimientos', payload)
  return data.mensaje
}

// ─── Historial / Reportes ─────────────────────────────────────────────────────

export async function obtenerHistorial(filtros: FiltrosHistorial): Promise<Movimiento[]> {
  const { data } = await http.get<Movimiento[]>('/historial', { params: filtros })
  return data
}

// ─── Listas auxiliares ───────────────────────────────────────────────────────

export async function obtenerListas(): Promise<Listas> {
  const { data } = await http.get<Listas>('/listas')
  return data
}

// ─── Configuración ───────────────────────────────────────────────────────────

export async function inicializarSistema(): Promise<string> {
  const { data } = await http.post<{ mensaje: string }>('/inicializar')
  return data.mensaje
}

export async function validarIntegridad(): Promise<ValidacionIntegridad> {
  const { data } = await http.get<ValidacionIntegridad>('/validar-integridad')
  return data
}

// ─── Usuarios ───────────────────────────────────────────────────────────

export async function obtenerUsuarios(): Promise<UsuariosResponse> {
  const { data } = await http.get<UsuariosResponse>('/api/usuarios/')
  return data
}

export async function crearUsuarios(): Promise<CreateResponse> {
  const { data } = await http.get<CreateResponse>('/api/usuario/create')
  return data
}

export async function updateUsuario(id_usuario: number, cambios: Partial<UsuarioData>) {
  const { data } = await http.put<UpdateResponse>(
    `/api/usuario/update/${id_usuario}`,
    cambios
  )
  return data
}

// ─── localidades ───────────────────────────────────────────────────────────
export async function obtenerLocalidades(): Promise<localidadesResponse>{
  const { data } = await http.get<localidadesResponse>('/api/localidades/')
  return data
}