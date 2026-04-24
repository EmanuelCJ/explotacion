import { defineStore } from 'pinia'
import { auth, verificar , logout } from '@/api/inventario'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any,
    isAuthenticated: false,
    initialized: false // 🔥 importante para el guard
  }),

  actions: {
    async fetchUser() {
      try {
        const data = await verificar()
        this.user = data
        this.isAuthenticated = true
      } catch {
        this.user = null
        this.isAuthenticated = false
      } finally {
        this.initialized = true
      }
    },

    async login(username: string, password: string) {
      const response = await auth(username, password)
      await this.fetchUser()
      return response
    },

    async logout() {
      try {
        await logout()
      } catch {}
      this.user = null
      this.isAuthenticated = false
    }
  }
})