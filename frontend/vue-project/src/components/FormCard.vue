<script setup lang="ts">
import { reactive, watch } from 'vue'

const props = defineProps<{
  modelValue: any
  fields: any[]
  title: string
}>()

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

const form = reactive({ ...props.modelValue })

watch(form, () => {
  emit('update:modelValue', form)
}, { deep: true })

const handleSubmit = () => {
  emit('submit', form)
}
</script>

<template>
  <div class="edit-overlay">
    <div class="edit-card">
      <h3>{{ title }}</h3>

      <div class="grid-form">
        <div v-for="field in fields" :key="field.key" class="form-group">
          <label>{{ field.label }}</label>

          <!-- INPUT -->
          <input
            v-if="field.type === 'text' || field.type === 'number'"
            :type="field.type"
            v-model="form[field.key]"
          />

          <!-- SELECT -->
          <select v-else-if="field.type === 'select'" v-model="form[field.key]">
            <option v-for="opt in field.options" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="edit-actions">
        <button @click="handleSubmit">Confirmar</button>
        <button @click="$emit('cancel')">Cancelar</button>
      </div>
    </div>
  </div>
</template>