import { defineStore } from 'pinia'
import { me } from '@/api/inventario'
import type { UsuarioData, MeResponse } from '@/types'

export const useUsuarioStore = defineStore('usuario', {
  state: () => ({
    usuario: null as UsuarioData | any, //cambie null por any
    rol: null as string | null,
    username: null as string | null,
    error: null as string | null,
  }),
  actions: {
    async fetchUsuario() {
      try {
        const response: MeResponse = await me()

        if ('usuario' in response) {
          this.usuario = response.usuario
          this.rol = response.rol
          this.username = response.username
          this.error = null
        } else {
          this.usuario = null
          this.rol = null
          this.username = null
          this.error = response.error ?? 'Error desconocido'
        }
      } catch (err: any) {
        this.usuario = null
        this.rol = null
        this.username = null
        this.error = err.response?.data || 'Error al obtener usuario'
      }
    }
  }
})
