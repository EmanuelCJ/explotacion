// ─── Enums ────────────────────────────────────────────────────────────────────

export enum TipoMovimiento {
  INGRESO = 'INGRESO',
  SALIDA = 'SALIDA',
  AJUSTE_POSITIVO = 'AJUSTE_POSITIVO',
  AJUSTE_NEGATIVO = 'AJUSTE_NEGATIVO',
  AJUSTE = 'AJUSTE'
}

export enum EstadoStock {
  NORMAL = 'Normal',
  BAJO = 'Stock Bajo',
  SIN_STOCK = 'Sin Stock'
}

// ─── Modelos ──────────────────────────────────────────────────────────────────

export interface Producto {
  codigo: string
  nombre: string
  unidad: string
  grupo: string
  stockMin: number
  fechaCreacion?: string
}

export interface ProductoStock extends Producto {
  cantidad: number
  estado: EstadoStock
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
