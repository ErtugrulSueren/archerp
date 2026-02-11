<template>
  <div class="flex items-center">
    <button 
        type="button" 
        class="bg-slate-200 relative inline-flex h-7 w-12 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2" 
        :class="{ 
          'bg-blue-600': modelValue,
          'cursor-pointer': !disabled,
          'cursor-not-allowed opacity-50': disabled
        }"
        role="switch" 
        :aria-checked="modelValue"
        :disabled="disabled"
        @click="!disabled && $emit('update:modelValue', !modelValue)"
    >
      <span class="sr-only">{{ label }}</span>
      <span 
        aria-hidden="true" 
        class="translate-x-0 pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
        :class="{ 'translate-x-5': modelValue }"
      ></span>
    </button>
    <span 
      v-if="label" 
      class="ml-3 text-base font-medium" 
      :class="disabled ? 'text-slate-400 cursor-not-allowed' : 'text-slate-900 cursor-pointer'" 
      @click="!disabled && $emit('update:modelValue', !modelValue)"
    >{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  label: String,
  disabled: Boolean
})

defineEmits(['update:modelValue'])
</script>
