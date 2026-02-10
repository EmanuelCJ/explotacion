<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-title">
        <h1>SISTEMAS Explotacion</h1>
        <p class="header-subtitle">
          Hola, <span class="user-greeting">{{ nombreUsuario }}</span> | Localidad:
          {{ localidad }}
        </p>
      </div>
      <button class="btn-logout" @click="$emit('logout')">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        <span>Cerrar Sesión</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
interface Props {
  nombreUsuario: string;
  localidad: string;
}

defineProps<Props>();

defineEmits<{
  logout: [];
}>();
</script>

<style scoped>
.app-header {
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

.header-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0;
}

.user-greeting {
  font-weight: 600;
  color: #3b82f6;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-logout:hover {
  background-color: #dc2626;
}
</style>
