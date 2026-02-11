<template>
  <Popover v-model:show="isOpen">
    <template #target>
      <button 
        @click="isOpen = !isOpen"
        class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        :class="{ 'bg-gray-100 text-gray-900': isOpen || activeCount > 0 }"
      >
        <FeatherIcon name="sliders" class="w-4 h-4" />
        <span class="hidden sm:inline">Varsayılanlar</span>
        <Badge v-if="activeCount > 0" theme="blue" size="sm" class="ml-1">
          {{ activeCount }}
        </Badge>
      </button>
    </template>
    
    <template #body-main>
      <div class="p-4 w-80">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-gray-900">Oturum Varsayılanları</h3>
          <button 
            v-if="activeCount > 0"
            @click="clearAll"
            class="text-xs text-gray-400 hover:text-red-500 transition-colors"
            :disabled="saving"
          >
            Temizle
          </button>
        </div>
        
        <div v-if="isLoading" class="flex items-center justify-center py-8">
          <div class="w-6 h-6 border-2 border-gray-200 border-t-primary-600 rounded-full animate-spin"></div>
        </div>
        
        <div v-else-if="fields.length === 0" class="py-4 text-center">
          <p class="text-sm text-gray-500">Oturum varsayılanları tanımlanmamış.</p>
          <p class="text-xs text-gray-400 mt-2">
            Frappe Desk'ten "Oturum Varsayılan Ayarları" menüsünden yapılandırın.
          </p>
        </div>
        
        <div v-else class="space-y-4">
          <div v-for="field in fields" :key="field.fieldname" class="space-y-1.5">
            <label class="text-xs text-gray-500 font-medium">{{ field.label }}</label>
            <select 
              :value="defaults[field.fieldname]"
              @change="handleChange(field.fieldname, $event.target.value)"
              class="w-full text-sm border-gray-200 rounded-lg focus:ring-primary-500 focus:border-primary-500 py-2 px-3 bg-white"
              :disabled="saving"
            >
              <option value="">Seçiniz...</option>
              <option v-for="opt in fieldOptions[field.fieldname]" :key="opt" :value="opt">
                {{ opt }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-100">
          <p class="text-xs text-gray-400">
            Seçilen varsayılanlar tüm listelerde ve raporlarda otomatik filtre olarak uygulanır.
          </p>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { FeatherIcon, Badge, Popover, call } from 'frappe-ui'
import { useSessionDefaults } from '@/composables/useSessionDefaults'

const { 
  defaults, 
  fields,
  isLoading, 
  loadDefaults, 
  setDefault,
  clearAllDefaults,
  getActiveDefaultsCount 
} = useSessionDefaults()

const isOpen = ref(false)
const saving = ref(false)
const fieldOptions = reactive({})

const activeCount = computed(() => getActiveDefaultsCount())

async function handleChange(fieldname, value) {
  saving.value = true
  try {
    await setDefault(fieldname, value)
  } catch (e) {
    console.error('Failed to save default:', e)
  } finally {
    saving.value = false
  }
}

async function clearAll() {
  saving.value = true
  try {
    await clearAllDefaults()
  } catch (e) {
    console.error('Failed to clear defaults:', e)
  } finally {
    saving.value = false
  }
}

// Load options for each field
async function loadFieldOptions() {
  for (const field of fields.value) {
    if (field.options) {
      try {
        const result = await call('frappe.client.get_list', {
          doctype: field.options,
          fields: ['name'],
          limit_page_length: 0
        })
        fieldOptions[field.fieldname] = result?.map(r => r.name) || []
      } catch (e) {
        console.warn(`Failed to load options for ${field.fieldname}:`, e)
        fieldOptions[field.fieldname] = []
      }
    }
  }
}

// Watch fields and load options when they change
watch(fields, () => {
  if (fields.value.length > 0) {
    loadFieldOptions()
  }
}, { immediate: true })

onMounted(() => {
  loadDefaults()
})
</script>
