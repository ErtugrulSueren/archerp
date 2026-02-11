<template>
  <div class="relative space-y-1.5" ref="container">
    <label v-if="label" class="block text-sm font-medium text-slate-700">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
        <input
            type="text"
            v-model="searchQuery"
            @focus="isOpen = !disabled && true"
            @input="isOpen = !disabled && true"
            class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base px-4 py-3 transition-all duration-200 placeholder:text-slate-400 disabled:bg-slate-50"
            :placeholder="placeholder || 'Ara...'"
            :disabled="disabled"
            v-bind="$attrs"
            autocomplete="off"
        />
        
        <div v-if="modelValue" class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button @click="clearSelection" class="text-slate-400 hover:text-slate-600 p-1">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
        </div>
    </div>

    <!-- Dropdown -->
    <div v-if="isOpen && filteredOptions.length > 0" class="absolute z-10 mt-1 w-full bg-white rounded-xl shadow-lg border border-slate-100 max-h-60 overflow-auto py-1">
        <div 
            v-for="option in filteredOptions" 
            :key="option.value"
            @click="selectOption(option)"
            class="px-4 py-2 hover:bg-slate-50 cursor-pointer text-base text-slate-700 flex items-center justify-between group"
            :class="{'bg-blue-50 text-blue-700': modelValue === option.value}"
        >
            <span>{{ option.label }}</span>
            <svg v-if="modelValue === option.value" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-600"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
    </div>
    
    <div v-if="isOpen && filteredOptions.length === 0" class="absolute z-10 mt-1 w-full bg-white rounded-xl shadow-lg border border-slate-100 p-4 text-center text-slate-500 text-sm">
        Sonuç bulunamadı.
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  options: {
    type: Array,
    required: true, 
    // [{ label: 'Label', value: 'value' }]
  },
  label: String,
  placeholder: String,
  required: Boolean,
  disabled: Boolean
})

const emit = defineEmits(['update:modelValue'])

const searchQuery = ref('')
const isOpen = ref(false)
const container = ref(null)

const filteredOptions = computed(() => {
    if (!searchQuery.value) return props.options
    const query = searchQuery.value.toLowerCase()
    return props.options.filter(opt => opt.label.toLowerCase().includes(query))
})

// Initialize search query if value exists
watch(() => props.modelValue, (val) => {
    const selected = props.options.find(o => o.value === val)
    if (selected) {
        searchQuery.value = selected.label
    } else if (!val) {
        searchQuery.value = ''
    } else {
        // If value exists but options not loaded yet, show the value itself
        searchQuery.value = val
    }
}, { immediate: true })

// Update searchQuery when options change (e.g., when they're loaded from backend)
watch(() => props.options, () => {
    if (props.modelValue) {
        const selected = props.options.find(o => o.value === props.modelValue)
        if (selected) {
            searchQuery.value = selected.label
        }
    }
}, { deep: true })

function selectOption(option) {
    emit('update:modelValue', option.value)
    searchQuery.value = option.label
    isOpen.value = false
}

function clearSelection() {
    emit('update:modelValue', '')
    searchQuery.value = ''
    isOpen.value = false // Optional: keep open or close
}

// Click outside to close
function handleClickOutside(event) {
    if (container.value && !container.value.contains(event.target)) {
        isOpen.value = false
        // Reset query if no valid selection? (Optional UX choice)
        // For now, let's keep it simple: if typed but not selected, maybe revert? 
        // We'll leave it as is for flexible search feeling.
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>
