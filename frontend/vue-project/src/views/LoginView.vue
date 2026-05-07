<template>
  <div class="login-page bg-puente ">
    <!-- Overlay oscuro sobre la imagen -->
    <div class="bg-overlay" />

    <!-- Partículas decorativas
    <div class="particles">
      <span v-for="n in 12" :key="n" class="particle" :style="particleStyle(n)" />
    </div> -->

    <!-- Card flotante glassmorphism -->
    <div class="login-wrapper">
      <div class="glass-card">

        <!-- Logo / Nombre empresa -->
        <div class="brand-area">
          <div class="brand-icon">
            <img src="@/assets/logoaguas.png" alt="Logo" class="logo-image" />
          </div>
          <h2 class="brand-name">Aguas Rionegrinas SA</h2>
          <p class="brand-tagline">Explotación de recursos hídricos</p>
        </div>

        <!-- Separador -->
        <div class="divider" />

        <!-- Formulario -->
        <div class="form-area">
          <!-- Mensaje de error -->
          <transition name="fade-slide">
            <div v-if="errorMsg" class="error-banner" role="alert">
              <svg viewBox="0 0 20 20" fill="currentColor" class="error-icon" aria-hidden="true">
                <path fill-rule="evenodd" d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <span>{{ errorMsg }}</span>
            </div>
          </transition>

          <!-- Username -->
          <div class="input-group" :class="{ focused: focus.username, filled: form.username }">
            <label class="input-label" for="username">Usuario</label>
            <div class="input-wrapper">
              <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
              </svg>
              <input
                id="username"
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
            <label class="input-label" for="password">Contraseña</label>
            <div class="input-wrapper">
              <svg class="input-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
              </svg>
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="glass-input"
                placeholder="Ingresa tu contraseña"
                autocomplete="current-password"
                @focus="focus.password = true"
                @blur="focus.password = false"
                @keyup.enter="handleLogin"
              />
              <button
                class="toggle-password"
                type="button"
                :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                @click="showPassword = !showPassword"
                tabindex="-1"
              >
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
            <span class="btn-text">
              <template v-if="!isLoading">
                <svg viewBox="0 0 20 20" fill="currentColor" class="btn-icon" aria-hidden="true">
                  <path fill-rule="evenodd" d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                INGRESAR
              </template>
              <template v-else>
                <svg class="spinner" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="20 60"/>
                </svg>
                Verificando...
              </template>
            </span>
          </button>
        </div>

        <!-- Footer del card -->
        <p class="card-footer">Sistema de gestión corporativo</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {useAuthStore}  from '@/stores/authStore'
import router from '@/router/router'

// ─── Estado ──────────────────────────────────────────────────────────────
const form         = reactive({ username: '', password: '' })
const focus        = reactive({ username: false, password: false })
const isLoading    = ref(false)
const errorMsg     = ref('')
const showPassword = ref(false)
const authStore    = useAuthStore()

// ─── Login ────────────────────────────────────────────────────────────────
async function handleLogin() {
  if (isLoading.value || !form.username || !form.password) return
  errorMsg.value = ''
  isLoading.value = true
  try {
    
    const response = await authStore.login(form.username, form.password)
    console.log("respuesta del login:", response)

    if (response){
      // Redirigir a home o dashboard después del login exitoso
      router.push({ name: 'home' })
    }
    
  } catch (err: any) {
    const serverError = err.response?.data?.error;
    if (serverError && serverError.includes("'NoneType' object has no attribute 'close'")) {
      errorMsg.value = "La base de datos esta en mantenimiento. Consulte con el departamento de sistemas.";
    } else if (err.code === 'ERR_NETWORK') {
      errorMsg.value = "El servidor no responde. Es posible que esté en mantenimiento. Consulte con el departamento de sistemas.";
    } else {
      errorMsg.value = serverError || 'El servidor no responde. Es posible que esté en mantenimiento. Consulte con el departamento de sistemas.';
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* ─── Google Fonts ──────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500&display=swap');

/* ─── Variables ─────────────────────────────────────────────────────────── */
:root {
  --accent:       #7dd3fc;
  --text-primary: rgba(255, 255, 255, 0.88); 
  --text-muted:   rgba(255, 255, 255, 0.78);
  --input-bg:     rgba(255, 255, 255, 0.98);
  --input-border: rgba(255, 255, 255, 0.22);
  --input-focus:  rgba(125, 211, 252, 0.60);
  --card-bg:      rgba(255, 255, 255, 0.6);
  --card-border:  rgba(255, 255, 255, 0.20);
  --error-text:   rgba(255, 255, 255, 0.98);
  --error-bg:     rgba(239, 68, 68, 0.25);
  --error-border: rgba(252, 165, 165, 0.5);
}

/* ─── Reset ──────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* imagen */
.bg-puente {
  background-image: url('@/assets/portadapuente.jpg');
  background-size: cover;
  background-position: center;
  width: 100%;
  height: 100vh; /* ocupa toda la pantalla */
}

/* ─── Página ─────────────────────────────────────────────────────────────── */
.login-page {
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  min-height: 100dvh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  /* Respeta notches en dispositivos móviles */
  padding: env(safe-area-inset-top, 0px) env(safe-area-inset-right, 0px)
           env(safe-area-inset-bottom, 0px) env(safe-area-inset-left, 0px);
}

/* Overlay */
.bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.72) 0%,
    rgba(0, 0, 0, 0.50) 50%,
    rgba(0, 0, 0, 0.78) 100%
  );
  backdrop-filter: blur(1.5px);
  z-index: 0;
}

