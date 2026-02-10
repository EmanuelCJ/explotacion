import axios from "axios";
import type { Articulo } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const articulosApi = {
  getAll: (query?: string) => {
    const params = query ? { q: query } : {};
    return api.get<Articulo[]>("/articulos", { params });
  },

  create: (data: Partial<Articulo>) => {
    return api.post<Articulo>("/articulos", data);
  },

  update: (id: number, data: Partial<Articulo>) => {
    return api.put<Articulo>("/articulos", { id, ...data });
  },

  delete: (ids: number[]) => {
    return api.delete(`/articulos?ids=${ids.join(",")}`);
  },

  adjustStock: (id: number, action: "agregar" | "retirar", cantidad: number) => {
    return api.patch<Articulo>("/articulos", { id, action, cantidad });
  },
};
