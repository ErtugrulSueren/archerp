<template>
  <div 
    class="flex items-center justify-center rounded-full overflow-hidden shrink-0 select-none"
    :class="[sizeClasses, !image ? colorClass : 'bg-slate-100']"
  >
    <img 
      v-if="image" 
      :src="image" 
      :alt="label" 
      class="w-full h-full object-cover"
    />
    <span v-else class="font-bold text-slate-700" :class="textSize">
      {{ initials }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  image: String,
  label: {
    type: String,
    default: ''
  },
  size: {
    type: String, // sm, md, lg, xl
    default: 'md'
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-8 h-8'
    case 'lg': return 'w-12 h-12'
    case 'xl': return 'w-16 h-16'
    default: return 'w-10 h-10' // md
  }
})

const textSize = computed(() => {
    switch (props.size) {
    case 'sm': return 'text-xs'
    case 'lg': return 'text-base'
    case 'xl': return 'text-lg'
    default: return 'text-sm' // md
  }
})

const initials = computed(() => {
  if (!props.label) return '?'
  return props.label
    .split(' ')
    .map(w => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const colorClass = computed(() => {
  const colors = [
    'bg-red-100 text-red-700',
    'bg-orange-100 text-orange-700',
    'bg-amber-100 text-amber-700',
    'bg-yellow-100 text-yellow-700',
    'bg-lime-100 text-lime-700',
    'bg-green-100 text-green-700',
    'bg-emerald-100 text-emerald-700',
    'bg-teal-100 text-teal-700',
    'bg-cyan-100 text-cyan-700',
    'bg-sky-100 text-sky-700',
    'bg-blue-100 text-blue-700',
    'bg-indigo-100 text-indigo-700',
    'bg-violet-100 text-violet-700',
    'bg-purple-100 text-purple-700',
    'bg-fuchsia-100 text-fuchsia-700',
    'bg-pink-100 text-pink-700',
    'bg-rose-100 text-rose-700',
  ]
  
  if (!props.label) return 'bg-slate-100 text-slate-600'
  
  // Simple hash to pick consistent color
  let hash = 0
  for (let i = 0; i < props.label.length; i++) {
    hash = props.label.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  return colors[Math.abs(hash) % colors.length]
})
</script>
