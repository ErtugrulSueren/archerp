<template>
  <div class="space-y-1.5">
    <label v-if="label" class="block text-sm font-medium text-slate-700">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <input
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base px-4 py-3 transition-all duration-200 placeholder:text-slate-400 disabled:bg-slate-50 disabled:text-slate-500"
        :class="[
            iconLeft ? 'pl-10' : '', 
            error ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500' : ''
        ]"
        :placeholder="placeholder"
        :disabled="disabled"
        v-bind="$attrs"
      />
      <!-- Left Icon -->
      <div v-if="iconLeft" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
          <component :is="iconLeft" v-if="typeof iconLeft === 'object'" class="h-5 w-5" />
          <span v-else v-html="computedIcon" class="flex items-center [&>svg]:h-5 [&>svg]:w-5"></span>
      </div>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-if="help && !error" class="mt-1 text-sm text-slate-500">{{ help }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import feather from 'feather-icons'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  type: {
    type: String,
    default: 'text'
  },
  placeholder: String,
  required: Boolean,
  disabled: Boolean,
  error: String,
  help: String,
  iconLeft: [Object, String]
})

defineEmits(['update:modelValue'])

const computedIcon = computed(() => {
    if (typeof props.iconLeft === 'string') {
        const iconName = props.iconLeft.toLowerCase()
        
        // Defensive check for feather library
        if (feather && feather.icons && feather.icons[iconName]) {
            return feather.icons[iconName].toSvg({ class: 'h-5 w-5', 'stroke-width': 2 })
        }
        
        // If 'Barcode' is passed but no feather icon, we might need a fallback or custom mapping.
        // Feather lacks 'barcode'. Let's add a custom fallback/shim for common missing ones.
        if (iconName === 'barcode') {
            return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5v14"/><path d="M8 5v14"/><path d="M12 5v14"/><path d="M17 5v14"/><path d="M21 5v14"/></svg>`
        }
        if (iconName === 'currency') { 
             if(feather && feather.icons && feather.icons['dollar-sign']) {
                 return feather.icons['dollar-sign'].toSvg({ class: 'h-5 w-5', 'stroke-width': 2 })
             }
             return '<span class="text-slate-400 font-bold">$</span>'
        }
        return props.iconLeft
    }
    return ''
})
</script>
