<template>
  <Button
    v-bind="$attrs"
    :class="[
      'rounded-xl transition-all duration-200 active:scale-[0.98]',
      // Solid Variants (Primary)
      variant === 'solid' && theme !== 'gray' ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md hover:shadow-indigo-500/30 hover:-translate-y-0.5 border-t border-white/20' : '',
      
      // Gray Solid (Secondary Actions)
      variant === 'solid' && theme === 'gray' ? 'bg-white text-gray-700 border border-gray-200 shadow-sm hover:shadow-md hover:border-gray-300 hover:text-gray-900' : '',

      // Subtle/Ghost
      variant === 'subtle' || variant === 'ghost' ? 'hover:bg-gray-100/80 hover:text-gray-900' : '',
            
      // Sizes
      size === 'lg' ? 'px-6 py-2.5 text-base' : '',
      size === 'md' ? 'px-4 py-2 text-sm' : '',
      
      $attrs.class
    ]"
    :variant="variant"
    :theme="theme"
    :size="size"
  >
    <slot />
  </Button>
</template>

<script setup>
import { Button } from 'frappe-ui'

defineProps({
  variant: {
    type: String,
    default: 'solid'
  },
  theme: {
    type: String,
    default: 'gray'
  },
  size: {
    type: String,
    default: 'md'
  }
})
</script>
