<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from './stores/authStore';
const auth = useAuthStore()

//persiste sesiones entre recargas
onMounted(async () => {
  await auth.fetchUser()
})

</script>

<template>
  <RouterView />
</template>

<style scoped>
/* Estilos globales para resetear el navegador */
body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  height: 100vh;
}

/* Transiciones suaves entre vistas */
.fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #fafbfc;
  display: flex;
  flex-direction: column;
}

.content-header {
  background: #fff;
  padding: 18px 28px;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.content-header h2 {
  color: #2e86ab;
  font-size: 1.4rem;
  font-weight: 600;
}

.content-body {
  padding: 28px;
  flex: 1;
}
</style>
