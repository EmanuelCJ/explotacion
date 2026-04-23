// ─── Enums ────────────────────────────────────────────────────────────────────

export enum TipoMovimiento {
  INGRESO = 'INGRESO',
  SALIDA = 'SALIDA',
  AJUSTE_POSITIVO = 'AJUSTE_POSITIVO',
  AJUSTE_NEGATIVO = 'AJUSTE_NEGATIVO',
  AJUSTE = 'AJUSTE'
}

export enum activo {
  NORMAL = 1,
  BAJO = 2,
  SIN_STOCK = 3
}

// ─── Modelos ──────────────────────────────────────────────────────────────────

export interface Producto {
  codigo: string
  nombre: string
  unidad_medida?: string
  id_categoria: number
  stock_minimo: number
  descripcion: string
  costo?: number
}

export interface ProductoStock extends Producto {
  cantidad: number
  estado: activo
}

export interface ProductoSugerencia {
  codigo: string
  nombre: string
  unidad: string
  grupo: string
}

export interface Movimiento {
  codigo: string
  fecha: string
  tipo: TipoMovimiento
  cantidad: number
  producto: string
  observaciones: string
  usuario: string
}

export interface Resumen {
  totalProductos: number
  totalMovimientos: number
  sinStock: number
  stockBajo: number
  valorTotalInventario: number
  movimientosUltimoMes: number
}

export interface Listas {
  unidades: string[]
  grupos: string[]
}

export interface ValidacionIntegridad {
  errores: string[]
}

// ─── Payloads para requests ───────────────────────────────────────────────────

export interface NuevoProductoPayload {
  codigo: string
  nombre: string
  unidad: string
  grupo: string
  stockMin: number
}

export interface NuevoMovimientoPayload {
  codigo: string
  fecha: string
  tipo: TipoMovimiento
  cantidad: number
  observaciones: string
}

export interface FiltrosHistorial {
  fechaDesde: string
  fechaHasta: string
  tipo: TipoMovimiento | ''
}

// ─── Respuesta API genérica ───────────────────────────────────────────────────

export interface ApiResponse<T = void> {
  ok: boolean
  mensaje?: string
  data?: T
}

// ─── UI helpers ───────────────────────────────────────────────────────────────

export type MessageType = 'success' | 'error' | 'warning' | 'info'

export interface AppMessage {
  text: string
  type: MessageType
}

export interface auth {
  username: string
  password: string
}

interface ResponseServer {
  mensaje: string
}

interface ResponseError {
  error: string
  detail?: string
}

// El servidor puede responder con éxito y error para manejarlo mejor en el frontend.
export type Response = ResponseServer | ResponseError

export interface Usuario {
  id: number
  nombre: string
  apellido: string
  username: string
  email?: string
  rol: string
  localidad?: string
  permisos: string[]
}

export type MeResponse = Usuario | ResponseError

interface AuthSuccess {
  status: number
  message: string
  usuario: Usuario
}

interface AuthError {
  error: string
}

export type AuthResponse = AuthSuccess | AuthError

