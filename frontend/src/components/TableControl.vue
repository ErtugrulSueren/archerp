<template>
  <div class="border rounded-lg border-gray-200 overflow-hidden">
    <!-- Table Header -->
    <div class="bg-gray-50 border-b border-gray-200 px-4 py-2 flex justify-between items-center">
        <div>
            <h4 class="text-sm font-medium text-gray-700">
                {{ label }} <span v-if="required" class="text-red-500">*</span>
            </h4>
            <p v-if="description" class="text-xs text-gray-500 mt-0.5">{{ description }}</p>
        </div>
        <AppButton 
            v-if="!disabled"
            size="sm" 
            variant="outline" 
            icon-left="plus"
            @click="openAddModal"
        >
            Ekle
        </AppButton>
    </div>

    <!-- Table Body -->
    <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
            <thead class="bg-white border-b border-gray-100">
                <tr>
                    <th class="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider w-10">No</th>
                    <th 
                        v-for="field in visibleFields" 
                        :key="field.fieldname"
                        class="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider min-w-[150px]"
                        :class="{'text-right': field.fieldtype === 'Int' || field.fieldtype === 'Float' || field.fieldtype === 'Currency'}"
                    >
                        {{ field.label }}
                        <span v-if="field.reqd" class="text-red-500">*</span>
                    </th>
                    <th class="px-3 py-2 w-10" v-if="!disabled"></th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                <tr 
                    v-for="(row, idx) in rows" 
                    :key="row.idx || idx" 
                    class="hover:bg-gray-50 cursor-pointer"
                    @click="openEditModal(row, idx)"
                >
                    <td class="px-3 py-2 text-gray-400 text-xs text-center">{{ idx + 1 }}</td>
                    <td 
                        v-for="field in visibleFields" 
                        :key="field.fieldname"
                        class="px-3 py-2 text-gray-700"
                        :class="{'text-right': field.fieldtype === 'Int' || field.fieldtype === 'Float' || field.fieldtype === 'Currency'}"
                    >
                        {{ row[field.fieldname] }}
                    </td>
                    <td class="px-3 py-2 text-right" v-if="!disabled">
                        <button 
                            @click.stop="removeRow(idx)"
                            class="text-gray-400 hover:text-red-500 transition-colors p-1"
                        >
                             <FeatherIcon name="trash-2" class="w-4 h-4" />
                        </button>
                    </td>
                </tr>
                <!-- Empty State -->
                <tr v-if="rows.length === 0">
                    <td :colspan="visibleFields.length + 2" class="px-4 py-8 text-center text-gray-500 bg-gray-50/50">
                        <p>Henüz kayıt eklenmedi</p>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <!-- Dialog for Editing Row -->
    <Dialog
      :options="{
        title: editingRowIndex === -1 ? `Yeni ${label || 'Kayıt'}` : `${label || 'Kayıt'} Düzenle`,
        size: 'xl'
      }"
      v-model="isModalOpen"
    >
      <template #body-content>
        <div class="space-y-4" v-if="editingRow">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <template v-for="field in modalFields" :key="field.fieldname">
                    <div v-if="isFieldVisible(field, editingRow)">
                        <FormControl 
                            :field="field"
                            v-model="editingRow[field.fieldname]"
                            :doc="editingRow"
                            @update:modelValue="(val) => handleFieldChange(field, val)"
                        />
                    </div>
                </template>
            </div>
        </div>
      </template>
      <template #actions>
        <AppButton variant="solid" @click="saveRow">
          Tamam
        </AppButton>
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { call, FeatherIcon, Dialog } from 'frappe-ui'
import FormControl from './FormControl.vue'
import AppButton from './AppButton.vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  doctype: { type: String, required: true },
  label: String,
  disabled: Boolean,
  description: String,
  required: Boolean
})

const emit = defineEmits(['update:modelValue'])

const meta = ref(null)
const rows = ref([])
const isModalOpen = ref(false)
const editingRow = ref(null)
const editingRowIndex = ref(-1)

// Sync props.modelValue to local rows
watch(() => props.modelValue, (val) => {
    if (val && JSON.stringify(val) !== JSON.stringify(rows.value)) {
        rows.value = [...val]
    }
}, { immediate: true, deep: true })

// Sync rows change back to modelValue
watch(rows, (val) => {
    emit('update:modelValue', val)
}, { deep: true })


const fetchFromDeps = computed(() => {
    if (!meta.value || !meta.value.fields) return {}
    const deps = {}
    meta.value.fields.forEach(f => {
        if (f.fetch_from && f.fetch_from.includes('.')) {
            const [linkField, sourceField] = f.fetch_from.split('.')
            if (!deps[linkField]) deps[linkField] = []
            deps[linkField].push({ 
                targetField: f.fieldname, 
                sourceField: sourceField 
            })
        }
    })
    return deps
})

