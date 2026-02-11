<template>
  <div
    :class="[
      'rounded-lg p-4 transition-all duration-250',
      typeClasses[type],
      dismissible && 'pr-12 relative',
    ]"
    role="alert"
  >
    <div class="flex items-start gap-3">
      <!-- Icon -->
      <div class="flex-shrink-0">
        <svg
          v-if="type === 'success'"
          class="h-5 w-5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
            clip-rule="evenodd"
          />
        </svg>
        <svg
          v-else-if="type === 'error'"
          class="h-5 w-5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
            clip-rule="evenodd"
          />
        </svg>
        <svg
          v-else-if="type === 'warning'"
          class="h-5 w-5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
            clip-rule="evenodd"
          />
        </svg>
        <svg
          v-else
          class="h-5 w-5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z"
            clip-rule="evenodd"
          />
        </svg>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <h3 v-if="title" class="text-sm font-semibold mb-1">{{ title }}</h3>
        <div class="text-sm">
          <slot />
        </div>
      </div>

      <!-- Dismiss button -->
      <button
        v-if="dismissible"
        @click="$emit('dismiss')"
        type="button"
        class="absolute top-3 right-3 inline-flex rounded-lg p-1.5 hover:bg-black/10 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors"
      >
        <span class="sr-only">Dismiss</span>
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path
            d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  type: {
    type: String,
    default: 'info',
    validator: (v) => ['success', 'error', 'warning', 'info'].includes(v),
  },
  dismissible: Boolean,
})

defineEmits(['dismiss'])

const typeClasses = {
  success: 'bg-success-50 text-success-900 border-l-4 border-success-500',
  error: 'bg-error-50 text-error-900 border-l-4 border-error-500',
  warning: 'bg-warning-50 text-warning-900 border-l-4 border-warning-500',
  info: 'bg-info-50 text-info-900 border-l-4 border-info-500',
}
</script>
