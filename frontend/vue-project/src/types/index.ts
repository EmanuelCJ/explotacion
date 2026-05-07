// ─── Enums ────────────────────────────────────────────────────────────────────

export enum TipoMovimiento {
  INGRESO = 'INGRESO',
  SALIDA = 'SALIDA',
  AJUSTE_POSITIVO = 'AJUSTE_POSITIVO',
  AJUSTE_NEGATIVO = 'AJUSTE_NEGATIVO',
  AJUSTE = 'AJUSTE'
}

export enum activo_producto {
  Activo = 1,
  NoActivo = 0
}

// ─── Modelos ──────────────────────────────────────────────────────────────────

export interface Producto {
  activo: number,
  codigo: string,
  costo: number,
  descripcion: string,
  created_at: string,
  descripcion_lugar: string,
  id_categoria: number,
  nombre_categoria: string,
  id_lugar: number,
  id_producto: number,
  nombre_lugar: string,
  nombre: string,
  stock: number,
  stock_minimo: number,
  unidad_medida: string,
  updated_at: string
}

export interface editarProducto {
  nombre?: string,
  costo?: number,
  unidad_medida?: string,
  id_categoria?: number,
  stock_minimo?: number,
  descripcion?: string,
  activo?: number
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


// ─── auth-interfaz ───────────────────────────────────────────────────────────────

// Interfaz login
export interface auth {
  username: string
  password: string
}

// ─── Usuario-interfaz ───────────────────────────────────────────────────────────────

// Modelo para crear un nuevo usuario
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
// modelo para obtener info del usuario
export interface UsuarioData {
  id_usuario: number
  nombre: string
  apellido: string
  username: string
  email?: string
  id_localidad?: number
  id_rol?: number,
  localidad_nombre?: string
  permisos: string[],
  activo?: number,
  legajo?: number,
  rol?: string,
  created_at?: string
}

// ─── respuesta-servidor-interfaz ───────────────────────────────────────────────────────────────

// Esta interfaz contesta el servidor 
interface ResponseError {
  error: string
  detail?: string
}

interface Refresh {
  mensaje: string
}

// Para obtener respuesta del servidor a enpoint refresh.
export type RefreshResponse = Refresh | ResponseError

interface AuthError {
  error: string
}
interface Auth {
  status: number
  message: string
  usuario: Usuario
}
// Para obtener respuesta del servidor a enpoint auth.
export type AuthResponse = Auth | AuthError | ResponseError

export interface Me {
  usuario: UsuarioData
  rol: string
  username: string
}

interface MeError {
  error: string
  detail?: string
}
// Para obtener respueta del servidor a enpoint me.
export type MeResponse = Me | MeError

interface Verificar {
  message: string,
  usuario_id: string,
  valid: boolean
}
interface VerificarError {
  valid: boolean,
  error: string
}

// para verificar la sesión activa, el servidor puede responder con éxito o error dependiendo de si la sesión es válida o no.
export type VerificarResponse = Verificar | VerificarError | ResponseError

interface logout {
  mensaje: string
}

interface LogoutError {
  error: string
  detail?: string
}

// respuesta del servidor al endpoint logout, puede ser un mensaje de éxito o un error.
export type LogoutResponse = logout | LogoutError

// respuesta de api/usuarios/
interface UsuariosData {
  usuarios: UsuarioData[]
}
// el enpoint devuelve error
interface UsuariosError {
  error: string
  detail?: string
}

export type UsuariosResponse = UsuariosData | UsuariosError

export interface usuariomodel {
  nombre : string,
  apellido:string,
  username : string,
  email: string,
  legajo:number,
  password : string,
  id_localidad:number,
  id_rol:number,
  activo?: number,
}


interface createUsuarioResponse {
  message: string,
  success: Boolean,
  usuario_id: number
}

interface createUsuarioError {
  error: string
  detail?: string
}

export type CreateResponse = createUsuarioResponse | createUsuarioError

interface updateSeccess {
  message: string
}

interface updateError {
  error: string,
  detail?: string
}

export type UpdateResponse = updateSeccess | updateError

export interface localidad {
  id_localidad: number,
  nombre: string
}

interface localidadesError {
  error: string,
  detail?: string
}

export type localidadesResponse = localidad[] | localidadesError

export interface roles {
  'id_rol':number,
  'nombre': string,
  'descripcion': string,
}

interface rolesError {
  error: string,
  detail?: string
}

export type get_roles = roles[] | rolesError