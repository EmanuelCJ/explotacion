<!-- 
 RoleGuard.vue 
 Este componente sirve para ocultar los elementos dependiendo de rol del usuario.
-->
<template>
  <slot v-if="allowed" />
</template>

<script setup lang="ts">

import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const props = defineProps<{ roles: readonly string[] }>()

const auth = useAuthStore()

const allowed = computed(() => {
  return auth.hasRoles(props.roles)
})

</script>