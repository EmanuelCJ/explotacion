<template>
  <div class="login-page" :style="backgroundStyle">
    <!-- Overlay oscuro sobre la imagen -->
    <div class="bg-overlay" />

    <!-- Partículas decorativas -->
    <div class="particles">
      <span v-for="n in 12" :key="n" class="particle" :style="particleStyle(n)" />
    </div>

    <!-- Card flotante glassmorphism -->
    <div class="login-wrapper">
      <div class="glass-card">

        <!-- Logo / Nombre empresa -->
        <div class="brand-area">
          <div class="brand-icon">
            <img v-if="bgImage" :src="logoaguas" alt="Logo" class="logo-image" width="50px" />
            <!-- <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="20" cy="20" r="18" stroke="rgba(255,255,255,0.8)" stroke-width="1.5"/>
              <path d="M12 20 L20 12 L28 20 L20 28 Z" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.7)" stroke-width="1.2"/>
              <circle cx="20" cy="20" r="4" fill="rgba(255,255,255,0.6)"/>
            </svg> -->
          </div>
          <h2 class="brand-name">Aguas Rionegrinas SA</h2>
          <p class="brand-tagline">Explotacion de recursos hídricos</p>
        </div>

        <!-- Separador -->
        <div class="divider" />

        <!-- Formulario -->
        <div class="form-area">
          <!-- Mensaje de error -->
          <transition name="fade-slide">
            <div v-if="errorMsg" class="error-banner">
              <svg viewBox="0 0 20 20" fill="currentColor" class="error-icon">
                <path fill-rule="evenodd" d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              {{ errorMsg }}
            </div>
          </transition>

          <!-- Username -->
          <div class="input-group" :class="{ focused: focus.username, filled: form.username }">
            <label class="input-label">Usuario</label>
            <div class="input-wrapper">
              <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
              </svg>
              <input
                v-model="form.username"
                type="text"
                class="glass-input"
                placeholder="Ingresa tu usuario"
                autocomplete="username"
                @focus="focus.username = true"
                @blur="focus.username = false"
                @keyup.enter="handleLogin"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="input-group" :class="{ focused: focus.password, filled: form.password }">
            <label class="input-label">Contraseña</label>
            <div class="input-wrapper">
              <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
              </svg>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="glass-input"
                placeholder="Ingresa tu contraseña"
                autocomplete="current-password"
                @focus="focus.password = true"
                @blur="focus.password = false"
                @keyup.enter="handleLogin"
              />
              <button class="toggle-password" type="button" @click="showPassword = !showPassword" tabindex="-1">
                <svg v-if="!showPassword" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                </svg>
                <svg v-else viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                  <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.064 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Botón Login -->
          <button
            class="login-btn"
            :class="{ loading: isLoading }"
            :disabled="isLoading || !form.username || !form.password"
            @click="handleLogin"
          >
            <span v-if="!isLoading" class="btn-text">
              <svg viewBox="0 0 20 20" fill="currentColor" class="btn-icon">
                <path fill-rule="evenodd" d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              INGRESAR
            </span>
            <span v-else class="btn-text">
              <svg class="spinner" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="20 60" />
              </svg>
              Verificando...
            </span>
          </button>
        </div>

        <!-- Footer del card -->
        <p class="card-footer">Sistema de gestión corporativo</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import router from '@/router'
import { auth } from '@/api/inventario'
import puente from '@/assets/portadapuente.jpg'
import logoaguas from '@/assets/a CIR.png'

// ─── Estado ────────────────────────────────────────────────────────────────
const form = reactive({ username: '', password: '' })
const focus = reactive({ username: false, password: false })
const isLoading = ref(false)
const errorMsg = ref('')
const showPassword = ref(false)
const bgImage = ref(puente)   // URL de la imagen de fondo cargada por el usuario
const iconImage = ref(logoaguas)    // URL de la imagen del logo cargada por el usuario
const bgInput = ref(null)
// const connection = inventario() // Instancia de la API de inventario (si necesitas hacer llamadas desde aquí)


