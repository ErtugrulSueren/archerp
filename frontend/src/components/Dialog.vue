<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto overflow-x-hidden bg-gray-900/50 backdrop-blur-sm p-4 md:p-6"
        role="dialog"
        aria-modal="true"
        @click.self="closeOnOutsideClick && $emit('update:modelValue', false)"
      >
        <Transition name="scale">
          <div
            v-if="modelValue"
            class="relative w-full max-w-lg transform rounded-xl bg-white p-6 shadow-2xl transition-all"
            :class="maxWidthClass"
          >
             <div v-if="title" class="mb-5">
                <h3 class="text-xl font-semibold text-gray-900 leading-none">{{ title }}</h3>
             </div>
             
             <button
               v-if="showClose"
               @click="$emit('update:modelValue', false)"
               class="absolute top-4 right-4 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
               aria-label="Close"
             >
               <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
             </button>

             <div class="text-gray-600">
                <slot />
             </div>

             <div v-if="$slots.actions" class="mt-8 flex justify-end space-x-3">
               <slot name="actions" />
             </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  showClose: {
    type: Boolean,
    default: true
  },
  closeOnOutsideClick: {
    type: Boolean,
    default: true
  },
  maxWidth: {
    type: String,
    default: 'md' 
  }
})

defineEmits(['update:modelValue'])

const maxWidthClass = computed(() => {
  switch (props.maxWidth) {
    case 'sm': return 'max-w-sm'
    case 'md': return 'max-w-lg'
    case 'lg': return 'max-w-2xl'
    case 'xl': return 'max-w-4xl'
    case '2xl': return 'max-w-6xl'
    case 'full': return 'max-w-full'
    default: return 'max-w-lg'
  }
})

// Prevent scrolling when open
watch(() => props.modelValue, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
