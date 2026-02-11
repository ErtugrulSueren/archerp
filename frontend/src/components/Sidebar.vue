<template>
  <!-- ─── Mobile Backdrop ─── -->
  <transition name="backdrop-fade">
    <div 
      v-if="activeModule && isMobileOpen" 
      class="sidebar-backdrop"
      @click="closeMobileSidebar"
    ></div>
  </transition>

  <!-- ─── Sidebar ─── -->
  <aside 
    v-if="activeModule"
    class="sidebar-root"
    :class="[
      isSidebarCollapsed ? 'sidebar--collapsed' : 'sidebar--expanded',
      isMobileOpen ? 'sidebar--mobile-open' : ''
    ]"
  >
    <!-- ─── Logo Section ─── -->
    <div class="sidebar-logo" :class="isSidebarCollapsed ? 'sidebar-logo--collapsed' : ''">
      <router-link to="/workspace" class="sidebar-logo__link" title="Çalışma Alanına Dön" @click="closeMobileSidebar">
        <div class="sidebar-logo__icon">
          <img 
            v-if="logoUrl" 
            :src="logoUrl" 
            alt="Logo" 
            class="sidebar-logo__img"
          />
          <FeatherIcon v-else name="hexagon" class="sidebar-logo__fallback-icon" />
        </div>
        <transition name="sidebar-fade">
          <span v-if="!isSidebarCollapsed" class="sidebar-logo__text">ARC ERP</span>
        </transition>
      </router-link>

      <!-- Mobile close button -->
      <button class="sidebar-logo__close" @click="closeMobileSidebar">
        <FeatherIcon name="x" class="sidebar-logo__close-icon" />
      </button>
    </div>

    <!-- ─── Module Header ─── -->
    <div class="sidebar-module" v-if="activeModule">
      <div v-if="!isSidebarCollapsed" class="sidebar-module__expanded">
        <div class="sidebar-module__icon-wrap">
          <FeatherIcon :name="activeModule.ikon || 'layers'" class="sidebar-module__icon" />
        </div>
        <div class="sidebar-module__info">
          <span class="sidebar-module__label">Aktif Modül</span>
          <h3 class="sidebar-module__name">{{ activeModule.modul_adi }}</h3>
        </div>
      </div>
      <div v-else class="sidebar-module__collapsed" :title="activeModule.modul_adi">
        <div class="sidebar-module__icon-wrap sidebar-module__icon-wrap--sm">
          <FeatherIcon :name="activeModule.ikon || 'layers'" class="sidebar-module__icon" />
        </div>
      </div>
    </div>

    <!-- ─── Navigation ─── -->
    <nav class="sidebar-nav">

      <!-- Ungrouped Items -->
      <div v-if="activeModule.items && activeModule.items.length > 0" class="sidebar-nav__section">
        <div v-for="item in activeModule.items" :key="item.etiket">
          <router-link
            v-if="getRoute(item)"
            :to="getRoute(item)"
            class="sidebar-nav__item"
            :class="{
              'sidebar-nav__item--active': isActive(getRoute(item)),
              'sidebar-nav__item--collapsed': isSidebarCollapsed
            }"
            :title="isSidebarCollapsed ? item.etiket : ''"
            @click="onNavClick"
          >
            <span class="sidebar-nav__indicator"></span>
            <FeatherIcon :name="item.ikon || 'circle'" class="sidebar-nav__icon" />
            <span v-if="!isSidebarCollapsed" class="sidebar-nav__label">{{ item.etiket }}</span>
          </router-link>
        </div>
      </div>

      <!-- Grouped Items -->
      <div 
        v-for="(items, groupName) in activeModule.grouped_items" 
        :key="groupName" 
        class="sidebar-nav__section"
      >
        <div v-if="!isSidebarCollapsed" class="sidebar-nav__group-title">
          {{ groupName }}
        </div>
        <div v-else class="sidebar-nav__group-divider"></div>

        <div v-for="item in items" :key="item.etiket">
          <router-link
            v-if="getRoute(item)"
            :to="getRoute(item)"
            class="sidebar-nav__item"
            :class="{
              'sidebar-nav__item--active': isActive(getRoute(item)),
              'sidebar-nav__item--collapsed': isSidebarCollapsed
            }"
            :title="isSidebarCollapsed ? item.etiket : ''"
            @click="onNavClick"
          >
            <span class="sidebar-nav__indicator"></span>
            <FeatherIcon :name="item.ikon || 'circle'" class="sidebar-nav__icon" />
            <span v-if="!isSidebarCollapsed" class="sidebar-nav__label">{{ item.etiket }}</span>
          </router-link>
        </div>
      </div>
    </nav>

    <!-- ─── Footer ─── -->
    <div class="sidebar-footer">
      <!-- User Profile -->
      <div class="sidebar-user" :class="isSidebarCollapsed ? 'sidebar-user--collapsed' : ''">
        <div class="sidebar-user__avatar">
          {{ userInitials }}
        </div>
        <div v-if="!isSidebarCollapsed" class="sidebar-user__info">
          <p class="sidebar-user__name">{{ userName }}</p>
          <button @click="logout" class="sidebar-user__logout">
            <FeatherIcon name="log-out" class="sidebar-user__logout-icon" />
            <span>Çıkış</span>
          </button>
        </div>
      </div>

      <!-- Collapse Toggle (desktop only) -->
      <button @click="toggleSidebar" class="sidebar-toggle" title="Menüyü Daralt/Genişlet">
        <FeatherIcon 
          :name="isSidebarCollapsed ? 'chevrons-right' : 'chevrons-left'" 
          class="sidebar-toggle__icon"
        />
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useSidebar } from '@/composables/useSidebar'
import { useRoute } from 'vue-router'
import { onMounted, ref, computed, watch } from 'vue'
import { call, FeatherIcon } from 'frappe-ui'