// ─── URL base de la API Flask ────────────────────────────────────────────
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// ─── Fondo dinámico ──────────────────────────────────────────────────────
const backgroundStyle = computed(() => ({
  backgroundImage: bgImage.value
    ? `url(${bgImage.value})`
    : 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
}))

function onBgChange(e) {
  const file = e.target.files[0]
  if (!file) return
  bgImage.value = URL.createObjectURL(file)
}

// ─── Partículas decorativas ──────────────────────────────────────────────
function particleStyle(n) {
  const sizes = [4, 6, 3, 8, 5, 4, 7, 3, 6, 4, 5, 8]
  const delays = [0, 1.2, 2.4, 0.6, 3, 1.8, 0.3, 2.1, 3.6, 1.5, 2.7, 0.9]
  return {
    width: `${sizes[n - 1]}px`,
    height: `${sizes[n - 1]}px`,
    left: `${(n * 8.3) % 100}%`,
    top: `${(n * 13.7) % 100}%`,
    animationDelay: `${delays[n - 1]}s`,
  }
}

// ─── Login ────────────────────────────────────────────────────────────────
async function handleLogin() {
  if (isLoading.value || !form.username || !form.password) return
  errorMsg.value = ''
  isLoading.value = true

  try {

    // Llamada a la función de autenticación osea al backend Flask
    const response = await auth(form.username, form.password)
    
    if (response['status'] === 200) {
      // Login exitoso, redirigir a la página principal
      router.push('/Home')
      console.log( response['usuario']) // aca deberia guardar la info en store
    } else {
      errorMsg.value = response['error']
    }
  } catch (err) {
    if (err.response) {
      errorMsg.value = err.response.data.error || 'No se recibió respuesta del servidor. Verificá tu conexión.'
    } else {
      errorMsg.value = 'Ocurrió un error inesperado.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* ─── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

/* ─── Variables ─────────────────────────────────────────────────────────── */
:root {
  --glass-bg: rgba(255, 255, 255, 0.08);
  --glass-border: rgba(255, 255, 255, 0.18);
  --glass-shadow: rgba(0, 0, 0, 0.4);
  --accent: #7dd3fc;
  --accent-glow: rgba(125, 211, 252, 0.35);
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.55);
  --input-bg: rgba(255, 255, 255, 0.07);
  --input-border: rgba(255, 255, 255, 0.15);
  --input-focus: rgba(125, 211, 252, 0.5);
  --error-color: #fca5a5;
  --error-bg: rgba(239, 68, 68, 0.15);
}

/* ─── Layout principal ──────────────────────────────────────────────────── */
.login-page {
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  transition: background-image 0.6s ease;
}

/* Overlay semi-oscuro sobre la imagen */
.bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.35) 50%,
    rgba(0, 0, 0, 0.60) 100%
  );
  backdrop-filter: blur(1px);
  z-index: 0;
}

/* ─── Partículas ────────────────────────────────────────────────────────── */
.particles { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(125, 211, 252, 0.25);
  animation: floatUp 8s ease-in-out infinite;
}
@keyframes floatUp {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.3; }
  50%       { transform: translateY(-40px) scale(1.3); opacity: 0.7; }
}

/* ─── Wrapper / Card ────────────────────────────────────────────────────── */
.login-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 440px;
  padding: 1rem;
  animation: cardEnter 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
@keyframes cardEnter {
  from { opacity: 0; transform: translateY(30px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0)   scale(1); }
}

.glass-card {
  background: rgba(15, 20, 40, 0.45);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 2.5rem 2.2rem 2rem;
  box-shadow:
    0 8px 40px var(--glass-shadow),
    0 0 0 1px rgba(255,255,255,0.04) inset,
    0 1px 0 rgba(255,255,255,0.1) inset;
}

/* ─── Brand ─────────────────────────────────────────────────────────────── */
.brand-area {
  text-align: center;
  margin-bottom: 1.5rem;
  animation: fadeIn 0.6s 0.2s both;
}
.brand-icon svg {
  width: 48px;
  height: 48px;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 0 12px rgba(125,211,252,0.4));
}
.brand-name {
  font-family: 'Rajdhani', sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 0.22em;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin: 0 0 0.3rem;
}
.brand-tagline {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin: 0;
  letter-spacing: 0.04em;
}

