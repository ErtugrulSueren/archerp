<template>
  <div
    :class="[
      'relative inline-flex items-center justify-center overflow-hidden flex-shrink-0',
      'rounded-full bg-gradient-to-br transition-transform duration-200',
      sizeClasses[size],
      colorClasses[color],
      ring && 'ring-2 ring-offset-2 ring-white',
      statusRing && statusRingClasses[status],
      hoverable && 'hover:scale-105 cursor-pointer',
    ]"
  >
    <!-- Image -->
    <img
      v-if="src && !imageError"
      :src="src"
      :alt="alt || label"
      class="h-full w-full object-cover"
      @error="imageError = true"
    />

    <!-- Initials fallback -->
    <span
      v-else
      :class="[
        'font-semibold select-none',
        textSizeClasses[size],
      ]"
    >
      {{ initials }}
    </span>

    <!-- Status indicator -->
    <span
      v-if="status"
      :class="[
        'absolute bottom-0 right-0 block rounded-full',
        'ring-2 ring-white',
        statusSizeClasses[size],
        statusColorClasses[status],
      ]"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  src: String,
  alt: String,
  label: String,
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['xs', 'sm', 'md', 'lg', 'xl', '2xl'].includes(v),
  },
  color: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'gray', 'success', 'warning', 'error'].includes(v),
  },
  status: {
    type: String,
    validator: (v) => ['online', 'offline', 'away', 'busy'].includes(v),
  },
  ring: Boolean,
  statusRing: Boolean,
  hoverable: Boolean,
})

const imageError = ref(false)

const initials = computed(() => {
  if (!props.label) return '?'
  return props.label
    .split(' ')
    .map((word) => word[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const sizeClasses = {
  xs: 'h-6 w-6',
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16',
  '2xl': 'h-24 w-24',
}

const textSizeClasses = {
  xs: 'text-xs',
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-xl',
  '2xl': 'text-3xl',
}

const colorClasses = {
  primary: 'from-primary-500 to-primary-600 text-white',
  gray: 'from-gray-300 to-gray-400 text-gray-700',
  success: 'from-success-500 to-success-600 text-white',
  warning: 'from-warning-500 to-warning-600 text-white',
  error: 'from-error-500 to-error-600 text-white',
}

const statusSizeClasses = {
  xs: 'h-1.5 w-1.5',
  sm: 'h-2 w-2',
  md: 'h-2.5 w-2.5',
  lg: 'h-3 w-3',
  xl: 'h-3.5 w-3.5',
  '2xl': 'h-4 w-4',
}

const statusColorClasses = {
  online: 'bg-success-500',
  offline: 'bg-gray-400',
  away: 'bg-warning-500',
  busy: 'bg-error-500',
}

const statusRingClasses = {
  online: 'ring-success-500/30',
  offline: 'ring-gray-400/30',
  away: 'ring-warning-500/30',
  busy: 'ring-error-500/30',
}
</script>
