<!-- RoleGuard.vue -->
<template>
  <slot v-if="allowed" />
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'

const props = defineProps<{ roles: string[] }>()

const auth = useAuthStore()

const allowed = auth.hasRole(props.roles)
</script>