/* ─── Wrapper ────────────────────────────────────────────────────────────── */
.login-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 480px;
  min-width: 280px;
  padding: 0 16px;
  animation: cardEnter 0.65s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
@keyframes cardEnter {
  from { opacity: 0; transform: translateY(28px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}

/* ─── Card ───────────────────────────────────────────────────────────────── */
.glass-card {
  background: rgba(15, 23, 42, 0.4) !important;
  backdrop-filter: blur(28px) saturate(180%); 
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  /*backdrop-filter:none;  Evita problemas de rendimiento en móviles antiguos */
  border: 1px solid var(--card-border);
  border-radius: clamp(16px, 3vw, 24px);
  padding: clamp(24px, 5vw, 44px) clamp(20px, 5vw, 44px) clamp(20px, 4vw, 36px);
  box-shadow:
    0 14px 60px rgba(0, 0, 0, 0.60),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset,
    0 1px 0   rgba(255, 255, 255, 0.12) inset;
}

/* ─── Brand ──────────────────────────────────────────────────────────────── */
.brand-area {
  text-align: center;
  margin-bottom: clamp(16px, 3vw, 24px);
  animation: fadeSlideUp 0.55s 0.15s both;
}
.brand-icon {
  display: flex;
  justify-content: center;
  margin-bottom: clamp(8px, 1.5vw, 14px);
}
.logo-image {
  width:  clamp(48px, 8vw, 68px);
  height: clamp(48px, 8vw, 68px);
  object-fit: contain;
  filter: drop-shadow(0 0 14px rgba(125, 211, 252, 0.38));
  border-radius: 50%;
}
.brand-name {
  font-family: 'Rajdhani', sans-serif;
  font-size: clamp(0.95rem, 2.5vw, 1.15rem);
  font-weight: 700;
  letter-spacing: 0.18em;
  color: rgba(255, 255, 255, 0.88) !important;
  text-transform: uppercase;
  margin: 0 0 0.3rem;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.55);
  word-break: break-word;
}
.brand-tagline {
  font-size: clamp(0.72rem, 1.8vw, 0.82rem);
  color: rgba(255, 255, 255, 0.88) !important;
  margin: 0;
  letter-spacing: 0.05em;
}

/* ─── Divider ────────────────────────────────────────────────────────────── */
.divider {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(125, 211, 252, 0.30) 30%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(125, 211, 252, 0.30) 70%,
    transparent 100%
  );
  margin-bottom: clamp(16px, 3vw, 28px);
}

/* ─── Formulario ─────────────────────────────────────────────────────────── */
.form-area {
  display: flex;
  flex-direction: column;
  gap: clamp(12px, 2.5vw, 18px);
}
.input-group { display: flex; flex-direction: column; gap: 6px; }

.input-label {
  font-size: clamp(0.68rem, 1.6vw, 0.74rem);
  font-weight: 600;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.88);
  transition: color 0.2s;
  white-space: nowrap;
}
.input-group.focused .input-label {
  color: var(--accent);
  text-shadow: 0 0 6px rgba(125, 211, 252, 0.35);
}

.input-wrapper { position: relative; display: flex; align-items: center; }

.input-icon {
  position: absolute;
  left: 13px;
  width: 15px;
  height: 15px;
  color: rgba(255, 255, 255, 0.50);
  pointer-events: none;
  transition: color 0.2s;
  flex-shrink: 0;
}
.input-group.focused .input-icon { color: var(--accent); }

