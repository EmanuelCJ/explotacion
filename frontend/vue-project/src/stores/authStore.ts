import { defineStore } from 'pinia'
import { auth , me , verificar } from '../api/inventario'


export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as null | User,
    isAuthenticated: false,
  }),

  actions: {
    async status() {
      try {
        const {res} = await verificar()
        if (res["valid"] === true) {
          this.isAuthenticated = true
        } else {
          this.isAuthenticated = false
        }
      } catch {
        this.user = null
        this.isAuthenticated = false
      }
    },

    async login(username: string, password: string) {
      const { usuario } =await auth(username, password)
      this.user = usuario
      await this.status()
    },

    async logout() {
      await axios.post('/api/auth/logout')
      this.user = null
      this.isAuthenticated = false
    }
  }
})
