<template>
  <button
    :class="[
      // Base styles
      'relative inline-flex items-center justify-center font-medium overflow-hidden',
      'focus:outline-none focus-ring press-effect',
      'disabled:opacity-60 disabled:cursor-not-allowed disabled:shadow-none',
      'transition-all duration-250 ease-smooth',
      
      // Size variations
      sizeClasses[size],
      
      // Variant styles
      variantClasses[variant],
      
      // Full width
      block ? 'w-full' : '',
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
    v-bind="$attrs"
  >
    <!-- Ripple effect container -->
    <span 
      v-if="ripples.length > 0" 
      class="absolute inset-0 overflow-hidden rounded-[inherit]"
    >
      <span
        v-for="ripple in ripples"
        :key="ripple.id"
        class="absolute rounded-full bg-white/30 animate-ripple"
        :style="{
          left: `${ripple.x}px`,
          top: `${ripple.y}px`,
          width: '20px',
          height: '20px',
        }"
      />
    </span>

    <!-- Content -->
    <span :class="['relative z-10 flex items-center justify-center gap-2', loading && 'opacity-0']">
      <component
        :is="iconLeft"
        v-if="iconLeft && !loading"
        :class="['flex-shrink-0', iconSizes[size]]"
      />
      <slot />
      <component
        :is="iconRight"
        v-if="iconRight && !loading"
        :class="['flex-shrink-0', iconSizes[size]]"
      />
    </span>

    <!-- Loading spinner -->
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <svg
        class="spinner"
        :class="iconSizes[size]"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </span>

    <!-- Gradient overlay for primary variant -->
    <span 
      v-if="variant === 'primary' && !disabled && !loading" 
      class="absolute inset-0 bg-gradient-to-r from-primary-600 to-primary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-250 rounded-[inherit]"
    />
  </button>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'outline', 'ghost', 'danger', 'success', 'white'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value),
  },
  block: Boolean,
  loading: Boolean,
  disabled: Boolean,
  iconLeft: [Object, Function, String],
  iconRight: [Object, Function, String],
})

const ripples = ref([])

const handleClick = (e) => {
  if (props.disabled || props.loading) return

  // Create ripple effect
  const button = e.currentTarget
  const rect = button.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const ripple = {
    id: Date.now(),
    x: x - 10,
    y: y - 10,
  }

  ripples.value.push(ripple)

  // Remove ripple after animation
  setTimeout(() => {
    ripples.value = ripples.value.filter(r => r.id !== ripple.id)
  }, 600)
}

const sizeClasses = {
  xs: 'px-2.5 py-1 text-xs rounded-md gap-1',
  sm: 'px-3.5 py-1.5 text-sm rounded-md gap-1.5',
  md: 'px-4 py-2 text-sm rounded-lg gap-2',
  lg: 'px-5 py-2.5 text-base rounded-lg gap-2',
  xl: 'px-6 py-3 text-base rounded-xl gap-2.5',
}

const iconSizes = {
  xs: 'w-3.5 h-3.5',
  sm: 'w-4 h-4',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
  xl: 'w-5 h-5',
}

const variantClasses = {
  primary: [
    'bg-gradient-to-br from-primary-600 to-primary-700',
    'text-white shadow-primary-sm',
    'hover:shadow-primary hover:-translate-y-0.5',
    'active:translate-y-0 active:shadow-primary-sm',
    'border border-primary-700/50',
  ].join(' '),
  
  secondary: [
    'bg-primary-50 text-primary-700 border border-primary-200',
    'hover:bg-primary-100 hover:border-primary-300',
    'active:bg-primary-200',
  ].join(' '),
  
  outline: [
    'bg-white text-gray-700 border-2 border-gray-300',
    'hover:bg-gray-50 hover:border-gray-400 hover:shadow-sm',
    'active:bg-gray-100',
  ].join(' '),
  
  ghost: [
    'bg-transparent text-gray-700',
    'hover:bg-gray-100',
    'active:bg-gray-200',
  ].join(' '),
  
  danger: [
    'bg-gradient-to-br from-error-600 to-error-700',
    'text-white shadow-sm',
    'hover:shadow-md hover:-translate-y-0.5',
    'active:translate-y-0',
    'border border-error-700/50',
  ].join(' '),
  
  success: [
    'bg-gradient-to-br from-success-600 to-success-700',
    'text-white shadow-sm',
    'hover:shadow-md hover:-translate-y-0.5',
    'active:translate-y-0',
    'border border-success-700/50',
  ].join(' '),
  
  white: [
    'bg-white text-gray-900 border border-gray-200 shadow-sm',
    'hover:bg-gray-50 hover:shadow',
    'active:bg-gray-100',
  ].join(' '),
}
</script>
