<template>
  <div class="border border-slate-200 rounded-xl bg-white">
    <table class="min-w-full divide-y divide-slate-200">
      <thead class="bg-slate-50">
        <tr>
          <th 
            v-for="col in columns" 
            :key="col.key"
            class="px-4 py-3 text-left text-xs font-bold text-slate-600 uppercase tracking-wider"
          >
            {{ col.label }}
          </th>
          <th v-if="!disabled" class="px-4 py-3 w-20"></th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-slate-100">
        <tr v-for="(row, idx) in localData" :key="idx" class="hover:bg-slate-50" @dblclick="editRow(idx)">
          <td v-for="col in columns" :key="col.key" class="px-4 py-3">
            <input
              v-if="col.type === 'text'"
              type="text"
              v-model="row[col.key]"
              :disabled="disabled"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:bg-slate-50"
              :placeholder="col.placeholder"
            />
            <Combobox
              v-else-if="col.type === 'select'"
              :options="col.options || []"
              v-model="row[col.key]"
              :disabled="disabled"
            />
            <span v-else-if="col.type === 'currency' || col.fieldtype === 'Currency'" class="text-sm text-slate-700 font-mono block text-right">
                {{ formatCurrency(row[col.key]) }}
            </span>
            <span v-else class="text-sm text-slate-700">{{ row[col.key] }}</span>
          </td>
          <td v-if="!disabled" class="px-4 py-3 text-right whitespace-nowrap">
             <div class="flex items-center justify-end gap-1">
                <button 
                  @click.stop="editRow(idx)"
                  class="text-blue-500 hover:text-blue-700 p-1 rounded hover:bg-blue-50 transition-colors"
                  title="Detaylı Düzenle"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                </button>
                <button 
                  @click.stop="removeRow(idx)"
                  class="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors"
                  title="Sil"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
             </div>
          </td>
        </tr>
        <tr v-if="localData.length === 0">
          <td :colspan="columns.length + (disabled ? 0 : 1)" class="px-4 py-8 text-center text-slate-400 text-sm">
            {{ emptyMessage || 'Henüz kayıt yok.' }}
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!disabled" class="bg-slate-50 px-4 py-3 border-t border-slate-200">
      <Button variant="outline" size="sm" icon-left="Plus" @click="addRow">
        {{ addButtonLabel || 'Satır Ekle' }}
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Button from './Button.vue'
import Combobox from './Combobox.vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  disabled: Boolean,
  emptyMessage: String,
  addButtonLabel: String
})

const emit = defineEmits(['update:modelValue', 'edit-row'])

const localData = ref([...props.modelValue])

watch(() => props.modelValue, (newVal) => {
  localData.value = [...newVal]
}, { deep: true })

watch(localData, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

function addRow() {
  const newRow = {}
  props.columns.forEach(col => {
    newRow[col.key] = ''
  })
  localData.value.push(newRow)
  // Auto-open modal for new row
  emit('edit-row', localData.value.length - 1)
}

function removeRow(index) {
  localData.value.splice(index, 1)
}

function editRow(index) {
  emit('edit-row', index)
}

function formatCurrency(val) {
    if (!val) return '0.00'
    return parseFloat(val).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
