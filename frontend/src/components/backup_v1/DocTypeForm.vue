<template>
  <AppLayout content-width="max-w-[95%]">
    <div v-if="loading" class="flex justify-center items-center py-40">
        <div class="flex flex-col items-center gap-4">
             <div class="animate-spin h-10 w-10 border-3 border-blue-600 border-t-transparent rounded-full shadow-lg shadow-blue-500/30"></div>
             <div class="text-slate-400 font-medium animate-pulse">Form Yükleniyor...</div>
        </div>
    </div>
    
    <div v-else-if="error" class="flex justify-center py-20">
        <div class="text-center max-w-md">
            <div class="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Bir hata oluştu</h3>
            <p class="text-slate-500 mb-6">{{ error }}</p>
            <Button variant="outline" @click="$router.push(`/auto/${doctype.toLowerCase()}`)">Listeye Dön</Button>
        </div>
    </div>

    <div v-else class="space-y-6 pb-20">
       <!-- Header Section (Clean) -->
       <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-slate-200/60 pb-6">
           <div class="flex items-center gap-4">
                <!-- Back Button -->
                <button 
                    @click="$router.push(`/auto/${doctype.toLowerCase()}`)"
                    class="w-10 h-10 rounded-xl border border-slate-200 text-slate-500 flex items-center justify-center hover:bg-slate-50 hover:text-slate-900 transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                </button>

                <div>
                   <div class="flex items-center gap-2 text-sm text-slate-500 mb-1">
                        <span class="hover:text-slate-900 cursor-pointer transition-colors" @click="$router.push(`/auto/${doctype.toLowerCase()}`)">{{ doctypeName }}</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-300"><polyline points="9 18 15 12 9 6"/></svg>
                        <span class="text-slate-900 font-medium">{{ doc.name || 'Yeni Kayıt' }}</span>
                   </div>
                   
                   <div class="flex items-center gap-3">
                        <Avatar 
                            v-if="doc.name"
                            :label="doc[titleField] || doc.name" 
                            :image="imageField ? doc[imageField] : null" 
                            size="md" 
                        />
                        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">
                            {{ doc[titleField] || doc.name || `Yeni ${doctypeName}` }}
                        </h1>
                        <!-- Status Badge -->
                        <Badge 
                            v-if="doc.docstatus !== undefined"
                            :variant="getDocStatusVariant(doc.docstatus)" 
                            class="ml-2"
                        >
                            {{ getDocStatusLabel(doc.docstatus) }}
                        </Badge>
                   </div>
               </div>
           </div>
           
           <div class="flex items-center gap-3">
               <!-- View Mode: Edit Button -->
               <Button 
                   v-if="!isEditMode && doc.name"
                   variant="solid" 
                   theme="blue" 
                   icon-left="Edit"
                   class="shadow-lg shadow-blue-500/20"
                   @click="router.push(`/auto/${doctype.toLowerCase()}/${doc.name}/edit`)"
               >
                   Düzenle
               </Button>

                <!-- Custom Actions Dropdown -->
                <Dropdown 
                    v-if="customActions.length > 0" 
                    label="İşlemler" 
                    :options="customActions"
                    class="shadow-lg shadow-blue-500/20"
                />
               
               <!-- Edit Mode: Workflow & Standard Actions -->
               <template v-if="isEditMode">
                   
                    <!-- Standard Actions -->
                   <Button variant="ghost" theme="gray" icon-left="Trash" @click="confirmDelete = true" v-if="doc.name && doc.docstatus !== 1" class="text-red-600 hover:bg-red-50 hover:text-red-700">Sil</Button>
                   <Button variant="outline" @click="$router.back()" v-if="!doc.name">İptal</Button>

                   <!-- Workflow Actions -->
                   <Button 
                       v-for="action in workflowActions" 
                       :key="action.action"
                       :variant="action.variant"
                       :theme="action.theme"
                       :icon-left="action.icon"
                       @click="handleWorkflowAction(action.action)"
                   >
                       {{ action.label }}
                   </Button>
                   
                   <Button variant="solid" theme="blue" icon-left="Save" :loading="saving" @click="saveDoc" v-if="doc.docstatus !== 1" class="shadow-lg shadow-blue-500/20">Kaydet</Button>
               </template>
           </div>
       </div>

       <!-- Form Card -->
       <div class="bg-white rounded-2xl border border-slate-200/60 shadow-sm">
           
           <!-- Tab Header (if multiple tabs) -->
           <div v-if="formLayout.length > 1" class="bg-slate-50/50 border-b border-slate-200 px-6 pt-4 rounded-t-2xl">
                <div class="flex gap-6 overflow-x-auto">
                    <button 
                        v-for="tab in formLayout" 
                        :key="tab.name"
                        @click="activeTab = tab.name"
                        class="pb-4 text-sm font-medium border-b-2 transition-all whitespace-nowrap px-1"
                        :class="activeTab === tab.name ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'"
                    >
                        {{ tab.label }}
                    </button>
                </div>
           </div>

           <!-- Tab Content -->
           <div class="p-8">
                <template v-for="tab in formLayout" :key="tab.name">
                    <div v-show="activeTab === tab.name || formLayout.length <= 1">
                        
                        <!-- Iterate Sections -->
                        <div v-for="(section, sIndex) in tab.sections" :key="sIndex" class="mb-8 last:mb-0">
                            
                            <!-- Section Header -->
                            <div v-if="section.label" class="mb-4 text-base font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
                                {{ section.label }}
                            </div>

                            <!-- Section Grid (Row) -->
                            <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
                                
                                <!-- Iterate Columns -->
                                <div 
                                    v-for="(column, cIndex) in section.columns" 
                                    :key="cIndex"
                                    class="col-span-1"
                                    :class="{
                                        'md:col-span-12': section.columns.length === 1,
                                        'md:col-span-6': section.columns.length === 2,
                                        'md:col-span-4': section.columns.length === 3,
                                        'md:col-span-3': section.columns.length === 4
                                    }"
                                >
                                    <div class="space-y-6">
                                        <!-- Iterate Fields -->
                                        <template v-for="field in column.fields" :key="field.fieldname">
                                            
                                            <!-- Full Width Types (Override column span if needed, but usually fit in column) -->
                                            <!-- If inside a column, they just take full width of that column -->
                                            
                                            <div class="w-full transition-opacity" :class="isFieldDisabled(field) ? 'opacity-70' : ''">

                                                 <!-- Table Field -->
                                                <div v-if="field.fieldtype === 'Table'">
                                                    <label class="block text-sm font-semibold text-slate-900 mb-3 flex items-center justify-between">
                                                        <span>{{ field.label }}{{ field.reqd ? ' *' : '' }}</span>
                                                        <span class="text-xs font-normal text-slate-400 bg-slate-50 px-2 py-1 rounded">Tablo</span>
                                                    </label>
                                                    <div class="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                                                        <EditableTable 
                                                            v-model="doc[field.fieldname]"
                                                            :columns="getTableColumns(field)"
                                                            :disabled="!isEditMode"
                                                            :empty-message="`Henüz ${field.label} eklenmedi`"
                                                            :add-button-label="`${field.label} Ekle`"
                                                            @edit-row="openRowEdit($event, field)"
                                                        />
                                                    </div>
                                                </div>

                                                <!-- Text Editor / Long Text -->
                                                <div v-else-if="['Text Editor', 'Long Text', 'Small Text', 'HTML', 'Code'].includes(field.fieldtype)">
                                                     <label class="block text-sm font-medium text-slate-700 mb-2">
                                                        {{ field.label }}{{ field.reqd ? ' *' : '' }}
                                                    </label>
                                                    <textarea 
                                                        v-model="doc[field.fieldname]"
                                                        :rows="field.fieldtype === 'Text Editor' ? 10 : field.fieldtype === 'Small Text' ? 3 : 5"
                                                        :disabled="isFieldDisabled(field)"
                                                        class="block w-full rounded-xl border-slate-200 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base px-4 py-3 bg-slate-50 focus:bg-white transition-colors"
                                                    ></textarea>
                                                </div>

                                                <!-- Normal Inputs -->
                                                
                                                <!-- Data / Int / Float / etc -->
                                                <TextInput 
                                                    v-else-if="['Data', 'Int', 'Float', 'Date', 'Datetime', 'Time', 'Password', 'Duration', 'Barcode', 'Dynamic Link'].includes(field.fieldtype)"
                                                    :label="field.label + (field.reqd ? ' *' : '')"
                                                    v-model="doc[field.fieldname]"
                                                    :type="getInputType(field.fieldtype)"
                                                    :required="field.reqd"
                                                    :disabled="isFieldDisabled(field)"
                                                    class="w-full"
                                                />

                                                <!-- Link / Select -->
                                                <Combobox 
                                                    v-else-if="['Link', 'Select'].includes(field.fieldtype)"
                                                    :label="field.label + (field.reqd ? ' *' : '')"
                                                    :options="getFieldOptions(field)"
                                                    v-model="doc[field.fieldname]"
                                                    :required="field.reqd"
                                                    :disabled="isFieldDisabled(field)"
                                                    class="w-full"
                                                />
                                                
                                                <!-- Currency -->
                                                <div v-else-if="field.fieldtype === 'Currency'">
                                                    <label class="block text-sm font-medium text-slate-700 mb-1.5">
                                                        {{ field.label }}{{ field.reqd ? ' *' : '' }}
                                                    </label>
                                                    <div class="relative">
                                                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 z-10">
                                                            <span class="text-slate-500 font-semibold">₺</span>
                                                        </div>
                                                        <input
                                                            type="number"
                                                            v-model="doc[field.fieldname]"
                                                            :disabled="isFieldDisabled(field)"
                                                            :required="field.reqd"
                                                            class="block w-full rounded-xl border-slate-200 pl-10 pr-4 py-2.5 text-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-slate-100 transition-shadow"
                                                            step="0.01"
                                                            placeholder="0.00"
                                                        />
                                                    </div>
                                                </div>

                                                <!-- Check -->
                                                <div v-else-if="field.fieldtype === 'Check'" class="pt-8 pl-1">
                                                    <Toggle 
                                                        :label="field.label"
                                                        v-model="doc[field.fieldname]"
                                                        :disabled="isFieldDisabled(field)"
                                                    />
                                                </div>
                                                
                                                <!-- Read Only -->
                                                <div v-else-if="field.fieldtype === 'Read Only'" class="pt-1">
                                                    <label class="block text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">
                                                        {{ field.label }}
                                                    </label>
                                                    <p class="text-sm font-medium text-slate-900 truncate">
                                                        {{ doc[field.fieldname] || '-' }}
                                                    </p>
                                                </div>
                                                
                                                <!-- Color -->
                                                <div v-else-if="field.fieldtype === 'Color'">
                                                    <label class="block text-sm font-medium text-slate-700 mb-2">
                                                        {{ field.label }}{{ field.reqd ? ' *' : '' }}
                                                    </label>
                                                    <input 
                                                        type="color"
                                                        v-model="doc[field.fieldname]"
                                                        :disabled="field.read_only"
                                                        class="h-10 w-20 rounded-lg border border-slate-200 cursor-pointer"
                                                    />
                                                </div>

                                                <!-- Image Display (Special case inside normal flow if not filtered out) -->
                                                <div v-else-if="field.fieldtype === 'Image'">
                                                     <div class="bg-slate-50 rounded-xl border border-slate-200 p-4 max-w-sm">
                                                        <label class="block text-sm font-bold text-slate-700 mb-3 block">
                                                            {{ field.label }}
                                                        </label>
                                                        <div class="relative group">
                                                            <div v-if="doc[field.fieldname]" class="w-full h-48 rounded-lg border-2 border-white shadow-sm overflow-hidden bg-white">
                                                                <img :src="doc[field.fieldname]" :alt="field.label" class="w-full h-full object-contain" />
                                                            </div>
                                                            <div v-else class="w-full h-48 rounded-lg border-2 border-dashed border-slate-300 flex flex-col items-center justify-center bg-slate-100 text-slate-400 gap-2">
                                                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                                                                <span class="text-xs font-medium">Görsel Yok</span>
                                                            </div>
                                                            <label v-if="isEditMode" class="btn btn-sm w-full mt-3 border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm rounded-lg py-2 text-xs font-medium cursor-pointer text-center block transition-all">
                                                                {{ doc[field.fieldname] ? 'Değiştir' : 'Yükle' }}
                                                                <input type="file" accept="image/*" class="hidden" @change="(e) => handleImageUpload(e, field.fieldname)" />
                                                            </label>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                                <div v-else-if="['Attach', 'Attach Image'].includes(field.fieldtype)">
                                                    <label class="block text-sm font-medium text-slate-700 mb-2">
                                                        {{ field.label }}{{ field.reqd ? ' *' : '' }}
                                                    </label>
                                                    <div class="flex items-center gap-3">
                                                        <input 
                                                            v-if="isEditMode"
                                                            type="file"
                                                            @change="(e) => handleFileUpload(e, field.fieldname)"
                                                            class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                                                        />
                                                        <a v-if="doc[field.fieldname]" :href="doc[field.fieldname]" target="_blank" class="text-blue-600 hover:text-blue-700 text-sm">
                                                            Görüntüle
                                                        </a>
                                                    </div>
                                                </div>
                                                
                                                <!-- Fallback -->
                                                <div v-else class="text-xs text-red-400 italic pt-2">
                                                    {{ field.label }} ({{ field.fieldtype }}) - Desteklenmiyor
                                                </div>

                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
                
                <!-- No Tabs Fallback -->
                <div v-if="formLayout.length === 0" class="text-center py-10 text-slate-400">
                    Görüntülenecek alan bulunamadı.
                </div>
           </div>
       </div>
    </div>
    
    <!-- Row Edit Modal -->
    <Dialog v-model="showRowModal" :options="{ size: 'xl' }">
        <template #body-content>
            <div class="p-6 bg-white min-h-[400px]">
                <h3 class="text-xl font-bold text-slate-900 mb-6 border-b pb-4">
                    {{ editingField ? editingField.label : 'Satır Düzenle' }} ({{ editingRowIndex + 1 }}. Satır)
                </h3>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6" v-if="editingField && childMetas[editingField.options]">
                    <template v-for="field in childMetas[editingField.options].fields" :key="field.fieldname">
                         <div v-if="!field.hidden && !['Section Break', 'Column Break', 'Tab Break'].includes(field.fieldtype)" class="col-span-1" :class="['Text Editor', 'Long Text', 'Small Text'].includes(field.fieldtype) ? 'md:col-span-2' : ''">
                            
                            <!-- Simplified Renderer for Dialog -->
                            <!-- Text/Data -->
                            <TextInput 
                                v-if="['Data', 'Int', 'Float', 'Date', 'Datetime', 'Time', 'Duration'].includes(field.fieldtype)"
                                :label="field.label"
                                v-model="editingRow[field.fieldname]"
                                :type="getInputType(field.fieldtype)"
                                :disabled="field.read_only"
                            />
                            
                            <!-- Currency -->
                            <div v-else-if="field.fieldtype === 'Currency'">
                                <label class="block text-sm font-medium text-slate-700 mb-1.5">{{ field.label }}</label>
                                <div class="relative">
                                    <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 z-10">
                                        <span class="text-slate-500 font-semibold">₺</span>
                                    </div>
                                    <input type="number" step="0.01" v-model="editingRow[field.fieldname]" :disabled="field.read_only" class="block w-full rounded-xl border-slate-200 pl-10 pr-4 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-slate-100 placeholder-slate-400 shadow-sm" />
                                </div>
                            </div>

                            <!-- Link/Select -->
                            <Combobox 
                                v-else-if="['Link', 'Select'].includes(field.fieldtype)"
                                :label="field.label"
                                :options="field.fieldtype === 'Link' ? (linkOptions[field.fieldname] || []) : getFieldOptions(field)"
                                v-model="editingRow[field.fieldname]"
                                :disabled="field.read_only"
                            />

                            <!-- Check -->
                            <div v-else-if="field.fieldtype === 'Check'" class="pt-6">
                                <Toggle :label="field.label" v-model="editingRow[field.fieldname]" :disabled="field.read_only" />
                            </div>

                            <!-- Text Area -->
                            <div v-else-if="['Text Editor', 'Small Text', 'Long Text'].includes(field.fieldtype)">
                                <label class="block text-sm font-medium text-slate-700 mb-2">{{ field.label }}</label>
                                <textarea v-model="editingRow[field.fieldname]" rows="3" class="w-full rounded-xl border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 block"></textarea>
                            </div>
                            
                            <!-- Read Only -->
                            <div v-else-if="field.read_only || field.fieldtype === 'Read Only'" class="pt-1">
                                <span class="text-xs uppercase text-slate-400 font-bold block mb-1">{{ field.label }}</span>
                                <span class="text-slate-800 font-medium">{{ editingRow[field.fieldname] || '-' }}</span>
                            </div>

                        </div>
                    </template>
                </div>
            </div>
        </template>
        <template #actions>
            <div class="px-6 pb-6 pt-4 flex justify-end gap-3 bg-white border-t rounded-b-xl">
                <Button variant="outline" @click="showRowModal = false">İptal</Button>
                <Button variant="solid" theme="blue" @click="saveRowEdit">Tamam</Button>
            </div>
        </template>
    </Dialog>

    <ConfirmDialog 
        v-model="confirmDelete"
        title="Kaydı Sil"
        message="Bu kaydı silmek istediğinize emin misiniz? Bu işlem geri alınamaz."
        @confirm="deleteDoc"
    />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { frappeRequest, Dialog } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import Button from '@/components/Button.vue'
