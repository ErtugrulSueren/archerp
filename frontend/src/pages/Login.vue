<template>
  <div class="login-page">
    <!-- Animated Background -->
    <div class="login-bg">
      <div class="login-bg__grid"></div>
      <div class="login-bg__glow login-bg__glow--1"></div>
      <div class="login-bg__glow login-bg__glow--2"></div>
    </div>

    <div class="login-container">
      <!-- Logo & Branding -->
      <div class="login-brand">
        <div class="login-brand__logo">
          <span class="login-brand__letter">A</span>
        </div>
        <h1 class="login-brand__name">ArcERP</h1>
        <p class="login-brand__tagline">İşletme Yönetim Platformu</p>
      </div>

      <!-- Login Card -->
      <div class="login-card">
        <h2 class="login-card__title">Giriş Yap</h2>
        <p class="login-card__subtitle">Hesabınıza erişmek için bilgilerinizi girin</p>

        <!-- Error -->
        <div v-if="error" class="login-error">
          <svg class="login-error__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <span>{{ error }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Username -->
          <div class="login-field">
            <label class="login-field__label" for="login-user">Kullanıcı Adı</label>
            <div class="login-field__input-wrap">
              <svg class="login-field__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
              <input 
                id="login-user"
                v-model="username" 
                type="text" 
                class="login-field__input"
                placeholder="E-posta veya kullanıcı adı"
                required 
                autocomplete="username"
              />
            </div>
          </div>
          
          <!-- Password -->
          <div class="login-field">
            <label class="login-field__label" for="login-pass">Şifre</label>
            <div class="login-field__input-wrap">
              <svg class="login-field__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input 
                id="login-pass"
                v-model="password" 
                type="password" 
                class="login-field__input"
                placeholder="••••••••"
                required 
                autocomplete="current-password"
              />
            </div>
          </div>

          <!-- Submit -->
          <button type="submit" :disabled="loading" class="login-submit">
            <span v-if="loading" class="login-submit__spinner"></span>
            <span>{{ loading ? 'Giriş yapılıyor...' : 'Giriş Yap' }}</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="login-footer">© {{ new Date().getFullYear() }} ArcERP. Tüm hakları saklıdır.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { call } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await call('login', {
      usr: username.value,
      pwd: password.value
    })
    
    // Force reload to update app state properly
    window.location.href = '/frontend/workspace'
  } catch (e) {
    console.error(e)
    error.value = 'Giriş başarısız: ' + (e.message || 'Bilinmeyen hata')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PAGE ROOT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: #0b1120;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ANIMATED BACKGROUND
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.login-bg__grid {
  position: absolute;
  inset: 0;
  opacity: 0.04;
  background-image:
    linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 60px 60px;
}

.login-bg__glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.15;
  animation: login-float 12s ease-in-out infinite alternate;
}

.login-bg__glow--1 {
  width: 500px;
  height: 500px;
  background: #3b82f6;
  top: -150px;
  right: -100px;
}

.login-bg__glow--2 {
  width: 400px;
  height: 400px;
  background: #8b5cf6;
  bottom: -100px;
  left: -80px;
  animation-delay: -6s;
}

@keyframes login-float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, -20px) scale(1.1); }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CONTAINER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-container {
  position: relative;
  width: 100%;
  max-width: 420px;
  animation: login-enter 600ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes login-enter {
  0% {
    opacity: 0;
    transform: translateY(24px) scale(0.97);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BRANDING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-brand {
  text-align: center;
  margin-bottom: 32px;
}

.login-brand__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  border-radius: 18px;
  box-shadow:
    0 8px 32px rgba(59, 130, 246, 0.35),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  margin-bottom: 16px;
}

.login-brand__letter {
  font-size: 28px;
  font-weight: 800;
  color: white;
  letter-spacing: -1px;
}

.login-brand__name {
  font-size: 28px;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -0.5px;
  margin: 0 0 4px 0;
}

.login-brand__tagline {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  font-weight: 400;
}

@media (max-width: 480px) {
  .login-brand {
    margin-bottom: 24px;
  }

  .login-brand__logo {
    width: 56px;
    height: 56px;
    border-radius: 16px;
  }

  .login-brand__letter {
    font-size: 24px;
  }

  .login-brand__name {
    font-size: 24px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LOGIN CARD
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.login-card__title {
  font-size: 22px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 4px 0;
}

.login-card__subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 28px 0;
}

@media (max-width: 480px) {
  .login-card {
    padding: 28px 22px;
    border-radius: 16px;
  }

  .login-card__title {
    font-size: 20px;
  }

  .login-card__subtitle {
    margin-bottom: 22px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ERROR
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 10px;
  color: #fca5a5;
  font-size: 13px;
  margin-bottom: 20px;
  animation: login-shake 400ms ease;
}

.login-error__icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: #f87171;
}

@keyframes login-shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FORM FIELDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login-field__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.login-field__input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.login-field__icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #475569;
  transition: color 200ms;
  pointer-events: none;
}

.login-field__input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: all 200ms ease;
}

.login-field__input::placeholder {
  color: #475569;
}

.login-field__input:focus {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.login-field__input:focus ~ .login-field__icon,
.login-field__input-wrap:focus-within .login-field__icon {
  color: #60a5fa;
}

@media (max-width: 480px) {
  .login-field__input {
    padding: 11px 12px 11px 40px;
    font-size: 16px; /* Prevents iOS zoom */
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SUBMIT BUTTON
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 13px 20px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 250ms ease;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
  margin-top: 4px;
}

.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(59, 130, 246, 0.4);
}

.login-submit:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.login-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-submit__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: login-spin 600ms linear infinite;
}

@keyframes login-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .login-submit {
    padding: 14px 20px;
    font-size: 16px;
    border-radius: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FOOTER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.login-footer {
  text-align: center;
  font-size: 12px;
  color: #334155;
  margin: 24px 0 0 0;
}
</style>
