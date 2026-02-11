<template>
  <div>
    <div class="flex items-start">
        <div class="flex items-center h-5">
            <input
            :id="id"
            type="checkbox"
            :checked="modelValue"
            :disabled="disabled"
            class="h-5 w-5 rounded-md border-gray-300 text-indigo-600 focus:ring-indigo-500/30 focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 ease-in-out cursor-pointer"
            :class="{ 'cursor-not-allowed': disabled, 'border-red-300': error }"
            @change="$emit('update:modelValue', $event.target.checked)"
            />
        </div>
        <div class="ml-3 text-sm">
            <label
            v-if="label"
            :for="id"
            class="font-medium text-gray-700 select-none cursor-pointer transition-colors duration-200"
            :class="{ 'opacity-50 cursor-not-allowed': disabled, 'text-red-700': error }"
            >
            {{ label }} <span v-if="required" class="text-red-500">*</span>
            </label>
        </div>
    </div>
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
        <p v-if="error" class="ml-8 mt-1 text-xs font-medium text-red-600 flex items-center gap-1">
            {{ error }}
        </p>
    </Transition>
    <p v-if="help && !error" class="ml-8 mt-1 text-xs text-gray-500">{{ help }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  label: String,
  help: String,
  error: String,
  required: Boolean,
  disabled: Boolean,
  id: {
    type: String,
    default: () => `checkbox-${Math.random().toString(36).substring(2, 9)}`,
  },
})

defineEmits(['update:modelValue'])
</script>