import TextInput from '@/components/TextInput.vue'
import Combobox from '@/components/Combobox.vue'
import Toggle from '@/components/Toggle.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EditableTable from '@/components/EditableTable.vue'
import Avatar from '@/components/Avatar.vue'
import Badge from '@/components/Badge.vue'
import { useToast } from '@/composables/useToast'
import Dropdown from '@/components/Dropdown.vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true
  },
  id: String
})

const route = useRoute()
const router = useRouter()
const toast = useToast()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const confirmDelete = ref(false)

const allCustomActions = ref([])
const customActions = computed(() => {
    return allCustomActions.value
        .filter(action => {
            if (!action.kosul) return true
            try {
                // Evaluate condition against current doc
                // Only run if doc is loaded (has name)
                if (!doc.value || !doc.value.name) return false
                return new Function('doc', `return ${action.kosul}`)(doc.value)
            } catch (e) {
                console.warn(`Condition error for ${action.buton_etiketi}:`, e)
                return false
            }
        })
        .map(action => ({
            label: action.buton_etiketi,
            action: () => executeAction({
                action_type: action.aksiyon_tipi,
                method: action.metot_veya_rota
            })
        }))
})

const meta = ref(null)
const doc = ref({})
const linkOptions = ref({})
const childMetas = ref({}) 
const activeTab = ref('') 

