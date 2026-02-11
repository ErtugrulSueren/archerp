<template>
  <div class="bg-white shadow-lg shadow-slate-200/50 ring-1 ring-slate-900/5 rounded-xl overflow-hidden">
    <table class="min-w-full divide-y divide-gray-100">
      <thead class="bg-slate-50/50">
        <tr>
          <th 
            v-for="col in columns" 
            :key="col.key"
            class="px-6 py-5 text-left text-base font-bold text-slate-600 uppercase tracking-wide"
            :class="[
              col.align === 'right' ? 'text-right' : 'text-left',
              col.width ? col.width : ''
            ]"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-50 bg-white">
        <tr 
          v-for="(row, rowIndex) in data" 
          :key="rowKeys ? row[rowKeys] : rowIndex" 
          class="group hover:bg-slate-50/80 transition-all duration-200 cursor-pointer"
          @click="$emit('row-click', row)"
        >
          <td 
            v-for="col in columns" 
            :key="col.key"
            class="px-6 py-5 whitespace-nowrap"
            :class="[col.align === 'right' ? 'text-right' : 'text-left']"
          >
            <!-- Slot for Custom Cell Content -->
            <slot :name="'cell-' + col.key" :row="row" :value="getValue(row, col.key)">
               <!-- Default Rendering -->
               <span class="text-base text-slate-700 font-medium group-hover:text-slate-900 transition-colors">
                 {{ getValue(row, col.key) }}
               </span>
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- Empty State -->
    <div v-if="!data || data.length === 0" class="p-12 text-center text-slate-400">
        <div class="flex flex-col items-center gap-3">
             <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="opacity-50"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
             <span class="text-lg font-medium">Kayıt bulunamadı.</span>
        </div>
    </div>

    <!-- Pagination / Footer -->
    <div v-if="showPagination" class="bg-blue-50/50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-slate-600 font-medium">
            <slot name="footer-left">
                Toplam Kayıt: <strong>{{ data.length }}</strong>
            </slot>
        </div>
        
        <div class="flex gap-2">
            <slot name="footer-right">
                <button class="px-3 py-1 border border-slate-300 rounded-lg text-sm bg-white hover:bg-slate-50 disabled:opacity-50" disabled>Önceki</button>
                <button class="px-3 py-1 border border-slate-300 rounded-lg text-sm bg-white hover:bg-slate-50">Sonraki</button>
            </slot>
        </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    default: () => []
  },
  rowKeys: {
    type: String,
    default: 'name'
  },
  showPagination: {
      type: Boolean,
      default: true
  }
})

function getValue(row, key) {
    return row[key]
}

defineEmits(['row-click'])
</script>