async function handleFieldChange(field, val) {
    // 1. Trigger Fetch From
    if (fetchFromDeps.value[field.fieldname]) {
        if (!val) {
            // Clear items if value is empty
            const targets = fetchFromDeps.value[field.fieldname]
            targets.forEach(t => {
                editingRow.value[t.targetField] = null
            })
            return
        }

        const targets = fetchFromDeps.value[field.fieldname]
        const sourceFields = targets.map(t => t.sourceField)
        
        try {
            // Get values from server
            const res = await call('frappe.client.get_value', {
                doctype: field.options,
                filters: { name: val },
                fieldname: sourceFields
            })

            if (res) {
                 for (const t of targets) {
                     if (res[t.sourceField] !== undefined) {
                         const newValue = res[t.sourceField]
                         const oldValue = editingRow.value[t.targetField]
                         
                         // Update
                         editingRow.value[t.targetField] = newValue

                         // RECURSIVE CHAIN:
                         // If the updated field (targetField) is ALSO a trigger for other fields
                         // We must manually trigger the change handler for it.
                         // We need the 'field' object for it.
                         if (newValue !== oldValue && fetchFromDeps.value[t.targetField]) {
                              const targetFieldMeta = meta.value.fields.find(f => f.fieldname === t.targetField)
                              if (targetFieldMeta) {
                                  // Await to ensure order
                                  await handleFieldChange(targetFieldMeta, newValue)
                              }
                         }
                     }
                 }
            }
        } catch (e) {
            console.error('Fetch From Error:', e)
        }
    }
}

const visibleFields = computed(() => {
    if (!meta.value || !meta.value.fields) return []
    // List view fields for table columns
    return meta.value.fields.filter(f => f.in_list_view && !f.hidden)
})

const modalFields = computed(() => {
    if (!meta.value || !meta.value.fields) return []
    // All fields for modal form (except hidden ones)
    return meta.value.fields.filter(f => !f.hidden)
})

async function fetchMeta() {
    if (!props.doctype) return
    try {
         const res = await call('frappe.desk.form.load.getdoctype', { doctype: props.doctype })
         if (res.docs && res.docs.length > 0) {
             meta.value = res.docs[0]
         }
    } catch (e) {
        console.error('Child Table Meta Error:', e)
    }
}

function processDefaults(fields) {
    const defaults = {}
    if (!fields) return defaults

    fields.forEach(f => {
        if (f.default) {
            let val = f.default
            if (val === 'Today') {
                val = new Date().toISOString().split('T')[0]
            } else if (val === 'Now') {
                const d = new Date()
                d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
                val = d.toISOString().slice(0, 16)
            } else if (val === '__user') {
                val = window.frappe?.session?.user || 'Administrator' 
            }
            defaults[f.fieldname] = val
        }
    })
    return defaults
}

// Reuse depends_on logic for the wrapper div
function evaluateDependsOn(expression, doc) {
    if (!expression) return true
    if (expression.startsWith && expression.startsWith('eval:')) {
        try {
            const code = expression.substring(5)
            const fn = new Function('doc', `return ${code}`)
            return fn(doc)
        } catch (e) {
            return true 
        }
    }
    if (doc[expression]) return true
    return !!doc[expression]
}

function isFieldVisible(field, doc) {
    if (field.hidden) return false
    if (field.depends_on) {
        return evaluateDependsOn(field.depends_on, doc)
    }
    return true
}

function openAddModal() {
    editingRowIndex.value = -1
    // Initialize defaults
    const defaults = { idx: rows.value.length + 1 }
    
    // Process field defaults
    if (meta.value && meta.value.fields) {
        const dynamicDefaults = processDefaults(meta.value.fields)
        Object.assign(defaults, dynamicDefaults)
    }
    
    editingRow.value = JSON.parse(JSON.stringify(defaults))
    isModalOpen.value = true
}

function openEditModal(row, index) {
    editingRowIndex.value = index
    editingRow.value = JSON.parse(JSON.stringify(row))
    isModalOpen.value = true
}

function saveRow() {
    if (editingRowIndex.value === -1) {
        // Add new
        rows.value.push(editingRow.value)
    } else {
        // Update existing
        rows.value.splice(editingRowIndex.value, 1, editingRow.value)
    }
    isModalOpen.value = false
    editingRow.value = null
}

function removeRow(index) {
    rows.value.splice(index, 1)
}

onMounted(() => {
    fetchMeta()
})

</script>

<style scoped>
/* Read-only table text style */
td {
    vertical-align: middle;
}
</style>
