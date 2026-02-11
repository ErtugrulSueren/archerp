<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol role="list" class="flex items-center space-x-2">
      <li v-for="(item, index) in items" :key="index">
        <div class="flex items-center">
          <svg v-if="index > 0" class="flex-shrink-0 h-5 w-5 text-slate-300" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
          </svg>
          <router-link 
            v-if="item.to" 
            :to="item.to"
            class="ml-2 text-base font-medium text-slate-500 hover:text-slate-700 transition-colors"
            :class="{ 'ml-0': index === 0 }"
          >
            {{ item.label }}
          </router-link>
          <span v-else class="ml-2 text-base font-medium text-slate-800" :class="{ 'ml-0': index === 0 }">
             {{ item.label }}
          </span>
        </div>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
    // [{ label: 'Home', to: '/' }, { label: 'Products' }]
  }
})
</script>
