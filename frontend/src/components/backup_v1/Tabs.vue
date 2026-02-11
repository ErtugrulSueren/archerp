<template>
  <div>
    <div class="border-b border-slate-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          @click="$emit('update:modelValue', tab.name)"
          :class="[
            modelValue === tab.name
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-base transition-colors'
          ]"
          :aria-current="modelValue === tab.name ? 'page' : undefined"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>
    <div class="py-4">
        <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  tabs: {
    type: Array,
    required: true,
    // [{ label: 'General', name: 'general' }]
  },
  modelValue: String
})

defineEmits(['update:modelValue'])
</script>
