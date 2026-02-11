<template>
    <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-10 shrink-0">
        <!-- Left: Page Title / Breadcrumbs -->
        <div class="flex items-center">
            <h2 class="text-lg font-semibold text-gray-900">{{ currentRouteName }}</h2>
        </div>

        <!-- Right: Actions -->
        <div class="flex items-center space-x-2">
            <!-- Session Defaults -->
            <SessionDefaultsDropdown />
            
            <!-- Notifications -->
            <button class="p-2 text-gray-400 hover:text-gray-500 rounded-full hover:bg-gray-100 focus:outline-none transition-colors">
                <span class="sr-only">Notifications</span>
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
            </button>
        </div>
    </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import SessionDefaultsDropdown from './SessionDefaultsDropdown.vue'

const route = useRoute()
const currentRouteName = computed(() => {
    if (route.name === 'DesignSystem') return 'Design System'
    return route.name
})
</script>