.glass-input {
  width: 100%;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 11px;
  padding: clamp(10px, 1.8vw, 13px) clamp(36px, 6vw, 44px) clamp(10px, 1.8vw, 13px) clamp(34px, 5.5vw, 42px);
  /* font-size >= 16px evita zoom automático en iOS al hacer focus */
  font-size: max(16px, clamp(0.875rem, 2vw, 0.95rem));
  font-family: 'Inter', sans-serif;
  color:  rgba(255, 255, 255, 0.95);
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s, background 0.25s;
}
.glass-input::placeholder { color: rgba(255, 255, 255, 0.45); }
.glass-input:focus {
  border-color: var(--input-focus);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.13), 0 2px 8px rgba(0, 0, 0, 0.22);
}
.glass-input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 100px rgba(10, 14, 35, 0.88) inset;
  -webkit-text-fill-color: var(--text-primary);
}

/* Área táctil mínima 44×44 px */
.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.52);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  min-width: 36px;
  min-height: 36px;
  transition: color 0.2s;
}
.toggle-password:hover { color: var(--accent); }
.toggle-password svg   { width: 16px; height: 16px; }

/* ─── Error ──────────────────────────────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(239, 68, 68, 0.25);
  border: 1px solid rgba(252, 165, 165, 0.5);
  border-radius: 10px;
  padding: 10px 13px;
  font-size: clamp(0.78rem, 1.8vw, 0.84rem);
  color: rgba(255, 255, 255, 0.88) !important;
  line-height: 1.45;
  word-break: break-word;
}
.error-icon { width: 15px; height: 15px; flex-shrink: 0; margin-top: 2px; }

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-6px); }

/* ─── Botón ──────────────────────────────────────────────────────────────── */
.login-btn {
  margin-top: 4px;
  width: 100%;
  min-height: 48px;   /* área táctil cómoda */
  padding: clamp(11px, 2vw, 14px) 16px;
  border: none;
  border-radius: 11px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: #fff;
  font-family: 'Rajdhani', sans-serif;
  font-size: clamp(0.95rem, 2.2vw, 1.05rem);
  font-weight: 700;
  letter-spacing: 0.14em;
  cursor: pointer;
  transition: transform 0.22s, box-shadow 0.22s, opacity 0.22s;
  box-shadow: 0 4px 22px rgba(59, 130, 246, 0.40);
  position: relative;
  overflow: hidden;
}
.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.14) 0%, transparent 55%);
  opacity: 0;
  transition: opacity 0.2s;
}
.login-btn:hover:not(:disabled)::before { opacity: 1; }
.login-btn:hover:not(:disabled)         { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(59,130,246,0.52); }
.login-btn:active:not(:disabled)        { transform: translateY(0); }
.login-btn:disabled                     { opacity: 0.42; cursor: not-allowed; box-shadow: none; }

.btn-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  pointer-events: none;
}
.btn-icon { width: 16px; height: 16px; flex-shrink: 0; }

.spinner { width: 18px; height: 18px; animation: spin 0.8s linear infinite; flex-shrink: 0; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ─── Footer ─────────────────────────────────────────────────────────────── */
.card-footer {
  text-align: center;
  font-size: clamp(0.68rem, 1.5vw, 0.75rem);
  color: rgba(255, 255, 255, 0.62);
  margin: clamp(14px, 2.5vw, 22px) 0 0;
  letter-spacing: 0.05em;
}

/* ─── Animaciones ────────────────────────────────────────────────────────── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════════
   BREAKPOINTS
   ═══════════════════════════════════════════════ */

/* Móvil muy chico < 360px */
@media (max-width: 359px) {
  .login-wrapper { padding: 0 10px; }
  .brand-name    { letter-spacing: 0.10em; }
}

/* Móvil 360–479px: permitir scroll si teclado virtual sube */
@media (max-width: 479px) {
  .login-page {
    align-items: flex-start;
    padding-top:    max(20px, env(safe-area-inset-top, 20px));
    padding-bottom: max(20px, env(safe-area-inset-bottom, 20px));
  }
  .login-wrapper { margin: auto 0; }
  .glass-card    { border-radius: 18px; }
}

/* Tablet 768px+ */
@media (min-width: 768px) {
  .login-wrapper { max-width: 460px; }
}

/* Desktop grande 1280px+ */
@media (min-width: 1280px) {
  .login-wrapper { max-width: 500px; }
}

/* Landscape móvil (altura reducida) */
@media (max-height: 600px) and (orientation: landscape) {
  .login-page  { align-items: flex-start; padding-top: 14px; padding-bottom: 14px; }
  .brand-area  { margin-bottom: 10px; }
  .logo-image  { width: 40px; height: 40px; }
  .divider     { margin-bottom: 10px; }
  .form-area   { gap: 9px; }
  .card-footer { margin-top: 10px; }
}
</style>