export interface Articulo {
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

export interface User {
  username: string;
  nombre: string;
  rol: "admin" | "usuario" | "visualizador";
  localidad: string;
}

export type CrudAction =
  | "crear"
  | "actualizar"
  | "buscar"
  | "retirar"
  | "agregar"
  | "eliminar";

export type SidebarSection = "almacen" | "envios" | "auditoria" | "estadisticas";
