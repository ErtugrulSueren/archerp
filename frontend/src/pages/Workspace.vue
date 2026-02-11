<template>
  <div class="ws-page">
    <!-- Background -->
    <div class="ws-bg">
      <div class="ws-bg__pattern"></div>
    </div>

    <div class="ws-container">
      <!-- Greeting & Search -->
      <div class="ws-hero">
        <!-- Top Actions -->
        <div class="ws-hero__actions">
          <SessionDefaultsDropdown />
          <button @click="logout" class="ws-hero__logout" title="Çıkış Yap">
            <FeatherIcon name="log-out" class="ws-hero__logout-icon" />
          </button>
        </div>

        <h1 class="ws-hero__greeting">
          Hoşgeldin, <span class="ws-hero__user">{{ sessionUser }}</span>
        </h1>
        <p class="ws-hero__subtitle">Bugün ne üzerinde çalışmak istersiniz?</p>
        
        <div class="ws-search">
          <div class="ws-search__icon-wrap">
            <FeatherIcon name="search" class="ws-search__icon" />
          </div>
          <input 
            ref="searchInput"
            type="text" 
            v-model="searchQuery"
            placeholder="Modül, rapor veya işlem ara..." 
            class="ws-search__input"
            autofocus
          >
          <div class="ws-search__kbd-wrap">
            <kbd class="ws-search__kbd">CTRL K</kbd>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="ws-loading">
        <div class="ws-loading__spinner"></div>
      </div>

      <!-- Content -->
      <div v-else class="ws-content">

        <!-- Search Results -->
        <div v-if="searchQuery">
          <transition-group 
            name="ws-list" 
            tag="div" 
            class="ws-grid ws-grid--search"
          >
            <router-link 
              v-for="app in filteredApps" 
              :key="app.uniqueKey"
              :to="app.route"
              class="ws-app-tile"
              :style="{ '--tile-color': app.color }"
            >
              <div class="ws-app-tile__icon">
                <FeatherIcon :name="app.icon" class="ws-app-tile__icon-svg" />
              </div>
              <h3 class="ws-app-tile__label">{{ app.label }}</h3>
              <span class="ws-app-tile__category">{{ app.category }}</span>
            </router-link>
          </transition-group>

          <div v-if="filteredApps.length === 0" class="ws-empty">
            <FeatherIcon name="search" class="ws-empty__icon" />
            <span class="ws-empty__text">Sonuç bulunamadı.</span>
          </div>
        </div>

        <!-- Default Navigation -->
        <div v-else>
          <transition name="ws-fade" mode="out-in">

            <!-- LEVEL 1: Module Grid -->
            <div v-if="!activeModule" key="modules" class="ws-grid ws-grid--modules">
              <div 
                v-for="module in processedModules" 
                :key="module.name"
                @click="setActiveModule(module)"
                class="ws-module-card"
                :style="{ '--mod-color': getColor(module.modul_adi) }"
              >
                <div class="ws-module-card__glow"></div>
                <div class="ws-module-card__icon">
                  <FeatherIcon :name="module.ikon || 'box'" class="ws-module-card__icon-svg" />
                </div>
                <div class="ws-module-card__info">
                  <h2 class="ws-module-card__name">{{ module.modul_adi }}</h2>
                  <p class="ws-module-card__count">{{ module.all_items.length }} İşlem</p>
                </div>
                <div class="ws-module-card__arrow">
                  <FeatherIcon name="arrow-right" class="ws-module-card__arrow-icon" />
                </div>
              </div>
            </div>

            <!-- LEVEL 2: Module Items -->
            <div v-else key="items">
              <!-- Back Header -->
              <div class="ws-back-header">
                <button @click="activeModule = null" class="ws-back-header__btn">
                  <FeatherIcon name="arrow-left" class="ws-back-header__btn-icon" />
                </button>
                <div class="ws-back-header__info">
                  <div class="ws-back-header__dot" :style="{ background: getColor(activeModule.modul_adi) }"></div>
                  <div>
                    <h2 class="ws-back-header__title">{{ activeModule.modul_adi }}</h2>
                    <p class="ws-back-header__sub">Modül işlemleri</p>
                  </div>
                </div>
              </div>
              
              <!-- Items Grid -->
              <div class="ws-grid ws-grid--items">
                <router-link 
                  v-for="item in activeModule.all_items"
                  :key="item.uniqueKey"
                  :to="item.route"
                  class="ws-item-tile"
                >
                  <div class="ws-item-tile__icon">
                    <FeatherIcon :name="item.icon || 'circle'" class="ws-item-tile__icon-svg" />
                  </div>
                  <span class="ws-item-tile__label">{{ item.label }}</span>
                </router-link>
                
                <div v-if="activeModule.all_items.length === 0" class="ws-empty ws-empty--full">
                  <FeatherIcon name="inbox" class="ws-empty__icon" />
                  <span class="ws-empty__text">Bu modülde henüz bir işlem tanımlanmamış.</span>
                </div>
              </div>
            </div>

          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { call, FeatherIcon } from 'frappe-ui'