// Row Edit State
const showRowModal = ref(false)
const editingRow = ref({})
const editingRowIndex = ref(-1)
const editingField = ref(null)

function openRowEdit(index, field) {
    editingRowIndex.value = index
    editingField.value = field
    // Clone to avoid direct mutation/formatting issues until save
    editingRow.value = { ...doc.value[field.fieldname][index] }
    showRowModal.value = true
}

function saveRowEdit() {
    if (editingRowIndex.value > -1 && editingField.value) {
        // Apply back
        doc.value[editingField.value.fieldname][editingRowIndex.value] = { ...editingRow.value }
    }
    showRowModal.value = false
} 

// Capitalize first letter of EACH word for Frappe
const doctypeName = computed(() => {
  if (!props.doctype) return ''
  return props.doctype
    .replace(/-/g, ' ') // Replace hyphens with spaces
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
})



const titleField = computed(() => meta.value?.title_field || null)
const imageField = computed(() => meta.value?.image_field || null)

// Edit mode check
const isEditMode = computed(() => {
  if (!props.id || props.id === 'new') return true
  return route.path.endsWith('/edit')
})

const isFieldDisabled = (field) => {
  if (!isEditMode.value) return true
  return field.read_only
}

// Input Type Helper
const getInputType = (fieldtype) => {
    switch(fieldtype) {
        case 'Int': 
        case 'Float': 
        case 'Currency': 
        case 'Percent':
            return 'number'
        case 'Date': return 'date'
        case 'Datetime': return 'datetime-local'
        case 'Time': return 'time'
        case 'Password': return 'password'
        default: return 'text'
    }
}

