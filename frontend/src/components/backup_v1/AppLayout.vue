<template>
  <div class="flex h-screen bg-gray-100 font-sans">
    <Sidebar :is-collapsed="isSidebarCollapsed" />

    <!-- Toast Container -->
    <Toast />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/50">
      <header class="h-20 bg-white/80 backdrop-blur border-b border-gray-100 flex items-center justify-between px-8 sticky top-0 z-10">
        <div class="flex items-center gap-4">
          <button 
            @click="isSidebarCollapsed = !isSidebarCollapsed"
            class="p-2 -ml-2 rounded-lg text-slate-500 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-200 transform transition-transform duration-200"
            :class="{ 'rotate-180': isSidebarCollapsed }"
          >
            <!-- Menu Icon -->
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </button>
          
          <h2 class="text-2xl font-bold text-slate-800 tracking-tight">{{ pageTitle }}</h2>
        </div>
        
        <!-- Top right area (User profile, notifications etc) -->
        <div class="flex items-center gap-4">
            <div class="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs font-bold">
                U
            </div>
        </div>
      </header>

      <main class="flex-1 overflow-auto p-8 scroll-smooth">
        <div :class="['mx-auto', contentWidth]">
            <slot></slot>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import Toast from '@/components/Toast.vue'

const route = useRoute()
const isSidebarCollapsed = ref(false)

const pageTitle = computed(() => {
  if (route.path === '/') return 'Ana Sayfa'
  if (route.path === '/urunler') return 'Ürün Yönetimi'
  return ''
})

defineProps({
  contentWidth: {
    type: String,
    default: 'max-w-7xl'
  }
})
</script>
