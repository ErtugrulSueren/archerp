<template>
  <div class="space-y-1.5">
    <label v-if="label" class="block text-sm font-medium text-slate-700">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <select
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base px-4 py-3 transition-all duration-200 disabled:bg-slate-50 disabled:text-slate-500 appearance-none bg-white"
        :class="[error ? 'border-red-300 text-red-900 focus:border-red-500 focus:ring-red-500' : '']"
        :disabled="disabled"
        v-bind="$attrs"
      >
        <option v-if="placeholder" value="" disabled selected>{{ placeholder }}</option>
        <option 
            v-for="option in options" 
            :key="option.value || option" 
            :value="option.value || option"
        >
          {{ option.label || option }}
        </option>
        <slot></slot>
      </select>
      <!-- Custom Arrow -->
      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-if="help && !error" class="mt-1 text-sm text-slate-500">{{ help }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  label: String,
  options: {
    type: Array,
    default: () => [] // Array of strings or objects { label: '...', value: '...' }
  },
  placeholder: String,
  required: Boolean,
  disabled: Boolean,
  error: String,
  help: String,
})

defineEmits(['update:modelValue'])
</script>
