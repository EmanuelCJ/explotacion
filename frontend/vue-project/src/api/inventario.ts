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
import type {
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
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

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
