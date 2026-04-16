<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ProductoSugerencia } from '@/types'
import { buscarProductoPorCodigo } from '@/api/inventario'

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'select': [producto: ProductoSugerencia]
}>()

const sugerencias = ref<ProductoSugerencia[]>([])
const mostrarDropdown = ref(false)
let debounceTimer: ReturnType<typeof setTimeout>

watch(() => props.modelValue, async (val) => {
  clearTimeout(debounceTimer)
  if (!val || val.length < 1) {
    sugerencias.value = []
    mostrarDropdown.value = false
    return
  }
  debounceTimer = setTimeout(async () => {
    sugerencias.value = await buscarProductoPorCodigo(val)
    mostrarDropdown.value = sugerencias.value.length > 0
  }, 300)
})

function onInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLInputElement).value)
}

function seleccionar(p: ProductoSugerencia) {
  emit('update:modelValue', p.codigo)
  emit('select', p)
  mostrarDropdown.value = false
}

function onBlur() {
  setTimeout(() => { mostrarDropdown.value = false }, 150)
}
</script>

<template>
  <div class="autocomplete-wrapper">
    <input
      :value="modelValue"
      :placeholder="placeholder ?? 'Código del producto'"
      type="text"
      autocomplete="off"
      @input="onInput"
      @blur="onBlur"
      @focus="mostrarDropdown = sugerencias.length > 0"
    />
    <div v-if="mostrarDropdown" class="dropdown">
      <div
        v-for="p in sugerencias"
        :key="p.codigo"
        class="dropdown-item"
        @mousedown.prevent="seleccionar(p)"
      >
        <span class="item-codigo">{{ p.codigo }}</span>
        <span class="item-nombre">{{ p.nombre }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.autocomplete-wrapper { position: relative; }

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 2px solid #5dade2;
  border-top: none;
  border-radius: 0 0 8px 8px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.dropdown-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #e5f2f7;
  transition: background 0.15s;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.dropdown-item:last-child { border-bottom: none; }
.dropdown-item:hover { background: #f0f8fc; }

.item-codigo { font-weight: 600; color: #2e86ab; font-size: 0.875rem; }
.item-nombre { color: #6c757d; font-size: 0.8rem; }
</style>
