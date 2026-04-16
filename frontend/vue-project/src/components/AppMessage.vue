<script setup lang="ts">
import type { MessageType } from '@/types'

defineProps<{
  text: string
  type: MessageType
}>()
</script>

<template>
  <div v-if="text" :class="['message', type]">{{ text }}</div>
</template>

<style scoped>
.message {
  padding: 11px 14px;
  border-radius: 8px;
  margin: 12px 0;
  font-weight: 500;
  font-size: 0.9rem;
}
.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.error   { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
.info    { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
</style>
