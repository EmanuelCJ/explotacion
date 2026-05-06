<!-- 
 RoleGuard.vue 
 Este componente sirve para ocultar los elementos dependiendo de rol del usuario.
-->
<template>
  <slot v-if="allowed" />
</template>

<script setup lang="ts">
import { useUsuarioStore } from '@/stores/UsuarioStore';

const props = defineProps<{ roles: string[] }>()

const usuario = useUsuarioStore()

const allowed = usuario.Role(props.roles)

</script>