<template>
  <div class="space-y-1.5">
    <label v-if="label" class="block text-sm font-medium text-slate-700">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <input
        type="date"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base px-4 py-3 transition-all duration-200 placeholder:text-slate-400 disabled:bg-slate-50 disabled:text-slate-500"
        :class="[error ? 'border-red-300 text-red-900 focus:border-red-500 focus:ring-red-500' : '']"
        :disabled="disabled"
        v-bind="$attrs"
      />
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: String,
  label: String,
  required: Boolean,
  disabled: Boolean,
  error: String,
})

defineEmits(['update:modelValue'])
</script>