// Field Options Helper
const getFieldOptions = (field) => {
    if (field.fieldtype === 'Select') {
        return (field.options || '').split('\n').filter(o => o.trim()).map(o => ({ label: o.trim(), value: o.trim() }))
    }
    if (field.fieldtype === 'Link') {
        return linkOptions.value[field.fieldname] || []
    }
    return []
}

// Status Helpers
const getDocStatusLabel = (status) => {
    switch(status) {
        case 0: return 'Taslak'
        case 1: return 'Gönderildi'
        case 2: return 'İptal Edildi'
        default: return ''
    }
}

const getDocStatusVariant = (status) => {
    switch(status) {
        case 0: return 'gray' // Draft
        case 1: return 'green' // Submitted
        case 2: return 'red' // Cancelled
        default: return 'gray'
    }
}

// Hierarchical Layout Logic: Tabs > Sections > Columns > Fields
const formLayout = computed(() => {
  if (!meta.value || !meta.value.fields) return []
  
  const layout = []
  
  // Helpers to create structure
  const createColumn = () => ({ fields: [] })
  const createSection = (label = '') => ({ label, columns: [createColumn()] })
  const createTab = (label = 'Genel', name = 'tab-0') => ({ label, name, sections: [createSection()] })
  
  // Initialize with first tab
  let currentTab = createTab()
  let currentSection = currentTab.sections[0]
  let currentColumn = currentSection.columns[0]
  let tabIndex = 0
  
  for (const field of meta.value.fields) {
    if (field.hidden === 1) continue
    
    // Tab Break (New Tab > New Section > New Column)
    if (field.fieldtype === 'Tab Break') {
        // Push previous tab if it has content in its last section/column OR if layout is empty (first tab)
        // Better logic: Always push the current tab if we are hitting a break, unless it's strictly empty and we haven't started.
        // But if Tab Break is first field, currentTab is empty. We should push the *new* tab, not the old one.
        
        // If we have content in the current tab, push it.
        const hasContent = currentTab.sections.some(s => s.columns.some(c => c.fields.length > 0));
        if (hasContent || layout.length === 0) {
             // If it's the very first tab (default) and it's empty, we might skip it if we strictly want tab breaks to define structure.
             // But Frappe usually keeps the default 'Details' tab if fields exist before the first break.
             if (hasContent) layout.push(currentTab)
        }
        
        tabIndex++
        currentTab = createTab(field.label || `Sekme ${tabIndex}`, `tab-${tabIndex}`)
        currentSection = currentTab.sections[0]
        currentColumn = currentSection.columns[0]
    }
    
    // Section Break (New Section in current Tab > New Column)
    else if (field.fieldtype === 'Section Break') {
        currentSection = createSection(field.label)
        currentTab.sections.push(currentSection)
        currentColumn = currentSection.columns[0]
    }
    
    // Column Break (New Column in current Section)
    else if (field.fieldtype === 'Column Break') {
        currentColumn = createColumn()
        currentSection.columns.push(currentColumn)
    }
    
    // Normal Fields
    else if (!['HTML', 'Heading', 'Button'].includes(field.fieldtype)) {
        currentColumn.fields.push(field)
    }
  }
  
  // Push the last tab if it has content
  if (currentTab.sections.some(s => s.columns.some(c => c.fields.length > 0))) {
      layout.push(currentTab)
  }
  
  // Create default tab if nothing exists
  if (layout.length === 0 && meta.value.fields.length > 0) {
      const defaultFields = meta.value.fields.filter(f => !f.hidden && !['HTML', 'Heading', 'Button', 'Tab Break', 'Section Break', 'Column Break'].includes(f.fieldtype))
      if (defaultFields.length > 0) {
          const tab = createTab('Tümü', 'tab-0')
          tab.sections[0].columns[0].fields = defaultFields
          layout.push(tab)
      }
  }
  
  return layout
})

