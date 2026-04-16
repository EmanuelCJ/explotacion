<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import { useInventarioStore } from '@/stores/inventario'

const route = useRoute()
const store = useInventarioStore()

onMounted(async () => {
  await store.cargarListas()
})
</script>

<template>
  <div class="app-container">
    <AppSidebar />
    <div class="main-content">
      <div class="content-header">
        <h2>{{ route.meta.title as string }}</h2>
      </div>
      <div class="content-body">
        <RouterView class="fade-in" />
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
