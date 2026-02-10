<template>
  <aside :class="['sidebar', { 'sidebar-collapsed': !isOpen }]">
    <!-- Toggle Button -->
    <button class="sidebar-toggle" @click="$emit('toggle')">
      <svg
        v-if="isOpen"
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M15 18l-6-6 6-6" />
      </svg>
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path d="M9 18l6-6-6-6" />
      </svg>
    </button>

    <!-- Logo/Empresa -->
    <div class="sidebar-header">
      <div class="logo-container">
        <div class="logo-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M9 3v18" />
          </svg>
        </div>
        <span v-if="isOpen" class="logo-text">Logo Empresa</span>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <button
        v-for="section in sections"
        :key="section.id"
        :class="['nav-item', { active: activeSection === section.id }]"
        @click="$emit('sectionChange', section.id)"
        :title="section.label"
      >
        <component :is="section.icon" class="nav-icon" />
        <span v-if="isOpen" class="nav-label">{{ section.label }}</span>
      </button>
    </nav>

    <!-- Graficos y Estadisticas (only visible for admin role) -->
    <div v-if="rol === 'admin' && isOpen" class="sidebar-section">
      <h3 class="section-title">Gráficos y estadísticas</h3>
      <div class="chart-placeholder">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="80"
          viewBox="0 0 200 80"
          fill="none"
        >
          <path
            d="M 0,60 L 40,45 L 80,50 L 120,30 L 160,35 L 200,20"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
          />
        </svg>
      </div>
    </div>

    <!-- User Info -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="8" r="4" />
            <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" />
          </svg>
        </div>
        <div v-if="isOpen" class="user-details">
          <p class="user-name">{{ username }}</p>
          <p class="user-role">Rol: {{ rol }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { SidebarSection } from "../types";

interface Props {
  isOpen: boolean;
  activeSection: SidebarSection;
  username: string;
  rol: string;
}

defineProps<Props>();

defineEmits<{
  toggle: [];
  sectionChange: [section: SidebarSection];
}>();

const sections = computed(() => [
  {
    id: "almacen" as const,
    label: "Almacen",
    icon: "IconBox",
  },
  {
    id: "envios" as const,
    label: "Envios",
    icon: "IconTruck",
  },
  {
    id: "auditoria" as const,
    label: "Auditoria",
    icon: "IconClipboard",
  },
  {
    id: "estadisticas" as const,
    label: "Estadisticas",
    icon: "IconChart",
  },
]);

// Simple icon components
const IconBox = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    </svg>
  `,
};

const IconTruck = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M1 3h15v13H1z"/><path d="M16 8h4l3 3v5h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
    </svg>
  `,
};

const IconClipboard = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
    </svg>
  `,
};

const IconChart = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>
    </svg>
  `,
};
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 240px;
  background-color: #1e293b;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 100;
  overflow: hidden;
}

.sidebar-collapsed {
  width: 64px;
}

.sidebar-toggle {
  position: absolute;
  right: -12px;
  top: 20px;
  width: 24px;
  height: 24px;
  background-color: #3b82f6;
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: transform 0.2s;
}

.sidebar-toggle:hover {
  transform: scale(1.1);
}

.sidebar-header {
  padding: 24px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background-color: #3b82f6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: none;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background-color: #3b82f6;
  color: white;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  font-size: 14px;
  white-space: nowrap;
}

.sidebar-section {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 12px;
  color: #94a3b8;
}

.chart-placeholder {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  color: #64748b;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background-color: rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 11px;
  margin: 2px 0 0;
  color: #94a3b8;
}
</style>