// Update activeTab logic to use formLayout
watch(formLayout, (newLayout) => {
  if (newLayout.length > 0 && !activeTab.value) {
    activeTab.value = newLayout[0].name
  }
}, { immediate: true })

// Workflow Actions
const workflowActions = computed(() => {
  const actions = []
  if (!doc.value.name) return actions
  
  if (meta.value?.is_submittable && doc.value.docstatus === 0) {
    actions.push({ label: 'Gönder', action: 'submit', variant: 'solid', theme: 'blue', icon: 'Send' })
  }
  
  if (doc.value.docstatus === 1) {
    actions.push({ label: 'İptal Et', action: 'cancel', variant: 'outline', theme: 'red', icon: 'X' })
  }
  
  if (doc.value.docstatus === 2) {
    actions.push({ label: 'Düzelt', action: 'amend', variant: 'outline', theme: 'gray', icon: 'Edit' })
  }
  
  return actions
})

// Custom Actions Logic
async function fetchCustomActions() {
    try {
        const actions = await frappeRequest({
            url: 'frappe.client.get_list',
            params: {
                doctype: 'Arch Action',
                filters: {
                    ilgili_belge: doctypeName.value,
                    aktif: 1
                },
                fields: ['buton_etiketi', 'aksiyon_tipi', 'metot_veya_rota', 'kosul']
            }
        })
        


        allCustomActions.value = actions
    } catch (e) {
        // Silent fail or log
        console.warn('Failed to fetch custom actions:', e)
    }
}

