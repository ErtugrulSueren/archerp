<template>
  <div class="animate-pulse bg-slate-200 rounded-lg" :class="[width, height]"></div>
</template>

<script setup>
defineProps({
  width: {
    type: String,
    default: 'w-full'
  },
  height: {
    type: String,
    default: 'h-4'
  }
})
</script>
