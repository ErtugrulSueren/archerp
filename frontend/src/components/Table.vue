<template>
  <div class="overflow-hidden shadow-sm ring-1 ring-gray-900/5 rounded-xl bg-white">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <!-- Header -->
        <thead class="bg-gradient-to-b from-gray-50 to-gray-100/50">
          <tr>
            <!-- Selection column -->
            <th v-if="selectable" scope="col" class="w-12 px-4 py-3.5">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected"
                @change="toggleAll"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 transition"
              />
            </th>

            <!-- Data columns -->
            <th
              v-for="col in columns"
              :key="col.key"
              scope="col"
              :class="[
                'px-6 py-3.5 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider',
                'first:pl-6 last:pr-6',
                col.sortable && 'cursor-pointer select-none hover:bg-gray-100/50 transition-colors',
                col.headerClass,
              ]"
              @click="col.sortable && handleSort(col.key)"
            >
              <div class="flex items-center gap-2">
                <span>{{ col.label }}</span>
                
                <!-- Sort indicator -->
                <span
                  v-if="col.sortable"
                  :class="[
                    'transition-all duration-200',
                    sortKey === col.key ? 'text-primary-600' : 'text-gray-400',
                  ]"
                >
                  <svg
                    v-if="sortKey === col.key && sortOrder === 'asc'"
                    class="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" />
                  </svg>
                  <svg
                    v-else-if="sortKey === col.key && sortOrder === 'desc'"
                    class="w-4 h-4 rotate-180"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" />
                  </svg>
                  <svg v-else class="w-4 h-4 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 3a.75.75 0 01.55.24l3.25 3.5a.75.75 0 11-1.1 1.02L10 4.852 7.3 7.76a.75.75 0 01-1.1-1.02l3.25-3.5A.75.75 0 0110 3zm-3.76 9.2a.75.75 0 011.06.04l2.7 2.908 2.7-2.908a.75.75 0 111.1 1.02l-3.25 3.5a.75.75 0 01-1.1 0l-3.25-3.5a.75.75 0 01.04-1.06z" />
                  </svg>
                </span>
              </div>
            </th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="divide-y divide-gray-100 bg-white">
          <tr
            v-for="(row, rowIndex) in computedData"
            :key="rowIndex"
            :class="[
              'transition-all duration-150',
              hoverable && 'hover:bg-gradient-to-r hover:from-gray-50 hover:to-transparent cursor-pointer',
              selectedRows.includes(rowIndex) && 'bg-primary-50/30',
              striped && rowIndex % 2 === 1 && 'bg-gray-50/30',
            ]"
            @click="handleRowClick(row, rowIndex)"
          >
            <!-- Selection column -->
            <td v-if="selectable" class="w-12 px-4 py-4">
              <input
                type="checkbox"
                :checked="selectedRows.includes(rowIndex)"
                @change="toggleRow(rowIndex)"
                @click.stop
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 transition"
              />
            </td>

            <!-- Data columns -->
            <td
              v-for="col in columns"
              :key="col.key"
              :class="[
                'px-6 py-4 text-sm text-gray-700',
                'first:pl-6 last:pr-6',
                col.cellClass,
                col.truncate && 'truncate max-w-xs',
              ]"
            >
              <!-- Custom cell slot -->
              <slot :name="`cell(${col.key})`" :value="row[col.key]" :row="row" :index="rowIndex">
                {{ row[col.key] }}
              </slot>
            </td>
          </tr>

          <!-- Empty state -->
          <tr v-if="computedData.length === 0">
            <td :colspan="columns.length + (selectable ? 1 : 0)" class="py-16 text-center">
              <div class="flex flex-col items-center gap-3">
                <svg
                  class="w-12 h-12 text-gray-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                  />
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ emptyTitle || 'Veri bulunamadı' }}</p>
                  <p v-if="emptyMessage" class="text-sm text-gray-500 mt-1">{{ emptyMessage }}</p>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center">
      <div class="flex flex-col items-center gap-3">
        <svg class="spinner w-8 h-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <p class="text-sm text-gray-600">Yükleniyor...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    default: () => [],
  },
  selectable: Boolean,
  hoverable: {
    type: Boolean,
    default: true,
  },
  striped: Boolean,
  loading: Boolean,
  emptyTitle: String,
  emptyMessage: String,
})

const emit = defineEmits(['row-click', 'selection-change'])

const sortKey = ref(null)
const sortOrder = ref('asc')
const selectedRows = ref([])

const computedData = computed(() => {
  if (!sortKey.value) return props.data

  const sorted = [...props.data].sort((a, b) => {
    const aVal = a[sortKey.value]
    const bVal = b[sortKey.value]
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal
    }
    
    const aStr = String(aVal || '').toLowerCase()
    const bStr = String(bVal || '').toLowerCase()
    
    if (sortOrder.value === 'asc') {
      return aStr.localeCompare(bStr)
    } else {
      return bStr.localeCompare(aStr)
    }
  })

  return sorted
})

const allSelected = computed(() => {
  return props.data.length > 0 && selectedRows.value.length === props.data.length
})

const someSelected = computed(() => {
  return selectedRows.value.length > 0 && selectedRows.value.length < props.data.length
})

const handleSort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const handleRowClick = (row, index) => {
  emit('row-click', { row, index })
}

const toggleRow = (index) => {
  const idx = selectedRows.value.indexOf(index)
  if (idx > -1) {
    selectedRows.value.splice(idx, 1)
  } else {
    selectedRows.value.push(index)
  }
  emit('selection-change', selectedRows.value.map(i => props.data[i]))
}

const toggleAll = () => {
  if (allSelected.value) {
    selectedRows.value = []
  } else {
    selectedRows.value = props.data.map((_, i) => i)
  }
  emit('selection-change', selectedRows.value.map(i => props.data[i]))
}
</script>
