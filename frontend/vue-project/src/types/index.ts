// interfaces TypeScript completas (Producto, Movimiento, Resumen, Listas, etc).

import type { st } from "vue-router/dist/router-CWoNjPRp.mjs";

export interface Producto {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  costo: number;
  stock: number;
  categoria: string;
  lugar: string;
  unidadMedida: string;
}

export interface Usuario {
  username: string;
  nombre: string;
  rol: number;
  apellido : string,
  email : string,
  password : string,
  legajo : string,
  id_localidad : number,
  id_rol : number
}

export type CrudAction =
  | "crear"
  | "actualizar"
  | "buscar"
  | "retirar"
  | "agregar"
  | "eliminar";

export type SidebarSection = "almacen" | "envios" | "auditoria" | "estadisticas";
