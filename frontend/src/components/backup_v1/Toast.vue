<template>
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-3 w-full max-w-sm pointer-events-none">
        <TransitionGroup 
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="transform translate-x-full opacity-0"
            enter-to-class="transform translate-x-0 opacity-100"
            leave-active-class="transition duration-200 ease-in"
            leave-from-class="transform translate-x-0 opacity-100"
            leave-to-class="transform translate-x-full opacity-0"
        >
            <div 
                v-for="toast in toasts" 
                :key="toast.id"
                class="pointer-events-auto bg-white rounded-xl shadow-xl border border-slate-100 p-4 flex items-start gap-4 overflow-hidden relative"
            >
                <!-- Status Line -->
                <div 
                    class="absolute left-0 top-0 bottom-0 w-1"
                    :class="{
                        'bg-green-500': toast.variant === 'success',
                        'bg-red-500': toast.variant === 'error',
                        'bg-yellow-500': toast.variant === 'warning',
                        'bg-blue-500': toast.variant === 'info',
                    }"
                ></div>

                <!-- Icon -->
                <div class="pt-0.5" :class="{
                        'text-green-600': toast.variant === 'success',
                        'text-red-600': toast.variant === 'error',
                        'text-yellow-600': toast.variant === 'warning',
                        'text-blue-600': toast.variant === 'info',
                }">
                     <svg v-if="toast.variant === 'success'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                     <svg v-else-if="toast.variant === 'error'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                </div>

                <!-- Content -->
                <div class="flex-1">
                    <h3 class="text-sm font-bold text-slate-800">{{ toast.title }}</h3>
                    <p class="text-sm text-slate-500 mt-1 leading-relaxed">{{ toast.text }}</p>
                </div>

                <!-- Close -->
                <button @click="remove(toast.id)" class="text-slate-400 hover:text-slate-600">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
        </TransitionGroup>
    </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()
</script>
