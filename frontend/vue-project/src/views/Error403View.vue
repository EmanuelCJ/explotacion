<template>
  <div class="error-container">
    <div class="error-card">
      <h1>🚫 Acceso Denegado</h1>
      <p>No estás autorizado para ingresar a esta sección.</p>
      <p>Serás redirigido al inicio en {{ countdown }} segundos...</p>
      <router-link to="/" class="btn-home">Ir al Home ahora</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const countdown = ref(8)

onMounted(() => {
  const interval = setInterval(() => {
    countdown.value--
    if (countdown.value === 0) {
      clearInterval(interval)
      router.push('/home')
    }
  }, 1000)
})
</script>

<style scoped lang="scss">
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}

.error-card {
  background: #fff;
  padding: 2rem 3rem;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 400px;
}

.error-card h1 {
  color: #e74c3c;
  margin-bottom: 1rem;
}

.error-card p {
  margin: 0.5rem 0;
  color: #555;
}

.btn-home {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.6rem 1.2rem;
  background: #3498db;
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  transition: background 0.3s;
}

.btn-home:hover {
  background: #2980b9;
}
</style>
