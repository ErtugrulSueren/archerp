<template>
  <div class="relative group" ref="containerRef">
    <div class="relative">
      <!-- Input element -->
      <input
        type="text"
        :value="displayValue"
        placeholder=" "
        :disabled="disabled || loading"
        class="block px-4 pb-2.5 pt-5 w-full text-base text-gray-900 bg-gray-50/50 border border-gray-200 rounded-xl appearance-none focus:outline-none focus:ring-0 focus:border-indigo-600 peer transition-all duration-200"
        :class="[
            disabled ? 'bg-gray-100 cursor-not-allowed opacity-75' : 'hover:bg-gray-100/50',
            loading ? 'cursor-wait' : ''
        ]"
        @input="handleInput"
        @focus="openDropdown"
        @keydown.down.prevent="navigateOptions(1)"
        @keydown.up.prevent="navigateOptions(-1)"
        @keydown.enter.prevent="selectHighlighted"
        @blur="handleBlur"
      />

       <!-- Floating Label -->
       <label
        class="absolute text-gray-500 duration-200 transform top-4 z-10 origin-[0] left-4 pointer-events-none truncate max-w-[calc(100%-3rem)]"
        :class="[
            displayValue || isFocused ? '-translate-y-4 scale-75' : 'scale-100 translate-y-0',
            isFocused ? 'text-indigo-600' : ''
        ]"
      >
        {{ label }} <span v-if="required" class="text-red-500">*</span>
      </label>

       <!-- Spinner or Chevron -->
       <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
           <div v-if="loading" class="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
           <FeatherIcon v-else name="chevron-down" class="w-5 h-5 transition-transform duration-200" :class="{'rotate-180': isOpen}" />
       </div>

       <!-- Bottom Highlight -->
       <div 
        v-if="!disabled"
        class="absolute bottom-0 left-0 h-[2px] w-0 bg-indigo-600 transition-all duration-300 peer-focus:w-full"
       ></div>
    </div>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
        <div 
            v-if="isOpen && options.length > 0" 
            class="absolute z-50 w-full mt-1 bg-white border border-gray-100 rounded-xl shadow-xl max-h-60 overflow-auto focus:outline-none py-1 custom-scrollbar"
            @scroll="onDropdownScroll"
        >
            <div
                v-for="(option, idx) in options"
                :key="option.value"
                class="px-4 py-2 text-sm text-gray-700 cursor-pointer hover:bg-gray-50 transition-colors"
                :class="{'bg-indigo-50 text-indigo-700': idx === highlightedIndex}"
                @click="selectOption(option)"
                @mouseenter="highlightedIndex = idx"
            >
                {{ option.label }}
            </div>
            <div v-if="loading" class="py-2 flex justify-center text-indigo-500">
                 <FeatherIcon name="loader" class="w-4 h-4 animate-spin" />
            </div>
        </div>
        <div v-else-if="isOpen && !loading" class="absolute z-50 w-full mt-1 bg-white border border-gray-100 rounded-xl shadow-xl p-3 text-sm text-gray-500 text-center">
            Sonuç bulunamadı
        </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { call, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: [String, Number, Object],
  targetDoctype: { type: String, required: true },
  label: String,
  disabled: Boolean,
  required: Boolean,
  placeholder: String,
  filters: Object
})

const emit = defineEmits(['update:modelValue'])

const containerRef = ref(null)
const isFocused = ref(false)
const isOpen = ref(false)
const options = ref([])
const loading = ref(false)
const searchText = ref('')
const highlightedIndex = ref(-1)
const resolvedTitle = ref(null)

// Pagination State
const start = ref(0)
const hasMore = ref(true)
const pageLength = 20

const displayValue = computed(() => {
    if (isFocused.value && searchText.value) return searchText.value
    if (props.modelValue && typeof props.modelValue === 'object') return props.modelValue.label || props.modelValue.value
    
    // Use resolved title if available (for initial value display)
    if (resolvedTitle.value) return resolvedTitle.value
    
    return props.modelValue || ''
})

function handleInput(e) {
    searchText.value = e.target.value
    if (!isOpen.value) isOpen.value = true
    // Reset pagination
    start.value = 0
    hasMore.value = true
    fetchOptions(e.target.value, false)
}

function openDropdown() {
    isFocused.value = true
    isOpen.value = true
    if (options.value.length === 0) {
        start.value = 0
        hasMore.value = true
        fetchOptions('', false)
    }
}

function handleBlur() {
    // We rely on click outside to close for interaction logic
}

function selectOption(option) {
    emit('update:modelValue', option.value)
    resolvedTitle.value = option.label // Set immediate title
    searchText.value = ''
    isOpen.value = false
    isFocused.value = false
}

function selectHighlighted() {
    if (highlightedIndex.value >= 0 && options.value[highlightedIndex.value]) {
        selectOption(options.value[highlightedIndex.value])
    }
}

function navigateOptions(direction) {
    if (!isOpen.value) {
        isOpen.value = true
        return
    }
    const newIndex = highlightedIndex.value + direction
    if (newIndex >= 0 && newIndex < options.value.length) {
        highlightedIndex.value = newIndex
        const el = document.getElementById(`option-${newIndex}`)
        if (el) el.scrollIntoView({ block: 'nearest' })
    }
}

async function fetchOptions(query = '', append = false) {
    if (!props.targetDoctype) return
    if (loading.value) return
    loading.value = true
    
    try {
        const filters = { ...props.filters }
        if (query) {
            filters.name = ['like', `%${query}%`]
        }

        const data = await call('frappe.desk.search.search_link', {
            doctype: props.targetDoctype,
            txt: query,
            filters: props.filters,
            page_length: pageLength,
            limit_start: start.value
        })
        
        const newOptions = data.map(d => ({ 
            label: d.description ? `${d.value}: ${d.description}` : d.value,
            value: d.value,
            description: d.description 
        }))

        if (append) {
            options.value = [...options.value, ...newOptions]
        } else {
            options.value = newOptions
        }

        // Check if we reached end
        if (newOptions.length < pageLength) {
            hasMore.value = false
        } else {
            start.value += pageLength
            hasMore.value = true
        }
        
        highlightedIndex.value = -1
    } catch (e) {
        console.error('Link options error:', e)
    } finally {
        loading.value = false
    }
}

function onDropdownScroll(e) {
    const el = e.target
    if (el.scrollHeight - el.scrollTop <= el.clientHeight + 50) {
        // Near bottom
        if (hasMore.value && !loading.value) {
            fetchOptions(searchText.value, true)
        }
    }
}

// Resolve initial title
watch(() => props.modelValue, async (val) => {
    if (val && typeof val !== 'object' && !resolvedTitle.value) {
         try {
             // Try to resolve title via search_link strict match
             const res = await call('frappe.desk.search.search_link', {
                doctype: props.targetDoctype,
                txt: val,
                filters: props.filters
             })
             const match = res.find(r => r.value === val)
             if (match) {
                 resolvedTitle.value = match.description || match.value
             } else {
                 resolvedTitle.value = val 
             }
         } catch(e) {
             resolvedTitle.value = val
         }
    } else if (!val) {
        resolvedTitle.value = null
    }
}, { immediate: true })

// Native Click Outside
function handleClickOutside(event) {
    if (containerRef.value && !containerRef.value.contains(event.target)) {
        isOpen.value = false
        isFocused.value = false
        searchText.value = ''
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>
