<template>
  <div class="flex items-center">
    <button
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :disabled="disabled"
      @click="toggle"
      :class="[
        modelValue ? 'bg-primary-600' : 'bg-gray-200',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
      ]"
    >
      <span class="sr-only">{{ label }}</span>
      <span
        aria-hidden="true"
        :class="[
          modelValue ? 'translate-x-5' : 'translate-x-0',
          'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
        ]"
      />
    </button>
    <span
      v-if="label"
      class="ml-3 text-sm font-medium text-gray-900 select-none cursor-pointer"
      :class="{ 'opacity-50 cursor-not-allowed': disabled }"
      @click="!disabled && toggle()"
    >
      {{ label }}
    </span>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  label: String,
  disabled: Boolean,
})

const emit = defineEmits(['update:modelValue'])

const toggle = () => {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>
