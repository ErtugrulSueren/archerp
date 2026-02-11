<template>
  <Dialog v-model="show" :options="{ size: 'md' }">
    <template #body-content>
      <div class="p-6">
        <div class="flex items-start gap-4">
          <!-- Icon -->
          <div 
            class="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center"
            :class="type === 'danger' ? 'bg-red-50 text-red-600' : 'bg-yellow-50 text-yellow-600'"
          >
            <svg v-if="type === 'danger'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v2m0 4h.01"/><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          
          <!-- Content -->
          <div class="pt-1">
            <h3 class="text-lg font-bold text-slate-900 mb-2">{{ title }}</h3>
            <p class="text-slate-500 text-sm leading-relaxed">{{ message }}</p>
          </div>
        </div>
      </div>
    </template>
    
    <template #actions>
      <div class="px-6 pb-6 pt-2 flex justify-end gap-3 bg-white rounded-b-xl">
        <Button variant="outline" @click="cancel">
          {{ cancelLabel }}
        </Button>
        <Button 
          :variant="type === 'danger' ? 'solid' : 'solid'"
          :theme="type === 'danger' ? 'red' : 'blue'"
          @click="confirm"
          :loading="loading"
        >
          {{ confirmLabel }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Dialog } from 'frappe-ui'
import Button from '@/components/Button.vue'

const props = defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    default: 'Emin misiniz?'
  },
  message: {
    type: String,
    default: 'Bu işlem geri alınamaz.'
  },
  type: {
    type: String, // 'danger' | 'warning'
    default: 'danger'
  },
  confirmLabel: {
    type: String,
    default: 'Onayla'
  },
  cancelLabel: {
    type: String,
    default: 'İptal'
  },
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

function confirm() {
  emit('confirm')
}

function cancel() {
  show.value = false
  emit('cancel')
}
</script>
