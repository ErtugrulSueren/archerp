<template>
  <div v-if="isLoggedIn" class="flex min-h-screen bg-gray-50 font-sans text-gray-900">
    <Sidebar />

    <!-- Mobile hamburger button -->
    <button 
      v-if="activeModule && !isMobileOpen"
      @click="toggleMobileSidebar"
      class="mobile-menu-btn"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <div 
        class="flex-1 flex flex-col min-h-screen transition-[margin] duration-300 ease-in-out"
        :class="mainContentClass"
    >
      <Header v-if="$route.name !== 'Workspace'" />
      <main class="flex-1">
        <router-view></router-view>
      </main>
    </div>
    <Toast />
  </div>
  
  <div v-else class="h-screen w-full">
    <router-view></router-view>
    <Toast />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { call } from 'frappe-ui'
import Sidebar from '@/components/Sidebar.vue'
import Header from '@/components/Header.vue'
import Toast from '@/components/Toast.vue'
import { useSidebar } from '@/composables/useSidebar'
import { useRoute } from 'vue-router'

const isLoggedIn = ref(false)
const { isSidebarCollapsed, isMobileOpen, activeModule, toggleMobileSidebar } = useSidebar()
const route = useRoute()

const mainContentClass = computed(() => {
    // If we are in Workspace, full width (no margin)
    if (route.name === 'Workspace') return 'ml-0'
    
    // If no active module (sidebar hidden), full width
    if (!activeModule.value) return 'ml-0'
    
    // On desktop, apply margin based on sidebar state
    return isSidebarCollapsed.value ? 'desktop-ml-collapsed' : 'desktop-ml-expanded'
})

onMounted(async () => {
  try {
    const user = await call('frappe.auth.get_logged_user')
    isLoggedIn.value = user !== 'Guest'
  } catch (error) {
    isLoggedIn.value = false
  }
})
</script>

<style>
/* Desktop sidebar margins */
.desktop-ml-expanded {
  margin-left: 280px;
}

.desktop-ml-collapsed {
  margin-left: 72px;
}

/* Mobile: no margin, content takes full width */
@media (max-width: 768px) {
  .desktop-ml-expanded,
  .desktop-ml-collapsed {
    margin-left: 0 !important;
  }
}

/* Mobile hamburger button */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 14px;
  left: 14px;
  z-index: 40;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #334155;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 200ms;
}

.mobile-menu-btn:hover {
  background: #f8fafc;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }
}
</style>