async function executeAction(action) {
    if (action.action_type === 'Route') {
        router.push(action.method)
    } else if (action.action_type === 'Server Method') {
        loading.value = true
        try {
            const response = await frappeRequest({
                url: action.method,
                method: 'POST',
                params: {
                    source_name: doc.value.name, // Required for make_mapped_doc methods
                    name: doc.value.name, 
                    ...doc.value
                }
            })
            
            // Check if backend returned a new document name (string)
            // Standard frappe responses usually wrap return value in 'message'
            let result = response
            if (response && response.message) {
                result = response.message
            }

            toast.success('İşlem Başarılı')

            // Handle Object Response (Mapped Document)
            if (typeof result === 'object' && result !== null && Object.keys(result).length > 0) {
                 // It's a document (mapped doc)
                 const targetDoctype = result.doctype // Required field in Frappe docs
                 
                 if (targetDoctype) {
                     toast.success('Yeni Belge Oluşturuluyor...')
                     
                     // Helper: Convert "Satis Faturasi" -> "satis-faturasi" (kebap-case) for URL
                     const urlSlug = targetDoctype.replace(/ /g, '-').toLowerCase()
                     
                     router.push({
                         path: `/auto/${urlSlug}/new`,
                         state: { prefilled: result }
                     })
                     return
                 }
            }

            // Legacy String Response (Created Name)
            if (typeof result === 'string' && result !== doc.value.name && result.length > 0) {
                 if (result !== 'success' && result !== 'OK') {
                     toast.success('Yeni Kayıt: ' + result)
                 }
                 await fetchDoc() // Just reload current if it was a background action
            } else {
                 await fetchDoc()
            }

        } catch (e) {
            console.error('Action failed:', e)
            toast.error('İşlem Başarısız', e.message)
        } finally {
            loading.value = false
        }
    }
}

watch(() => props.doctype, () => {
    customActions.value = []
    fetchCustomActions()
}, { immediate: true })

