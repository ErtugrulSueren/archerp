<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5 font-medium rounded-full transition-all duration-200',
      sizeClasses[size],
      variantClasses[variant],
      dot && 'pl-2',
      dismissible && 'pr-1.5',
      pulseOnNew && 'animate-pulse-slow',
    ]"
  >
    <!-- Dot indicator -->
    <span
      v-if="dot"
      :class="[
        'relative flex h-2 w-2',
        pulse && 'animate-pulse',
      ]"
    >
      <span
        v-if="pulse"
        :class="[
          'absolute inline-flex h-full w-full rounded-full opacity-75',
          dotColorClasses[variant],
        ]"
      ></span>
      <span
        :class="[
          'relative inline-flex rounded-full h-2 w-2',
          dotColorClasses[variant],
        ]"
      ></span>
    </span>

    <!-- Content -->
    <span class="truncate">
      <slot />
    </span>

    <!-- Dismiss button -->
    <button
      v-if="dismissible"
      @click="$emit('dismiss')"
      type="button"
      class="inline-flex flex-shrink-0 rounded-full p-0.5 hover:bg-black/10 focus:outline-none focus:ring-2 focus:ring-white/50 transition-colors"
    >
      <span class="sr-only">Dismiss</span>
      <svg class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
        <path
          d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
        />
      </svg>
    </button>
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'gray',
    validator: (v) => ['gray', 'primary', 'success', 'warning', 'error', 'info'].includes(v),
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
  dot: Boolean,
  pulse: Boolean,
  dismissible: Boolean,
  pulseOnNew: Boolean,
})

defineEmits(['dismiss'])

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
  lg: 'px-3 py-1 text-sm',
}

const variantClasses = {
  gray: 'bg-gray-100 text-gray-700 ring-1 ring-gray-200/50',
  primary: 'bg-primary-100 text-primary-700 ring-1 ring-primary-200/50',
  success: 'bg-success-100 text-success-700 ring-1 ring-success-200/50',
  warning: 'bg-warning-100 text-warning-700 ring-1 ring-warning-200/50',
  error: 'bg-error-100 text-error-700 ring-1 ring-error-200/50',
  info: 'bg-info-100 text-info-700 ring-1 ring-info-200/50',
}

const dotColorClasses = {
  gray: 'bg-gray-500',
  primary: 'bg-primary-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  error: 'bg-error-500',
  info: 'bg-info-500',
}
</script>