import { useSidebar } from '@/composables/useSidebar'
import SessionDefaultsDropdown from '@/components/SessionDefaultsDropdown.vue'

const user = ref('Kullanıcı')
const sessionUser = computed(() => user.value)

const searchQuery = ref('')
const searchInput = ref(null)
const { modules, fetchMenu, loading } = useSidebar()
const activeModule = ref(null)

const setActiveModule = (mod) => {
    activeModule.value = mod
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(searchQuery, (val) => {
    if (val) activeModule.value = null
})

// Color palette (CSS-friendly hex values instead of Tailwind classes)
const colorPalette = [
    '#3b82f6', '#10b981', '#f97316', '#6366f1',
    '#f43f5e', '#a855f7', '#06b6d4', '#ec4899',
    '#14b8a6', '#f59e0b', '#d946ef', '#84cc16'
]

const getColor = (str) => {
    let hash = 0
    if (!str) return colorPalette[0]
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colorPalette[Math.abs(hash) % colorPalette.length]
}

const getRoute = (item) => {
    if (item.hedef_rota) {
        const qIdx = item.hedef_rota.indexOf('?')
        if (qIdx !== -1) {
            const path = item.hedef_rota.substring(0, qIdx)
            const query = {}
            const params = new URLSearchParams(item.hedef_rota.substring(qIdx + 1))
            params.forEach((val, key) => { query[key] = val })
            return { path, query }
        }
        return item.hedef_rota
    }
    switch (item.turu) {
        case 'DocType':
            if (item.ilgili_doctype) return `/auto/${item.ilgili_doctype}`
            break
        case 'Rapor':
            if (item.ilgili_rapor) return `/report/${item.ilgili_rapor}`
            break
    }
    if (item.ilgili_doctype) return `/auto/${item.ilgili_doctype}`
    return null
}

const processedModules = computed(() => {
    if (!modules.value) return []
    
    return modules.value.map(mod => {
        const all_items = []
        
        if (mod.items) {
            mod.items.forEach(item => {
                const route = getRoute(item)
                if (route) {
                    all_items.push({
                        label: item.etiket,
                        icon: item.ikon || 'circle',
                        route: route,
                        uniqueKey: `${mod.name}-${item.idx}`
                    })
                }
            })
        }
        
        if (mod.grouped_items) {
            Object.keys(mod.grouped_items).forEach(groupName => {
                mod.grouped_items[groupName].forEach(item => {
                    const route = getRoute(item)
                    if (route) {
                        all_items.push({
                            label: item.etiket,
                            icon: item.ikon || 'circle',
                            route: route,
                            uniqueKey: `${mod.name}-${groupName}-${item.etiket}`
                        })
                    }
                })
            })
        }
        
        return { ...mod, all_items }
    })
})

const filteredApps = computed(() => {
    if (!searchQuery.value) return []
    
    const apps = []
    processedModules.value.forEach(mod => {
        mod.all_items.forEach(item => {
            apps.push({
                ...item,
                category: mod.modul_adi,
                color: getColor(mod.modul_adi)
            })
        })
    })
    
    const query = searchQuery.value.toLowerCase()
    return apps.filter(app => 
        app.label.toLowerCase().includes(query) || 
        app.category.toLowerCase().includes(query)
    )
})

const handleKeydown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        searchInput.value?.focus()
    }
}

onMounted(async () => {
    window.addEventListener('keydown', handleKeydown)
    try {
        const u = await call('frappe.auth.get_logged_user')
        if (u) user.value = u
        
        if (!modules.value.length) {
            await fetchMenu()
        }
    } catch (e) {
        console.error(e)
    }
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})

