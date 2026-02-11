<template>
  <div class="bg-white p-1 rounded-xl shadow-sm border border-gray-200 focus-within:border-indigo-300 focus-within:ring-4 focus-within:ring-indigo-50/50 transition-all duration-300">
      <textarea 
        v-model="content"
        rows="2"
        class="block w-full border-0 bg-transparent p-3 text-sm text-gray-900 placeholder:text-gray-400 focus:ring-0 resize-none min-h-[50px]"
        placeholder="Bir yorum yaz..."
      ></textarea>
      
      <div class="flex items-center justify-between px-2 pb-2 mt-1">
          <div></div> <!-- Spacer to keep button on right -->
          <AppButton 
            v-if="content.trim()"
            variant="solid" 
            size="sm" 
            class="rounded-lg !py-1.5 !px-4"
            icon-right="send"
            :loading="loading"
            @click="submit"
          >
              Gönder
          </AppButton>
      </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import AppButton from './AppButton.vue'

const emit = defineEmits(['submit'])
const content = ref('')
const loading = ref(false)

async function submit() {
    if (!content.value.trim()) return
    loading.value = true
    try {
        await emit('submit', content.value)
        content.value = ''
    } finally {
        loading.value = false
    }
}
</script>
