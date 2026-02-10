<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="handleClose">
        <div class="modal-container">
          <div class="modal-header">
            <h2>{{ modalTitle }}</h2>
            <button class="btn-close" @click="handleClose">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          <form class="modal-body" @submit.prevent="handleSubmit">
            <!-- Buscar -->
            <div v-if="action === 'buscar'" class="form-group">
              <label for="search">Buscar por nombre</label>
              <input
                id="search"
                v-model="formData.nombre"
                type="text"
                placeholder="Ingrese el nombre del artículo"
              />
            </div>

            <!-- Cantidad (para retirar/agregar) -->
            <div
              v-if="action === 'retirar' || action === 'agregar'"
              class="form-group"
            >
              <label for="cantidad">Cantidad</label>
              <input
                id="cantidad"
                v-model.number="formData.cantidad"
                type="number"
                min="1"
                required
              />
              <p class="help-text">
                {{ action === "retirar" ? "Cantidad a retirar" : "Cantidad a agregar" }}
              </p>
            </div>

            <!-- Confirmar eliminación -->
            <div v-if="action === 'eliminar'" class="alert-danger">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
                />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <p>
                ¿Está seguro que desea eliminar
                {{ selectedCount > 1 ? `${selectedCount} artículos` : "este artículo" }}?
              </p>
            </div>

            <!-- Crear/Actualizar -->
            <template v-if="action === 'crear' || action === 'actualizar'">
              <div class="form-group">
                <label for="nombre">Nombre *</label>
                <input
                  id="nombre"
                  v-model="formData.nombre"
                  type="text"
                  required
                />
              </div>

              <div class="form-group">
                <label for="codigo">Código *</label>
                <input
                  id="codigo"
                  v-model="formData.codigo"
                  type="text"
                  required
                />
              </div>

              <div class="form-group">
                <label for="descripcion">Descripción</label>
                <textarea
                  id="descripcion"
                  v-model="formData.descripcion"
                  rows="3"
                ></textarea>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="costo">Costo *</label>
                  <input
                    id="costo"
                    v-model.number="formData.costo"
                    type="number"
                    step="0.01"
                    min="0"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="stock">Stock *</label>
                  <input
                    id="stock"
                    v-model.number="formData.stock"
                    type="number"
                    min="0"
                    required
                  />
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="categoria">Categoría *</label>
                  <input
                    id="categoria"
                    v-model="formData.categoria"
                    type="text"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="lugar">Lugar *</label>
                  <input id="lugar" v-model="formData.lugar" type="text" required />
                </div>
              </div>

              <div class="form-group">
                <label for="unidadMedida">Unidad de Medida *</label>
                <input
                  id="unidadMedida"
                  v-model="formData.unidadMedida"
                  type="text"
                  required
                />
              </div>
            </template>

            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="handleClose">
                Cancelar
              </button>
              <button type="submit" class="btn-primary">
                {{ submitButtonText }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, reactive } from "vue";
import type { Articulo, CrudAction } from "../types";

interface Props {
  isOpen: boolean;
  action: CrudAction;
  articulo?: Articulo | null;
  selectedCount?: number;
}

const props = withDefaults(defineProps<Props>(), {
  articulo: null,
  selectedCount: 0,
});

const emit = defineEmits<{
  close: [];
  submit: [data: Partial<Articulo> & { cantidad?: number }];
}>();

const formData = reactive<Partial<Articulo> & { cantidad?: number }>({
  nombre: "",
  codigo: "",
  descripcion: "",
  costo: 0,
  stock: 0,
  categoria: "",
  lugar: "",
  unidadMedida: "",
  cantidad: 1,
});

watch(
  () => props.articulo,
  (newArticulo) => {
    if (newArticulo) {
      Object.assign(formData, newArticulo);
    } else {
      resetForm();
    }
  },
  { immediate: true }
);

watch(
  () => props.isOpen,
  (isOpen) => {
    if (!isOpen) {
      resetForm();
    }
  }
);

function resetForm() {
  formData.nombre = "";
  formData.codigo = "";
  formData.descripcion = "";
  formData.costo = 0;
  formData.stock = 0;
  formData.categoria = "";
  formData.lugar = "";
  formData.unidadMedida = "";
  formData.cantidad = 1;
}

const modalTitle = computed(() => {
  const titles: Record<CrudAction, string> = {
    crear: "Crear Artículo",
    actualizar: "Actualizar Artículo",
    buscar: "Buscar Artículo",
    retirar: "Retirar Stock",
    agregar: "Agregar Stock",
    eliminar: "Eliminar Artículo",
  };
  return titles[props.action];
});

const submitButtonText = computed(() => {
  const texts: Record<CrudAction, string> = {
    crear: "Crear",
    actualizar: "Actualizar",
    buscar: "Buscar",
    retirar: "Retirar",
    agregar: "Agregar",
    eliminar: "Eliminar",
  };
  return texts[props.action];
});

function handleClose() {
  emit("close");
}

function handleSubmit() {
  emit("submit", { ...formData });
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-container {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.btn-close {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-close:hover {
  background-color: #f1f5f9;
  color: #1e293b;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #334155;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.help-text {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.alert-danger {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  margin-bottom: 20px;
}

.alert-danger svg {
  flex-shrink: 0;
}

.alert-danger p {
  margin: 0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn-secondary,
.btn-primary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background-color: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover {
  background-color: #e2e8f0;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
