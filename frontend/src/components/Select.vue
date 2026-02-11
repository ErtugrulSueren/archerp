<template>
  <div>
    <div class="relative group">
      <select
        :id="id"
        :value="modelValue"
        :disabled="disabled"
        class="block px-4 pb-2.5 pt-5 w-full text-base text-gray-900 bg-gray-50/50 border border-gray-200 rounded-xl appearance-none focus:outline-none focus:ring-0 focus:border-indigo-600 peer transition-all duration-200"
        :class="[
            disabled ? 'bg-gray-100 cursor-not-allowed opacity-75' : 'hover:bg-gray-100/50',
            error ? 'border-red-300 focus:border-red-500 bg-red-50/10' : ''
        ]"
        @change="$emit('update:modelValue', $event.target.value)"
        v-bind="$attrs"
      >
        <option v-if="placeholder" value="" disabled selected class="text-gray-400">{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="option.value || option"
          :value="option.value || option"
        >
          {{ option.label || option }}
        </option>
      </select>

      <!-- Floating Label -->
      <label
        :for="id"
        class="absolute text-gray-500 duration-200 transform -translate-y-4 scale-75 top-4 z-10 origin-[0] left-4 peer-focus:text-indigo-600 peer-focus:scale-75 peer-focus:-translate-y-4 pointer-events-none truncate max-w-[calc(100%-3rem)]"
         :class="[
            modelValue ? '-translate-y-4 scale-75' : 'scale-100 translate-y-0',
            error ? 'text-red-500 peer-focus:text-red-600' : ''
        ]"
      >
        {{ label }} <span v-if="required" class="text-red-500">*</span>
      </label>

      <!-- Chevron Icon -->
      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500 group-hover:text-gray-700 transition-colors">
        <FeatherIcon name="chevron-down" class="w-5 h-5" />
      </div>

       <!-- Bottom Highlight (Animated) -->
       <div 
        v-if="!disabled && !error"
        class="absolute bottom-0 left-0 h-[2px] w-0 bg-indigo-600 transition-all duration-300 peer-focus:w-full"
       ></div>
    </div>

    <!-- Error message -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
        <p v-if="error" class="mt-1 ml-1 text-xs font-medium text-red-600 flex items-center gap-1">
            <FeatherIcon name="alert-circle" class="w-3.5 h-3.5" />
            {{ error }}
        </p>
    </Transition>
    
    <!-- Helper Text -->
    <p v-if="help && !error" class="mt-1 ml-1 text-xs text-gray-500">{{ help }}</p>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  modelValue: [String, Number],
  options: {
    type: Array,
    default: () => [],
  },
  label: String,
  placeholder: String,
  help: String,
  error: String,
  required: Boolean,
  disabled: Boolean,
  id: {
    type: String,
    default: () => `select-${Math.random().toString(36).substring(2, 9)}`,
  },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
select {
  /* Ensure default arrow is hidden across browsers */
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: none;
}
select::-ms-expand {
  display: none;
}
</style>
