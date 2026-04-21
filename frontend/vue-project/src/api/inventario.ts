/**
 * Capa de servicio que conecta con la API REST de Flask.
 * Todos los endpoints asumen base URL "/api" (proxiada a http://localhost:5000).
 *
 * Endpoints esperados en Flask:
 *   GET  /api/resumen
 *   GET  /api/stock
 *   GET  /api/listas
 *   GET  /api/productos/buscar?q=<texto>
 *   GET  /api/productos/buscar-codigo?codigo=<codigo>
 *   POST /api/productos            { codigo, nombre, unidad, grupo, stockMin }
 *   POST /api/movimientos          { codigo, fecha, tipo, cantidad, observaciones }
 *   GET  /api/historial?fechaDesde=&fechaHasta=&tipo=
 *   GET  /api/exportar-stock       → { url: string }
 *   POST /api/inicializar
 *   GET  /api/validar-integridad
 */

import axios from 'axios'

// ─── Tipos de datos ───────────────────────────────────────────────────────────

import type {
  AuthResponse,
  Response,
  MeResponse,
  Resumen,
  ProductoStock,
  ProductoSugerencia,
  Listas,
  Movimiento,
  ValidacionIntegridad,
  NuevoProductoPayload,
  NuevoMovimientoPayload,
  FiltrosHistorial
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
export async function logout(): Promise<void> {
  const { data } = await http.post('/api/auth/logout')
  return data

}
// ─── Info del Usuario actual ───────────────────────────────
export async function me(): Promise<MeResponse> {
  return await http.get('/api/auth/me')
}
// ─── Verificar sesión activa (para proteger rutas) ─────────────────────────
export async function verificar(): Promise<Response> {
  return await http.get('/api/auth/verify')
}
// ─── Cambio de contraseña ─────────────────────────────────────────────────
export async function cambioPassword(oldPassword: string, newPassword: string): Promise<void> {
  const { data } = await http.post('/api/auth/password', { oldPassword, newPassword })
  return data
}
// ─── Refrescar token de sesión (si se implementa refresh tokens cada vez que expire) ─────────────
export async function refresh(): Promise<Response> {
  return await http.post('/api/auth/refresh')
}


// ─── Dashboard ────────────────────────────────────────────────────────────────

export async function obtenerResumen(): Promise<Resumen> {
  const { data } = await http.get<Resumen>('/resumen')
  return data
}

// ─── Stock / Inventario ───────────────────────────────────────────────────────

export async function obtenerStock(): Promise<ProductoStock[]> {
  const { data } = await http.get<ProductoStock[]>('/stock')
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

export async function buscarProducto(texto: string): Promise<ProductoStock[]> {
  const { data } = await http.get<ProductoStock[]>('/productos/buscar', {
    params: { q: texto }
  })
  return data
}

export async function buscarProductoPorCodigo(codigo: string): Promise<ProductoSugerencia[]> {
  const { data } = await http.get<ProductoSugerencia[]>('/productos/buscar-codigo', {
    params: { codigo }
  })
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