const { 
  modules, loading, activeModule, resolveActiveModule, 
  isSidebarCollapsed, isMobileOpen, 
  toggleSidebar, toggleMobileSidebar, closeMobileSidebar, 
  fetchMenu 
} = useSidebar()

const route = useRoute()
const userName = ref('Administrator')
const logoUrl = ref('')

const userInitials = computed(() => {
  const parts = userName.value.split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return userName.value.substring(0, 2).toUpperCase()
})

// Close mobile sidebar on navigation
function onNavClick() {
  closeMobileSidebar()
}

onMounted(async () => {
    try {
        const user = await call('frappe.auth.get_logged_user')
        if (user) userName.value = user
        
        await fetchMenu()
        resolveActiveModule(route.path, route.query.module)
    } catch(e) {
        console.error('Sidebar mount error:', e)
    }
})

watch(() => [route.path, route.query.module], ([newPath, newModule]) => {
    resolveActiveModule(newPath, newModule)
})

watch(modules, (newModules) => {
    if (newModules && newModules.length > 0) {
        resolveActiveModule(route.path, route.query.module)
    }
})

function getRoute(item) {
    let path = null
    let extraQuery = {}
    if (item.hedef_rota) {
        // Parse query params from hedef_rota (e.g. "/auto/Hesap?account_type=Nakit (Cash)")
        const qIdx = item.hedef_rota.indexOf('?')
        if (qIdx !== -1) {
            path = item.hedef_rota.substring(0, qIdx)
            const params = new URLSearchParams(item.hedef_rota.substring(qIdx + 1))
            params.forEach((val, key) => { extraQuery[key] = val })
        } else {
            path = item.hedef_rota
        }
    } else if (item.turu === 'DocType' && item.ilgili_doctype) {
        path = `/auto/${item.ilgili_doctype}`
    } else if (item.turu === 'Rapor' && item.ilgili_rapor) {
        path = `/report/${item.ilgili_rapor}`
    } else if (item.ilgili_doctype) {
        path = `/auto/${item.ilgili_doctype}`
    }
    if (!path) return null

    const moduleName = activeModule.value?.name || activeModule.value?.modul_adi
    const query = { ...extraQuery }
    if (moduleName) query.module = moduleName

    if (Object.keys(query).length > 0) {
        return { path, query }
    }
    return path
}

function isActive(routeTarget) {
    if (!routeTarget) return false
    // routeTarget can be a string or { path, query } object
    const targetPath = typeof routeTarget === 'string' ? routeTarget : routeTarget.path
    const decoded = decodeURIComponent(route.path)
    const decodedTarget = decodeURIComponent(targetPath)
    return decoded === decodedTarget || decoded.startsWith(decodedTarget + '/')
}

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
   BACKDROP (Mobile only)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-backdrop {
  display: none;
}

