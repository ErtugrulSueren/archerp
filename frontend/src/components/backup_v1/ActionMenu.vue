<template>
  <div class="relative inline-block text-left" ref="container">
    <div @click="toggle">
      <slot name="trigger">
        <button type="button" class="inline-flex justify-center w-full rounded-xl border border-slate-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-slate-700 hover:bg-slate-50 focus:outline-none">
          {{ label }}
          <svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </slot>
    </div>

    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="isOpen" class="origin-top-right absolute right-0 mt-2 w-56 rounded-xl shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
        <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
            <div 
                v-for="(option, index) in options" 
                :key="index"
                @click="select(option)"
                class="block px-4 py-3 text-base text-slate-700 hover:bg-slate-50 hover:text-slate-900 cursor-pointer flex items-center gap-2"
                role="menuitem"
            >
                <component :is="option.icon" v-if="option.icon && typeof option.icon === 'object'" class="w-5 h-5 text-slate-400" />
                {{ option.label }}
            </div>
            <slot></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: 'Options'
  },
  options: {
    type: Array, // [{ label: 'Edit', action: () => {}, icon: ... }]
    default: () => []
  }
})

const isOpen = ref(false)
const container = ref(null)

function toggle() {
    isOpen.value = !isOpen.value
}

function select(option) {
    if (option.action) option.action()
    isOpen.value = false
}

function handleClickOutside(event) {
    if (container.value && !container.value.contains(event.target)) {
        isOpen.value = false
    }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>
