import { defineStore } from 'pinia'
import { auth, verificar, logout, me } from '@/api/inventario'
import type { UsuarioData, MeResponse } from '@/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    usuario: null as UsuarioData | null,
    rol: null as string | any,
    username: null as string | null,
    error: null as string | null,
    isAuthenticated: false,
    initialized: false
  }),

  getters: {
    hasRoles: (state) => {
      return (roles: readonly string[]) => {
        if (!state.isAuthenticated) return false
        if (!state.rol) return false

        return roles.includes(state.rol)
      }
    }
  },

  actions: {
    // Esta función verifica la sesión (ej: al refrescar F5)
    async fetchUser() {
      try {
        await verificar() // Verifica token/cookie
        await this.fetchMe() // Carga rol y datos
        this.isAuthenticated = true
      } catch {
        this.clearAuth()
      } finally {
        this.initialized = true
      }
    },

    // Carga los detalles específicos (especialmente el ROL)
    async fetchMe() {
      try {
        const response: MeResponse = await me()

        console.log('ME RESPONSE:', response)

        if ('usuario' in response) {
          this.usuario = response.usuario

          // 🔥 CORRECTO
          this.rol = response.usuario.rol
          this.username = response.usuario.username

          console.log('ROL:', this.rol)

          this.error = null
        }
      } catch (err: any) {
        this.clearAuth()
        this.error = err.response?.data || 'Error al obtener perfil'
      }
    },

    async login(username: string, password: string) {
      try {
        const response = await auth(username, password)
        // 🔥 CRUCIAL: Cargar los datos ANTES de que el router actúe
        this.isAuthenticated = true
        await this.fetchMe()
        this.initialized = true
        return response
      } catch (error) {
        this.clearAuth()
        throw error
      }
    },

    async logout() {
      try {
        await logout()
      } finally {
        this.clearAuth()
      }
    },

    // Helper para resetear todo
    clearAuth() {
      this.usuario = null
      this.rol = null
      this.username = null
      this.isAuthenticated = false
      this.initialized = true
    }
  }
})