async function fetchMeta() {
  try {
    const response = await frappeRequest({
      url: 'frappe.desk.form.load.getdoctype',
      params: { doctype: doctypeName.value, with_parent: 1 }
    })
    meta.value = response.docs[0]
    await fetchLinkOptions()
    await fetchChildMetas()
  } catch (e) {
    console.error('Failed to fetch meta:', e)
    error.value = 'DocType meta verisi yüklenemedi'
  }
}

async function fetchChildMetas() {
  if (!meta.value) return
  const tableFields = meta.value.fields.filter(f => f.fieldtype === 'Table')
  
  for (const field of tableFields) {
    try {
      const response = await frappeRequest({
        url: 'frappe.desk.form.load.getdoctype',
        params: { doctype: field.options }
      })
      childMetas.value[field.options] = response.docs[0]
      
      const childLinkFields = response.docs[0].fields.filter(f => f.fieldtype === 'Link')
      for (const childField of childLinkFields) {
        try {
          const data = await frappeRequest({
            url: 'frappe.client.get_list',
            params: { doctype: childField.options, fields: ['name'], limit_page_length: 1000 }
          })
          linkOptions.value[childField.fieldname] = data.map(d => ({ label: d.name, value: d.name }))
        } catch (e) {
           // efficient error handling 
        }
      }
    } catch (e) {
      console.error(`Failed to fetch child meta for ${field.options}:`, e)
    }
  }
}

async function fetchLinkOptions() {
  if (!meta.value) return
  const linkFields = meta.value.fields.filter(f => f.fieldtype === 'Link')
  
  for (const field of linkFields) {
    if (!field.link_filters) {
        // No filters, fetch standard list
        await fetchOptionsForField(field, {})
        continue
    }

    try {
        const filters = JSON.parse(field.link_filters)
        let isDynamic = false
        const dependencies = []

        // Check for dynamic filters (eval:doc.field)
        for (const [key, value] of Object.entries(filters)) {
            if (typeof value === 'string' && value.startsWith('eval:')) {
                isDynamic = true
                const dependency = value.replace('eval:doc.', '')
                dependencies.push(dependency)
            }
        }

        if (isDynamic && dependencies.length > 0) {
            // Watch dependencies
            dependencies.forEach(dep => {
                watch(() => doc.value[dep], async () => {
                   await resolveAndFetchOptions(field, filters)
                })
            })
            // Initial fetch
            await resolveAndFetchOptions(field, filters)
        } else {
            // Static filters
            await fetchOptionsForField(field, filters)
        }

    } catch (e) {
        console.warn(`Invalid link_filters for ${field.fieldname}`, e)
        // Fallback to no filter
        await fetchOptionsForField(field, {})
    }
  }
}

async function resolveAndFetchOptions(field, rawFilters) {
    const finalFilters = {}
    let missingDependency = false

    for (const [key, value] of Object.entries(rawFilters)) {
        if (typeof value === 'string' && value.startsWith('eval:')) {
            const depField = value.replace('eval:doc.', '')
            const depValue = doc.value[depField]
            
            if (!depValue) {
                missingDependency = true
                break
            }
            finalFilters[key] = depValue
        } else {
            finalFilters[key] = value
        }
    }

    if (missingDependency) {
        linkOptions.value[field.fieldname] = []
        return
    }
    
    await fetchOptionsForField(field, finalFilters)
}

async function fetchOptionsForField(field, filters) {
    try {
      const data = await frappeRequest({
        url: 'frappe.client.get_list',
        params: { 
            doctype: field.options, 
            fields: ['name'], 
            limit_page_length: 1000,
            filters: filters
        }
      })
      linkOptions.value[field.fieldname] = data.map(d => ({ label: d.name, value: d.name }))
    } catch (e) { /* ignore */ }
}