/* ─── Divider ───────────────────────────────────────────────────────────── */
.divider {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 10%,
    rgba(125,211,252,0.3) 30%,
    rgba(255,255,255,0.15) 50%,
    rgba(125,211,252,0.3) 70%,
    transparent 50%
  );
  margin-bottom: 1.8rem;
}

/* ─── Form ──────────────────────────────────────────────────────────────── */
.form-area { display: flex; flex-direction: column; gap: 1.1rem; }

.input-group { display: flex; flex-direction: column; gap: 0.4rem; }

.input-label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-secondary);
  transition: color 0.2s;
}
.input-group.focused .input-label { color: var(--accent); }

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
  pointer-events: none;
  transition: color 0.2s;
  flex-shrink: 0;
}
.input-group.focused .input-icon { color: var(--accent); }

.glass-input {
  width: 100%;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  padding: 0.78rem 2.8rem 0.78rem 2.6rem;
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s, background 0.25s;
}
.glass-input::placeholder { color: rgba(255,255,255,0.25); }
.glass-input:focus {
  border-color: var(--input-focus);
  background: rgba(255,255,255,0.10);
  box-shadow: 0 0 0 3px rgba(125,211,252,0.12), 0 2px 8px rgba(0,0,0,0.2);
}
/* Autofill Chrome */
.glass-input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 100px rgba(15,20,40,0.85) inset;
  -webkit-text-fill-color: var(--text-primary);
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  transition: color 0.2s;
}
.toggle-password:hover { color: var(--accent); }
.toggle-password svg { width: 16px; height: 16px; }

/* ─── Error banner ──────────────────────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--error-bg);
  border: 1px solid rgba(252, 165, 165, 0.3);
  border-radius: 10px;
  padding: 0.65rem 0.9rem;
  font-size: 0.82rem;
  color: var(--error-color);
}
.error-icon { width: 15px; height: 15px; flex-shrink: 0; }

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(-6px); }
.fade-slide-leave-to   { opacity: 0; transform: translateY(-6px); }

/* ─── Botón Login ───────────────────────────────────────────────────────── */
.login-btn {
  margin-top: 0.4rem;
  width: 100%;
  padding: 0.85rem;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: #fff;
  font-family: 'Rajdhani', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 4px 20px rgba(59,130,246,0.4);
  position: relative;
  overflow: hidden;
}
.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.2s;
}
.login-btn:hover:not(:disabled)::before { opacity: 1; }
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(59,130,246,0.55);
}
.login-btn:active:not(:disabled) { transform: translateY(0); }
.login-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}
.btn-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.btn-icon { width: 16px; height: 16px; }

/* Spinner */
.spinner {
  width: 18px;
  height: 18px;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ─── Footer card ───────────────────────────────────────────────────────── */
.card-footer {
  text-align: center;
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin: 1.5rem 0 0;
  letter-spacing: 0.04em;
  opacity: 0.6;
}

/* ─── Botón cambiar fondo ───────────────────────────────────────────────── */
.hidden-input { display: none; }
.bg-change-btn {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(15, 20, 40, 0.55);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 50px;
  padding: 0.55rem 1rem 0.55rem 0.75rem;
  color: rgba(255,255,255,0.7);
  font-size: 0.78rem;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: all 0.2s;
}
.bg-change-btn:hover {
  background: rgba(59,130,246,0.35);
  color: #fff;
  border-color: rgba(125,211,252,0.4);
}
.bg-change-btn svg { width: 16px; height: 16px; }

/* ─── Animaciones auxiliares ────────────────────────────────────────────── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ─── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 480px) {
  .glass-card {
    padding: 2rem 1.4rem 1.6rem;
    border-radius: 20px;
  }
  .brand-name { font-size: 0.95rem; }
  .login-wrapper { padding: 0.75rem; }
  .bg-change-btn span { display: none; }
  .bg-change-btn { padding: 0.6rem; border-radius: 50%; }
}

@media (min-width: 1024px) {
  .glass-card {
    padding: 3rem 2.8rem 2.4rem;
  }
}
</style>