<template>
  <div class="table-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Cargando artículos...</p>
    </div>

    <div v-else-if="articulos.length === 0" class="empty-state">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p>No se encontraron artículos</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="inventory-table">
        <thead>
          <tr>
            <th v-if="selectable" class="checkbox-cell">
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th>ID</th>
            <th>Nombre</th>
            <th>Código</th>
            <th>Descripción</th>
            <th>Costo</th>
            <th>Stock</th>
            <th>Categoría</th>
            <th>Lugar</th>
            <th>Unidad Medida</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="articulo in articulos"
            :key="articulo.id"
            :class="{ selected: isSelected(articulo.id) }"
          >
            <td v-if="selectable" class="checkbox-cell">
              <input
                type="checkbox"
                :checked="isSelected(articulo.id)"
                @change="toggleSelection(articulo.id)"
              />
            </td>
            <td>{{ articulo.id }}</td>
            <td class="cell-bold">{{ articulo.nombre }}</td>
            <td>{{ articulo.codigo }}</td>
            <td class="cell-description">{{ articulo.descripcion }}</td>
            <td class="cell-currency">${{ articulo.costo.toFixed(2) }}</td>
            <td :class="['cell-stock', getStockClass(articulo.stock)]">
              {{ articulo.stock }}
            </td>
            <td>{{ articulo.categoria }}</td>
            <td>{{ articulo.lugar }}</td>
            <td>{{ articulo.unidadMedida }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Articulo } from "../types";

interface Props {
  articulos: Articulo[];
  loading: boolean;
  selectable: boolean;
  selectedIds: number[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
  selectionChange: [ids: number[]];
}>();

const allSelected = computed(() => {
  return (
    props.articulos.length > 0 &&
    props.articulos.every((a) => props.selectedIds.includes(a.id))
  );
});

function isSelected(id: number): boolean {
  return props.selectedIds.includes(id);
}

function toggleSelection(id: number) {
  if (isSelected(id)) {
    emit(
      "selectionChange",
      props.selectedIds.filter((selectedId) => selectedId !== id)
    );
  } else {
    emit("selectionChange", [...props.selectedIds, id]);
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    emit("selectionChange", []);
  } else {
    emit(
      "selectionChange",
      props.articulos.map((a) => a.id)
    );
  }
}

function getStockClass(stock: number): string {
  if (stock === 0) return "stock-zero";
  if (stock < 10) return "stock-low";
  return "stock-ok";
}
</script>

<style scoped>
.table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state svg {
  color: #cbd5e1;
  margin-bottom: 16px;
}

.table-wrapper {
  overflow-x: auto;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
}

.inventory-table thead {
  background-color: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
}

.inventory-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: #475569;
  white-space: nowrap;
}

.inventory-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}

.inventory-table tbody tr {
  transition: background-color 0.2s;
}

.inventory-table tbody tr:hover {
  background-color: #f8fafc;
}

.inventory-table tbody tr.selected {
  background-color: #dbeafe;
}

.checkbox-cell {
  width: 40px;
  text-align: center;
}

.checkbox-cell input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.cell-bold {
  font-weight: 600;
  color: #1e293b;
}

.cell-description {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-currency {
  font-weight: 500;
  color: #059669;
}

.cell-stock {
  font-weight: 600;
}

.stock-zero {
  color: #ef4444;
}

.stock-low {
  color: #f59e0b;
}

.stock-ok {
  color: #10b981;
}
</style>