async function logout() {
    try {
        await call('logout')
        window.location.href = '/frontend/login'
    } catch(e) {
        window.location.href = '/frontend/login'
    }
}
</script>

<style scoped>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PAGE ROOT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
  background: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.ws-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.ws-bg__pattern {
  position: absolute;
  inset: 0;
  opacity: 0.4;
  background:
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.06) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CONTAINER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-container {
  position: relative;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HERO / GREETING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-hero {
  text-align: center;
  margin-bottom: 48px;
  position: relative;
}

.ws-hero__actions {
  position: absolute;
  right: 0;
  top: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.ws-hero__logout {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: none;
  background: transparent;
  color: #94a3b8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 200ms;
}

.ws-hero__logout:hover {
  color: #ef4444;
  background: #fef2f2;
}

.ws-hero__logout-icon {
  width: 16px;
  height: 16px;
}

.ws-hero__greeting {
  font-size: 42px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -1px;
  margin: 0 0 8px 0;
  line-height: 1.1;
}

.ws-hero__user {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.ws-hero__subtitle {
  font-size: 18px;
  color: #94a3b8;
  font-weight: 400;
  margin: 0;
}

@media (max-width: 768px) {
  .ws-hero {
    margin-bottom: 32px;
    padding-top: 44px;
  }

  .ws-hero__greeting {
    font-size: 28px;
    letter-spacing: -0.5px;
  }

  .ws-hero__subtitle {
    font-size: 15px;
  }

  .ws-hero__actions {
    top: 0;
    right: 0;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SEARCH
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-search {
  position: relative;
  max-width: 600px;
  margin: 28px auto 0;
}

.ws-search__icon-wrap {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  padding-left: 18px;
  pointer-events: none;
}

.ws-search__icon {
  width: 20px;
  height: 20px;
  color: #94a3b8;
  transition: color 200ms;
}

.ws-search__input {
  width: 100%;
  padding: 14px 60px 14px 52px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 16px;
  font-family: inherit;
  color: #0f172a;
  outline: none;
  transition: all 250ms ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.ws-search__input::placeholder {
  color: #94a3b8;
}

.ws-search__input:focus {
  border-color: #3b82f6;
  box-shadow: 0 4px 24px rgba(59, 130, 246, 0.1), 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.ws-search__input:focus ~ .ws-search__icon-wrap .ws-search__icon {
  color: #3b82f6;
}

.ws-search__kbd-wrap {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  padding-right: 14px;
}

.ws-search__kbd {
  display: inline-block;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-family: inherit;
}

@media (max-width: 768px) {
  .ws-search {
    margin-top: 20px;
  }

  .ws-search__input {
    font-size: 16px;
    padding: 13px 16px 13px 48px;
    border-radius: 14px;
  }

  .ws-search__kbd-wrap {
    display: none;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LOADING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-loading {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.ws-loading__spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: ws-spin 700ms linear infinite;
}

@keyframes ws-spin {
  to { transform: rotate(360deg); }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CONTENT & GRIDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-content {
  min-height: 300px;
}

.ws-grid {
  display: grid;
  gap: 20px;
}

.ws-grid--modules {
  grid-template-columns: repeat(3, 1fr);
}

.ws-grid--items,
.ws-grid--search {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 1024px) {
  .ws-grid--modules {
    grid-template-columns: repeat(2, 1fr);
  }
  .ws-grid--items,
  .ws-grid--search {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .ws-grid {
    gap: 12px;
  }

  .ws-grid--modules {
    grid-template-columns: repeat(2, 1fr);
  }

  .ws-grid--items,
  .ws-grid--search {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MODULE CARD (Level 1)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-module-card {
  position: relative;
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  text-align: center;
}

.ws-module-card:hover {
  border-color: transparent;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.03);
  transform: translateY(-3px);
}

.ws-module-card__glow {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--mod-color);
  opacity: 0.06;
  transition: opacity 300ms;
  pointer-events: none;
}

.ws-module-card:hover .ws-module-card__glow {
  opacity: 0.12;
}

.ws-module-card__icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--mod-color);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--mod-color) 30%, transparent);
  transition: transform 300ms;
}

.ws-module-card:hover .ws-module-card__icon {
  transform: scale(1.08);
}

.ws-module-card__icon-svg {
  width: 26px;
  height: 26px;
  color: white;
}

.ws-module-card__info {
  min-width: 0;
}

.ws-module-card__name {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.ws-module-card__count {
  font-size: 13px;
  color: #94a3b8;
  margin: 4px 0 0 0;
  font-weight: 500;
}

.ws-module-card__arrow {
  position: absolute;
  bottom: 16px;
  right: 16px;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 300ms;
  color: #cbd5e1;
}

.ws-module-card:hover .ws-module-card__arrow {
  opacity: 1;
  transform: translateX(0);
}

.ws-module-card__arrow-icon {
  width: 18px;
  height: 18px;
}

@media (max-width: 640px) {
  .ws-module-card {
    padding: 20px 16px;
    gap: 12px;
    border-radius: 14px;
  }

  .ws-module-card__icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .ws-module-card__icon-svg {
    width: 22px;
    height: 22px;
  }

  .ws-module-card__name {
    font-size: 14px;
  }

  .ws-module-card__count {
    font-size: 12px;
  }

  .ws-module-card__arrow {
    display: none;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BACK HEADER (Level 2)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-back-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.ws-back-header__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: white;
  border-radius: 12px;
  color: #64748b;
  cursor: pointer;
  transition: all 200ms;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.ws-back-header__btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.ws-back-header__btn-icon {
  width: 20px;
  height: 20px;
}

.ws-back-header__info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ws-back-header__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ws-back-header__title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.ws-back-header__sub {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

@media (max-width: 640px) {
  .ws-back-header__title {
    font-size: 18px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ITEM TILE (Level 2)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-item-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 24px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  text-decoration: none;
  transition: all 250ms ease;
}

.ws-item-tile:hover {
  border-color: #bfdbfe;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
  transform: translateY(-2px);
}

.ws-item-tile__icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  transition: all 200ms;
}

.ws-item-tile:hover .ws-item-tile__icon {
  background: #eff6ff;
}

.ws-item-tile__icon-svg {
  width: 20px;
  height: 20px;
  color: #64748b;
  transition: color 200ms;
}

.ws-item-tile:hover .ws-item-tile__icon-svg {
  color: #3b82f6;
}

.ws-item-tile__label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  line-height: 1.3;
}

.ws-item-tile:hover .ws-item-tile__label {
  color: #0f172a;
}

@media (max-width: 640px) {
  .ws-item-tile {
    padding: 18px 12px;
    border-radius: 12px;
  }

  .ws-item-tile__icon {
    width: 40px;
    height: 40px;
    margin-bottom: 10px;
  }

  .ws-item-tile__label {
    font-size: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SEARCH RESULT TILE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-app-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 24px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  text-decoration: none;
  transition: all 300ms ease;
}

.ws-app-tile:hover {
  border-color: transparent;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.07);
  transform: translateY(-3px);
}

.ws-app-tile__icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--tile-color);
  margin-bottom: 12px;
  transition: transform 300ms;
  box-shadow: 0 3px 10px color-mix(in srgb, var(--tile-color) 25%, transparent);
}

.ws-app-tile:hover .ws-app-tile__icon {
  transform: scale(1.1);
}

.ws-app-tile__icon-svg {
  width: 22px;
  height: 22px;
  color: white;
}

.ws-app-tile__label {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  line-height: 1.3;
  margin-bottom: 6px;
}

.ws-app-tile__category {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #94a3b8;
}

@media (max-width: 640px) {
  .ws-app-tile {
    padding: 18px 12px;
  }

  .ws-app-tile__icon {
    width: 42px;
    height: 42px;
  }

  .ws-app-tile__label {
    font-size: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   EMPTY STATE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-empty {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94a3b8;
  text-align: center;
}

.ws-empty__icon {
  width: 32px;
  height: 32px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.ws-empty__text {
  font-size: 14px;
}

.ws-empty--full {
  border: 2px dashed #e2e8f0;
  border-radius: 14px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TRANSITIONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ws-fade-enter-active,
.ws-fade-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.ws-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.ws-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* List Transitions (Search) */
.ws-list-enter-active,
.ws-list-leave-active {
  transition: all 400ms cubic-bezier(0.25, 0.8, 0.25, 1);
}

.ws-list-enter-from,
.ws-list-leave-to {
  opacity: 0;
  transform: translateY(15px);
}

.ws-list-move {
  transition: transform 400ms ease;
}
</style>
