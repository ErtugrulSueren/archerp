<template>
  <span 
    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold transition-colors border"
    :class="colorClasses"
  >
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'gray',
    validator: (value) => ['gray', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'indigo', 'pink'].includes(value)
  },
  label: {
    type: String,
    default: ''
  }
})

const colorClasses = computed(() => {
  const variants = {
    gray: 'bg-gray-50 text-gray-600 ring-1 ring-inset ring-gray-500/10',
    red: 'bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/10',
    green: 'bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20',
    blue: 'bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-700/10',
    yellow: 'bg-yellow-50 text-yellow-800 ring-1 ring-inset ring-yellow-600/20',
    orange: 'bg-orange-50 text-orange-700 ring-1 ring-inset ring-orange-600/10',
    purple: 'bg-purple-50 text-purple-700 ring-1 ring-inset ring-purple-700/10',
    indigo: 'bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-700/10',
    pink: 'bg-pink-50 text-pink-700 ring-1 ring-inset ring-pink-700/10',
  }
  return variants[props.variant] || variants.gray
})
</script>
