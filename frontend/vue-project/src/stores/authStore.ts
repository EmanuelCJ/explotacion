import { defineStore } from 'pinia'
import { auth } from '../api/inventario'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as null | User,
    isAuthenticated: false,
    loading: false
  }),

  actions: {
    async fetchUser() {
      try {
        const res = await axios.get('/api/auth/me')
        this.user = res.data
        this.isAuthenticated = true
      } catch {
        this.user = null
        this.isAuthenticated = false
      }
    },

    async login(data) {
      await axios.post('/api/auth/login', data)
      await this.fetchUser()
    },

    async logout() {
      await axios.post('/api/auth/logout')
      this.user = null
      this.isAuthenticated = false
    }
  }
})
