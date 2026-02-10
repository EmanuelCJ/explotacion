<template>
  <div class="action-bar">
    <button
      v-for="action in actions"
      :key="action.id"
      :class="['action-btn', { active: activeAction === action.id }]"
      :disabled="action.requiresSelection && !hasSelection"
      @click="$emit('action', action.id)"
    >
      {{ action.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { CrudAction } from "../types";

interface Props {
  activeAction: CrudAction | null;
  hasSelection: boolean;
}

defineProps<Props>();

defineEmits<{
  action: [action: CrudAction];
}>();

const actions = computed(() => [
  {
    id: "crear" as const,
    label: "Crear",
    requiresSelection: false,
  },
  {
    id: "actualizar" as const,
    label: "Actualizar",
    requiresSelection: true,
  },
  {
    id: "buscar" as const,
    label: "Buscar",
    requiresSelection: false,
  },
  {
    id: "retirar" as const,
    label: "Retirar",
    requiresSelection: true,
  },
  {
    id: "agregar" as const,
    label: "Agregar",
    requiresSelection: true,
  },
  {
    id: "eliminar" as const,
    label: "Eliminar",
    requiresSelection: true,
  },
]);
</script>

<style scoped>
.action-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 20px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.action-btn.active {
  background-color: #1e40af;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.action-btn:disabled {
  background-color: #cbd5e1;
  color: #94a3b8;
  cursor: not-allowed;
  transform: none;
}
</style>