@media (max-width: 768px) {
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 49;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ROOT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-root {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 50;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1),
              transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.sidebar--expanded { width: 280px; }
.sidebar--collapsed { width: 72px; }

/* Mobile: hidden by default, slide in from left */
@media (max-width: 768px) {
  .sidebar-root {
    width: 280px !important;
    transform: translateX(-100%);
  }

  .sidebar--mobile-open {
    transform: translateX(0);
  }

  /* On mobile, always show expanded state */
  .sidebar--collapsed {
    width: 280px !important;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LOGO
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.sidebar-logo--collapsed {
  padding: 0;
  justify-content: center;
}

@media (max-width: 768px) {
  .sidebar-logo {
    padding: 0 16px;
    justify-content: space-between;
  }
  .sidebar-logo--collapsed {
    padding: 0 16px;
    justify-content: space-between;
  }
}

.sidebar-logo__link {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  width: 100%;
  transition: opacity 200ms;
}

.sidebar-logo__link:hover {
  opacity: 0.85;
}

.sidebar-logo--collapsed .sidebar-logo__link {
  justify-content: center;
  gap: 0;
}

@media (max-width: 768px) {
  .sidebar-logo--collapsed .sidebar-logo__link {
    justify-content: flex-start;
    gap: 14px;
  }
}

.sidebar-logo__icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.sidebar-logo__img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.sidebar-logo__fallback-icon {
  width: 20px;
  height: 20px;
  color: white;
}

.sidebar-logo__text {
  font-size: 17px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.3px;
  white-space: nowrap;
}

/* Mobile close button */
.sidebar-logo__close {
  display: none;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  cursor: pointer;
  transition: all 200ms;
  flex-shrink: 0;
}

.sidebar-logo__close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.sidebar-logo__close-icon {
  width: 18px;
  height: 18px;
}

@media (max-width: 768px) {
  .sidebar-logo__close {
    display: flex;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MODULE HEADER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-module {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .sidebar-module {
    padding: 14px 16px;
  }
}

.sidebar-module__expanded {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-module__collapsed {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  /* On mobile, always show expanded module header */
  .sidebar-module__collapsed {
    display: none;
  }
}

.sidebar-module__icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.12);
  flex-shrink: 0;
}

.sidebar-module__icon-wrap--sm {
  width: 34px;
  height: 34px;
}

.sidebar-module__icon {
  width: 18px;
  height: 18px;
  color: #60a5fa;
}

.sidebar-module__info {
  min-width: 0;
}

.sidebar-module__label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #64748b;
  margin-bottom: 2px;
}

.sidebar-module__name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   NAVIGATION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 12px;
}

@media (max-width: 768px) {
  .sidebar-nav {
    padding: 8px 10px;
  }
}

.sidebar-nav__section {
  margin-bottom: 8px;
}

.sidebar-nav__group-title {
  padding: 16px 12px 6px 12px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #475569;
}

.sidebar-nav__group-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 12px 8px;
}

/* ── Nav Item ── */
.sidebar-nav__item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 450;
  color: #94a3b8;
  text-decoration: none;
  transition: all 200ms ease;
  margin-bottom: 2px;
}

.sidebar-nav__item--collapsed {
  justify-content: center;
  padding: 10px;
  gap: 0;
}

@media (max-width: 768px) {
  .sidebar-nav__item {
    padding: 11px 12px;
    font-size: 14px;
  }
  /* Override collapsed on mobile — always show full */
  .sidebar-nav__item--collapsed {
    justify-content: flex-start;
    padding: 11px 12px;
    gap: 12px;
  }
}

.sidebar-nav__item:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}

/* Active indicator bar */
.sidebar-nav__indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  border-radius: 0 3px 3px 0;
  background: #3b82f6;
  transition: height 200ms ease;
}

.sidebar-nav__item--active .sidebar-nav__indicator {
  height: 60%;
}

.sidebar-nav__item--active {
  color: #f1f5f9;
  background: rgba(59, 130, 246, 0.1);
}

.sidebar-nav__item--active .sidebar-nav__icon {
  color: #60a5fa;
  opacity: 1;
}

.sidebar-nav__icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 200ms ease, color 200ms ease;
}

.sidebar-nav__item:hover .sidebar-nav__icon {
  opacity: 1;
}

.sidebar-nav__label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Scrollbar */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}
.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}
.sidebar-nav:hover::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FOOTER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

/* ── User ── */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
}

.sidebar-user--collapsed {
  justify-content: center;
  padding: 14px 0;
  gap: 0;
}

@media (max-width: 768px) {
  .sidebar-user {
    padding: 14px 16px;
  }
  .sidebar-user--collapsed {
    justify-content: flex-start;
    padding: 14px 16px;
    gap: 12px;
  }
}

.sidebar-user__avatar {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
}

.sidebar-user__info {
  min-width: 0;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-user__name {
  font-size: 13px;
  font-weight: 500;
  color: #cbd5e1;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-user__logout {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #64748b;
  font-size: 11px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 200ms;
}

.sidebar-user__logout:hover {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
}

.sidebar-user__logout-icon {
  width: 13px;
  height: 13px;
}

/* ── Toggle ── */
.sidebar-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  background: transparent;
  color: #475569;
  cursor: pointer;
  transition: all 200ms;
}

.sidebar-toggle:hover {
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.03);
}

.sidebar-toggle__icon {
  width: 16px;
  height: 16px;
}

/* Hide collapse toggle on mobile */
@media (max-width: 768px) {
  .sidebar-toggle {
    display: none;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TRANSITIONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sidebar-fade-enter-active,
.sidebar-fade-leave-active {
  transition: opacity 200ms ease;
}
.sidebar-fade-enter-from,
.sidebar-fade-leave-to {
  opacity: 0;
}

.backdrop-fade-enter-active,
.backdrop-fade-leave-active {
  transition: opacity 300ms ease;
}
.backdrop-fade-enter-from,
.backdrop-fade-leave-to {
  opacity: 0;
}
</style>
