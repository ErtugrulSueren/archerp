<template>
  <div
    class="animate-pulse bg-gray-200"
    :class="[rounded ? 'rounded-full' : 'rounded-md', className]"
    :style="{ width: width, height: height }"
  ></div>
</template>

<script setup>
defineProps({
  width: {
    type: String,
    default: '100%',
  },
  height: {
    type: String,
    default: '1rem',
  },
  rounded: {
    type: Boolean,
    default: false,
  },
  className: {
    type: String,
    default: '',
  },
})
</script>
