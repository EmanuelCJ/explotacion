<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { logout } from '@/api/inventario'

const router = useRouter()
const route = useRoute()


const navItems = [
  { name: 'dashboard', label: 'Dashboard', icon: '📊' },
  { name: 'productos', label: 'Nuevo Producto', icon: '📦' },
  { name: 'movimientos', label: 'Movimientos', icon: '📋' },
  { name: 'inventario', label: 'Inventario', icon: '🗃️' },
  { name: 'reportes', label: 'Reportes', icon: '📈' },
  { name: 'buscar', label: 'Buscar', icon: '🔍' },
  { name: 'configuracion', label: 'Configuración', icon: '⚙️' }
] as const

function isActive(name: string): boolean {
  return route.name === name
}

function handleLogout() {
  logout().then(() => {
    router.push({ name: 'login' })
  })
}

</script>

<template>
  <nav class="sidebar">
    <div class="sidebar-header">
      <h1>QASO SYSTEM</h1>
      <p class="subtitle">Control de Inventario</p>
    </div>
    <ul class="nav-menu">
      <li v-for="item in navItems" :key="item.name" class="nav-item">
        <a class="nav-link" :class="{ active: isActive(item.name) }" @click="router.push({ name: item.name })">
          <span class="nav-icon">{{ item.icon }}</span>
          {{ item.label }}
        </a>
      </li>
    </ul>
    <!-- Botón Logout fijo abajo -->
    <div class="logout-container">
      
      <button class="logout-button" @click="handleLogout">
        Cierre de sesión
      </button>
    </div>
  </nav>
</template>


<style scoped>
.sidebar {
  width: 250px;
  background: #2e86ab;
  color: #fff;
  flex-shrink: 0;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
}

.sidebar-header {
  padding: 22px 20px;
  background: #1c5f7b;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.sidebar-header h1 {
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.nav-menu {
  list-style: none;
  padding: 16px 0;
  flex-grow: 1;
}

.nav-item {
  margin: 4px 14px;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 11px 14px;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: background 0.2s, color 0.2s, transform 0.2s;
  cursor: pointer;
  font-size: 0.9rem;
  user-select: none;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  transform: translateX(4px);
}

.nav-link.active {
  background: #5dade2;
  color: #fff;
  font-weight: 600;
}

.nav-icon {
  margin-right: 10px;
  font-size: 1rem;
  width: 22px;
  text-align: center;
}

.logout-container {
  margin-top: auto; /* empuja el botón hacia abajo */
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.logout-button {
  width: 100%;
  padding: 12px;
  background: #e74c3c;
  color: #fff;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.logout-button:hover {
  background: #c0392b;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: fixed;
    top: 0;
    left: -100%;
    z-index: 1000;
    transition: left 0.3s;
  }

  .sidebar.open {
    left: 0;
  }
}
</style>