async function fetchDoc() {
  loading.value = true
  try {
    await fetchMeta()
    if (props.id && props.id !== 'new') {
      const data = await frappeRequest({
        url: 'frappe.client.get',
        params: { doctype: doctypeName.value, name: props.id }
      })
      doc.value = data
    } else {
      // Initialize with defaults
      doc.value = { doctype: doctypeName.value, docstatus: 0 }
      meta.value.fields.forEach(f => {
        if (f.default) {
            if (['Check', 'Int'].includes(f.fieldtype)) {
                doc.value[f.fieldname] = parseInt(f.default)
            } else if (f.fieldtype === 'Float' || f.fieldtype === 'Currency') {
                doc.value[f.fieldname] = parseFloat(f.default)
            } else {
                doc.value[f.fieldname] = f.default
            }
        }
      })

      // Check for prefilled data from mapping action
      if (history.state && history.state.prefilled) {
          const prefilled = history.state.prefilled
          // Ensure we don't overwrite doctype/name if they are crucial (usually mapped doc has them correct)
          Object.assign(doc.value, prefilled)
          
          // Reset name to allow "New" behavior if mapped doc had a temp name or no name
          // Usually mapped doc doesn't have a final name yet, or it's 'New Entity 1'.
          // Frappe mapper might return 'name' as source name sometimes? No, it returns new structure.
          // Let's ensure name is not set effectively to 'new' or keep it if it's auto-generated draft
          delete doc.value.name
          delete doc.value.creation
          delete doc.value.modified
      }
    }
  } catch (e) {
    error.value = 'Kayıt yüklenemedi'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function saveDoc() {
  saving.value = true
  try {
    const method = doc.value.name ? 'frappe.client.save' : 'frappe.client.insert'
    const updated = await frappeRequest({
      url: method,
      params: { doc: doc.value }
    })
    doc.value = updated
    toast.success('Kaydedildi', 'Kayıt başarıyla güncellendi.')
    if (!props.id || props.id === 'new') {
      router.push(`/auto/${props.doctype.toLowerCase()}/${updated.name}`)
    }
  } catch (e) {
    toast.error('Hata', 'Kaydetme işlemi başarısız.')
    console.error(e)
  } finally {
    saving.value = false
  }
}

function getTableColumns(field) {
  const childMeta = childMetas.value[field.options]
  if (!childMeta) return []
  
  let cols = childMeta.fields.filter(f => f.in_list_view && !['name', 'parent', 'parenttype', 'parentfield'].includes(f.fieldname))
  
  // Fallback if no list view fields defined
  if (cols.length === 0) {
      cols = childMeta.fields.filter(f => !f.hidden && !['Section Break', 'Column Break', 'Tab Break'].includes(f.fieldtype)).slice(0, 4)
  }

  return cols.map(f => ({
      label: f.label,
      key: f.fieldname,
      type: f.fieldtype === 'Link' ? 'select' : f.fieldtype === 'Currency' ? 'currency' : 'text',
      options: f.fieldtype === 'Link' ? linkOptions.value[f.fieldname] || [] : undefined,
      placeholder: f.label,
      fieldtype: f.fieldtype 
    }))
}

function handleImageUpload(event, fieldname) {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    doc.value[fieldname] = e.target.result
    toast.info('Bilgi', 'Görsel yükleme backend ile entegre edilecek.')
  }
  reader.readAsDataURL(file)
}

function handleFileUpload(event, fieldname) {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    doc.value[fieldname] = e.target.result
    toast.info('Bilgi', 'Dosya yükleme backend ile entegre edilecek.')
  }
  reader.readAsDataURL(file)
}

async function handleWorkflowAction(action) {
  try {
    if (action === 'submit') await submitDoc()
    else if (action === 'cancel') await cancelDoc()
    else if (action === 'amend') await amendDoc()
  } catch (e) {
    console.error('Workflow action failed:', e)
  }
}

async function submitDoc() {
  saving.value = true
  try {
    const response = await frappeRequest({
        url: 'frappe.client.submit',
        params: { doc: doc.value }
    })
    doc.value = response
    toast.success('Gönderildi', 'Belge başarıyla gönderildi.')
  } catch (e) {
    toast.error('Hata', e.message || 'Gönderme işlemi başarısız.')
  } finally {
    saving.value = false
  }
}

async function cancelDoc() {
  saving.value = true
  try {
    const response = await frappeRequest({
        url: 'frappe.client.cancel',
        params: { doc: doc.value }
    })
    doc.value = response
    toast.success('İptal Edildi', 'Belge başarıyla iptal edildi.')
  } catch (e) {
    toast.error('Hata', e.message || 'İptal işlemi başarısız.')
  } finally {
    saving.value = false
  }
}

async function amendDoc() {
  try {
    const response = await frappeRequest({
        url: 'frappe.client.amend_doc',
        params: { doctype: doctypeName.value, name: doc.value.name }
    })
    toast.success('Düzeltme Oluşturuldu', 'Yeni düzeltme belgesi oluşturuldu.')
    router.push(`/auto/${props.doctype.toLowerCase()}/${response.name}`)
  } catch (e) {
    toast.error('Hata', e.message || 'Düzeltme işlemi başarısız.')
  }
}

async function deleteDoc() {
  try {
    await frappeRequest({
        url: 'frappe.client.delete',
        params: { doctype: doctypeName.value, name: doc.value.name }
    })
    toast.success('Silindi', 'Kayıt başarıyla silindi.')
    router.push(`/auto/${props.doctype.toLowerCase()}`)
  } catch (e) {
    toast.error('Hata', 'Silme işlemi başarısız.')
  }
}

onMounted(() => {
  fetchDoc()
})
</script>
