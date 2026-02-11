<template>
  <div
    :class="[
      // Base styles
      'bg-white rounded-xl border overflow-hidden transition-all duration-300',
      'flex flex-col',
      
      // Premium effects
      variant === 'default' && 'border-gray-200 shadow-sm hover:shadow-md',
      variant === 'elevated' && 'border-gray-100 shadow-md hover:shadow-lg',
      variant === 'glass' && 'glass border-white/20 shadow-lg',
      variant === 'gradient-border' && 'gradient-border shadow-md',
      
      // Hover lift
      hoverable && 'hover-lift cursor-pointer',
      
      // Padding variant
      noPadding && 'p-0',
    ]"
    @click="$emit('click', $event)"
  >
    <!-- Header with gradient background option -->
    <div
      v-if="title || $slots.header || $slots.actions"
      :class="[
        'px-6 py-4 border-b flex items-center justify-between shrink-0',
        headerGradient
          ? 'bg-gradient-to-r from-primary-50 to-primary-100/50 border-primary-100'
          : 'bg-gray-50/50 border-gray-100',
      ]"
    >
      <div class="flex items-center gap-3 flex-1">
        <div v-if="$slots.icon" class="flex-shrink-0">
          <slot name="icon" />
        </div>
        <div class="flex-1 min-w-0">
          <h3 v-if="title" class="text-lg font-semibold text-gray-900 truncate">
            {{ title }}
          </h3>
          <p v-if="subtitle" class="text-sm text-gray-500 truncate mt-0.5">
            {{ subtitle }}
          </p>
          <slot name="header" />
        </div>
      </div>
      
      <div v-if="$slots.actions" class="flex-shrink-0 ml-4">
        <slot name="actions" />
      </div>
    </div>

    <!-- Body -->
    <div :class="['flex-1', noPadding ? '' : 'p-6']">
      <slot />
    </div>

    <!-- Footer -->
    <div
      v-if="$slots.footer"
      class="px-6 py-4 bg-gray-50/50 border-t border-gray-100 shrink-0"
    >
      <slot name="footer" />
    </div>

    <!-- Loading shimmer overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50 rounded-xl"
    >
      <div class="flex flex-col items-center gap-3">
        <svg
          class="spinner w-8 h-8 text-primary-600"
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
        <p v-if="loadingText" class="text-sm text-gray-600">{{ loadingText }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  subtitle: String,
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'elevated', 'glass', 'gradient-border'].includes(v),
  },
  headerGradient: Boolean,
  hoverable: Boolean,
  noPadding: Boolean,
  loading: Boolean,
  loadingText: String,
})

defineEmits(['click'])
</script>
