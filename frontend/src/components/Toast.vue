<template>
  <Teleport to="body">
    <div aria-live="assertive" class="pointer-events-none fixed inset-0 flex items-end px-4 py-6 sm:items-start sm:p-6 z-[9999]">
      <div class="flex w-full flex-col items-center space-y-4 sm:items-end">
        <TransitionGroup
          enter-active-class="transform ease-out duration-350 transition"
          enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2 scale-95"
          enter-to-class="translate-y-0 opacity-100 sm:translate-x-0 scale-100"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-for="toast in toasts"
            :key="toast.id"
            class="pointer-events-auto w-full max-w-sm overflow-hidden rounded-xl bg-white shadow-xl ring-1 ring-black/5 backdrop-blur-sm"
          >
            <div class="p-4">
              <div class="flex items-start gap-3">
                <!-- Icon with animation -->
                <div class="flex-shrink-0">
                  <div
                    :class="[
                      'p-2 rounded-lg',
                      toast.variant === 'success' && 'bg-success-50',
                      toast.variant === 'error' && 'bg-error-50',
                      toast.variant === 'warning' && 'bg-warning-50',
                      toast.variant === 'info' && 'bg-info-50',
                    ]"
                  >
                    <svg
                      v-if="toast.variant === 'success'"
                      class="h-5 w-5 text-success-600 animate-scale-in"
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
                      v-else-if="toast.variant === 'error'"
                      class="h-5 w-5 text-error-600 animate-scale-in"
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
                      v-else-if="toast.variant === 'warning'"
                      class="h-5 w-5 text-warning-600 animate-scale-in"
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
                      class="h-5 w-5 text-info-600 animate-scale-in"
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
                </div>

                <!-- Content -->
                <div class="flex-1 pt-0.5">
                  <p class="text-sm font-semibold text-gray-900">{{ toast.title }}</p>
                  <p v-if="toast.message" class="mt-1 text-sm text-gray-600">{{ toast.message }}</p>
                  
                  <!-- Progress bar -->
                  <div
                    v-if="toast.duration"
                    class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden"
                  >
                    <div
                      :class="[
                        'h-full rounded-full transition-all',
                        toast.variant === 'success' && 'bg-success-500',
                        toast.variant === 'error' && 'bg-error-500',
                        toast.variant === 'warning' && 'bg-warning-500',
                        toast.variant === 'info' && 'bg-info-500',
                      ]"
                      :style="{
                        width: '100%',
                        animation: `shrink ${toast.duration}ms linear`,
                      }"
                    />
                  </div>
                </div>

                <!-- Close button -->
                <button
                  @click="remove(toast.id)"
                  class="flex-shrink-0 inline-flex rounded-lg p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-300 transition-colors"
                >
                  <span class="sr-only">Close</span>
                  <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()
</script>

<style scoped>
@keyframes shrink {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}
</style>
