<template>
  <div class="app-container">
    <AppSidebar
      :is-open="sidebarOpen"
      :active-section="activeSection"
      :username="currentUser.username"
      :rol="currentUser.rol"
      @toggle="sidebarOpen = !sidebarOpen"
      @section-change="handleSectionChange"
    />

    <main :class="['main-content', { 'main-content-expanded': !sidebarOpen }]">
      <AppHeader
        :nombre-usuario="currentUser.nombre"
        :localidad="currentUser.localidad"
        @logout="handleLogout"
      />

      <div class="content-wrapper">
        <div class="section-header">
          <h2 class="section-title">{{ activeSection }}</h2>
          <p class="section-description">
            Gestión de inventario y artículos del sistema
          </p>
        </div>

        <ActionBar
          :active-action="activeAction"
          :has-selection="selectedIds.length > 0"
          @action="handleAction"
        />

        <InventoryTable
          :articulos="articulos"
          :loading="loading"
          :selectable="selectable"
          :selected-ids="selectedIds"
          @selection-change="handleSelectionChange"
        />
      </div>
    </main>

    <ArticuloModal
      v-if="activeAction"
      :is-open="modalOpen"
      :action="activeAction"
      :articulo="selectedArticulo"
      :selected-count="selectedIds.length"
      @close="handleModalClose"
      @submit="handleModalSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import AppSidebar from "../components/AppSidebar.vue";
import AppHeader from "../components/AppHeader.vue";
import ActionBar from "../components/ActionBar.vue";
import InventoryTable from "../components/InventoryTable.vue";
import ArticuloModal from "../components/ArticuloModal.vue";
import { articulosApi } from "../services/api";
import type { Articulo, CrudAction, SidebarSection, User } from "../types";

// Usuario actual simulado
const currentUser = ref<User>({
  username: "carlos.mendez",
  nombre: "Carlos Mendez",
  rol: "admin",
  localidad: "Ciudad de Mexico",
});

// Estado de la aplicación
const sidebarOpen = ref(true);
const activeSection = ref<SidebarSection>("almacen");
const articulos = ref<Articulo[]>([]);
const loading = ref(true);
const activeAction = ref<CrudAction | null>(null);
const selectedIds = ref<number[]>([]);
const modalOpen = ref(false);

// Computed
const selectable = computed(() => {
  return (
    activeAction.value === "eliminar" ||
    activeAction.value === "actualizar" ||
    activeAction.value === "retirar" ||
    activeAction.value === "agregar"
  );
});

const selectedArticulo = computed(() => {
  if (selectedIds.value.length === 1) {
    return articulos.value.find((a) => a.id === selectedIds.value[0]) || null;
  }
  return null;
});

// Funciones
async function fetchArticulos(query?: string) {
  loading.value = true;
  try {
    const response = await articulosApi.getAll(query);
    articulos.value = response.data;
  } catch (error) {
    console.error("Error fetching articulos:", error);
  } finally {
    loading.value = false;
  }
}

function handleSectionChange(section: SidebarSection) {
  activeSection.value = section;
  // Aquí podrías cargar datos específicos de cada sección
}

function handleAction(action: CrudAction) {
  if (activeAction.value === action) {
    activeAction.value = null;
    selectedIds.value = [];
    return;
  }

  activeAction.value = action;
  selectedIds.value = [];

  if (action === "crear" || action === "buscar") {
    modalOpen.value = true;
  }
}

function handleSelectionChange(ids: number[]) {
  selectedIds.value = ids;
}

function handleModalClose() {
  modalOpen.value = false;
  if (activeAction.value === "crear" || activeAction.value === "buscar") {
    activeAction.value = null;
  }
}

async function handleModalSubmit(data: Partial<Articulo> & { cantidad?: number }) {
  try {
    switch (activeAction.value) {
      case "crear":
        await articulosApi.create(data);
        break;
      case "actualizar":
        if (selectedIds.value.length === 1) {
          await articulosApi.update(selectedIds.value[0], data);
        }
        break;
      case "buscar":
        await fetchArticulos(data.nombre || "");
        modalOpen.value = false;
        activeAction.value = null;
        return;
      case "retirar":
        for (const id of selectedIds.value) {
          await articulosApi.adjustStock(id, "retirar", data.cantidad || 1);
        }
        break;
      case "agregar":
        for (const id of selectedIds.value) {
          await articulosApi.adjustStock(id, "agregar", data.cantidad || 1);
        }
        break;
      case "eliminar":
        await articulosApi.delete(selectedIds.value);
        break;
    }
    modalOpen.value = false;
    activeAction.value = null;
    selectedIds.value = [];
    await fetchArticulos();
  } catch (error) {
    console.error("Error en operación:", error);
    alert("Ocurrió un error al realizar la operación");
  }
}

function handleLogout() {
  alert("Cerrando sesión...");
  // Aquí implementarías la lógica de logout real
}

// Watchers
watch(selectedIds, (newIds) => {
  if (newIds.length > 0 && selectable.value) {
    modalOpen.value = true;
  }
});

// Lifecycle
onMounted(() => {
  fetchArticulos();
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Inter", system-ui, -apple-system, sans-serif;
  background-color: #f1f5f9;
  color: #1e293b;
}

.app-container {
  min-height: 100vh;
  display: flex;
}

.main-content {
  flex: 1;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
}

.main-content-expanded {
  margin-left: 64px;
}

.content-wrapper {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-header {
  margin-bottom: 8px;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  text-transform: capitalize;
  margin-bottom: 4px;
}

.section-description {
  font-size: 14px;
  color: #64748b;
}
</style>
