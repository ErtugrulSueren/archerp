<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol role="list" class="flex items-center space-x-2">
      <li v-for="(item, index) in items" :key="item.label">
        <div class="flex items-center">
          <svg
            v-if="index > 0"
            class="h-5 w-5 flex-shrink-0 text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
          </svg>
          <router-link
            v-if="item.to"
            :to="item.to"
            class="ml-2 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
            :class="{ 'ml-0': index === 0 }"
             active-class="text-gray-900 pointer-events-none"
          >
            {{ item.label }}
          </router-link>
          <span
            v-else
            class="ml-2 text-sm font-medium text-gray-900"
            :class="{ 'ml-0': index === 0 }"
            aria-current="page"
          >
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
    // Expected format: [{ label: 'Home', to: '/' }, { label: 'Project' }]
  },
})
</script>
