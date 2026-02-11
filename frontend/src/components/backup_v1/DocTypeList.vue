<template>
  <AppLayout content-width="max-w-[95%]">
    <div class="space-y-8 pb-12">
       <!-- Header Section (Clean) -->
       <div class="flex flex-col gap-6">
           <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
               <div>
                   <div class="flex items-center gap-2 text-sm text-slate-500 mb-1">
                        <span class="hover:text-slate-900 cursor-pointer transition-colors" @click="$router.push('/')">Ana Sayfa</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-300"><polyline points="9 18 15 12 9 6"/></svg>
                        <span class="text-slate-900 font-medium">{{ doctypeNameTitleCase }}</span>
                   </div>
                   <h1 class="text-3xl font-bold text-slate-900 tracking-tight">{{ doctypeNameTitleCase }}</h1>
               </div>
               
               <div class="flex items-center gap-3">
                   <Button variant="outline" icon-left="Download">Dışa Aktar</Button>
                   <Button variant="solid" theme="blue" icon-left="Plus" class="shadow-lg shadow-blue-500/30" @click="navigateToNew">Yeni Ekle</Button>
               </div>
           </div>

           <!-- Toolbar (Search & Filters) -->
           <div class="bg-white p-2 rounded-2xl border border-slate-200/60 shadow-sm flex flex-col md:flex-row gap-2 items-center justify-between">
               
               <!-- Search -->
                <div class="relative w-full md:w-96 order-2 md:order-1">
                    <input 
                        type="text"
                        placeholder="Kayıt ara..." 
                        v-model="searchQuery" 
                        @input="handleSearch"
                        class="w-full pl-10 pr-4 py-2 bg-transparent border-none text-sm focus:ring-0 placeholder-slate-400 text-slate-700"
                    >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-3.5 top-2.5 text-slate-400"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </div>

               <!-- Status Tabs -->
               <div class="flex items-center gap-1 overflow-x-auto max-w-full p-1 order-1 md:order-2">
                   <button 
                        v-for="tab in tabs" 
                        :key="tab.value"
                        @click="currentTab = tab.value"
                        class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 whitespace-nowrap"
                        :class="currentTab === tab.value ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'"
                   >
                       {{ tab.label }}
                   </button>
               </div>
           </div>
       </div>

       <!-- Content Area -->
       <div v-if="!metaLoading && meta">
           
           <!-- List Header (Columns) -->
           <div class="grid gap-4 px-6 py-3 mb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider" :style="{ gridTemplateColumns: gridTemplate }">
                <div class="pl-2">Kayıt</div>
                <div v-for="col in displayColumns" :key="col.key" :class="col.align === 'right' ? 'text-right' : 'text-left'">
                    {{ col.label }}
                </div>
                <div class="text-right pr-2">Durum</div>
           </div>

           <!-- Floating Rows -->
           <div class="space-y-3">
               <div 
                    v-for="row in resources.list.data" 
                    :key="row.name"
                    @click="$router.push(`/auto/${doctype.toLowerCase()}/${row.name}`)"
                    class="group relative bg-white rounded-xl p-4 border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-blue-900/5 hover:-translate-y-0.5 hover:border-blue-500/30 transition-all duration-300 cursor-pointer"
               >
                   <div class="grid gap-4 items-center" :style="{ gridTemplateColumns: gridTemplate }">
                       
                       <!-- Main Column (Avatar + Title + ID) -->
                       <div class="flex items-center gap-4 min-w-0">
                           <Avatar 
                                :label="row[titleField] || row.name" 
                                :image="imageField ? row[imageField] : null" 
                                size="lg" 
                                class="shadow-sm ring-2 ring-white"
                           />
                           <div class="flex-1 min-w-0">
                               <h3 class="text-base font-bold text-slate-900 truncate group-hover:text-blue-600 transition-colors">
                                   {{ row[titleField] || row.name }}
                               </h3>
                               <p class="text-xs font-mono text-slate-400 mt-0.5 flex items-center gap-1.5">
                                   <span class="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                                   {{ row.name }}
                               </p>
                           </div>
                       </div>

                       <!-- Other Columns -->
                       <div 
                            v-for="col in displayColumns" 
                            :key="col.key"
                            class="text-sm font-medium text-slate-600 truncate"
                            :class="col.align === 'right' ? 'text-right' : 'text-left'"
                       >
                            <span v-if="col.type === 'Currency'">{{ formatCurrency(row[col.key]) }}</span>
                            <span v-else-if="col.type === 'Float' || col.type === 'Int'">{{ formatDecimal(row[col.key]) }}</span>
                            <span v-else>{{ row[col.key] }}</span>
                       </div>

                       <!-- Status / Actions -->
                       <div class="flex items-center justify-end gap-3">
                            <!-- Status Badge -->
                            <Badge v-if="statusFields.length > 0" :variant="getStatusVariant(row[statusFields[0]])">
                                {{ row[statusFields[0]] }}
                            </Badge>
                            <div v-else class="text-xs text-slate-400 italic">No Status</div>

                            <!-- Hover Arrow -->
                             <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all text-blue-600 -mr-2">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                             </div>
                       </div>
                   </div>
               </div>

               <!-- Empty State -->
               <div v-if="!resources.list.loading && (!resources.list.data || resources.list.data.length === 0)" class="py-20 text-center">
                    <div class="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner">
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-300"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                    </div>
                    <h3 class="text-lg font-bold text-slate-900 mb-2">Kayıt Bulunamadı</h3>
                    <p class="text-slate-500 max-w-md mx-auto mb-6">Aradığınız kriterlere uygun kayıt bulunamadı veya henüz hiç kayıt eklenmemiş.</p>
                    <Button variant="solid" theme="white" icon-left="Plus" @click="navigateToNew">İlk Kaydı Ekle</Button>
               </div>
           </div>

           <!-- Loading State -->
            <div v-if="resources.list.loading" class="space-y-3 mt-6">
                <div v-for="i in 5" :key="i" class="h-20 bg-white rounded-xl border border-slate-100 animate-pulse"></div>
            </div>

       </div>

       <!-- Full Page Loading -->
       <div v-else-if="metaLoading" class="flex justify-center py-40">
           <div class="flex flex-col items-center gap-4">
                <div class="animate-spin h-10 w-10 border-3 border-blue-600 border-t-transparent rounded-full shadow-lg shadow-blue-500/30"></div>
                <div class="text-slate-400 font-medium animate-pulse">Yükleniyor...</div>
           </div>
       </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { createResource, frappeRequest } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import Button from '@/components/Button.vue'
import Badge from '@/components/Badge.vue'
import Avatar from '@/components/Avatar.vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true
  }
})

const router = useRouter()
const route = useRoute()
const meta = ref(null)
const metaLoading = ref(true)
const searchQuery = ref('')
const currentTab = ref('All')
let searchTimeout = null

// Formats
const doctypeNameTitleCase = computed(() => {
  return props.doctype
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
})

// Fields
const titleField = computed(() => meta.value?.title_field || null)
const imageField = computed(() => meta.value?.image_field || null)

// Status
const statusFields = computed(() => {
    if (!meta.value) return []
    return meta.value.fields
        .filter(f => f.in_list_view && ['status', 'workflow_state', 'docstatus', 'durum'].includes(f.fieldname))
        .map(f => f.fieldname)
})

// Columns for Display (Excluding Title/Image/Status as they are handled specifically)
const displayColumns = computed(() => {
    if (!meta.value) return []
    return meta.value.fields
        .filter(f => {
            if (!f.in_list_view) return false
            if (f.fieldname === titleField.value) return false // Main col
            if (f.fieldname === imageField.value) return false // Main col
            if (statusFields.value.includes(f.fieldname)) return false // Status col
            return true
        })
        .map(f => ({
            label: f.label,
            key: f.fieldname,
            type: f.fieldtype,
            align: ['Int', 'Float', 'Currency'].includes(f.fieldtype) ? 'right' : 'left'
        }))
})

// Dynamic Grid Template
const gridTemplate = computed(() => {
    // 1 Fraction for Main Info (Avatar+Title)
    // 1 Fraction for Status/Actions
    // Remaining fractions shared among displayColumns
    const colCount = displayColumns.value.length
    if (colCount === 0) return '1fr 150px'
    // Limit columns to avoid breaking layout? 
    // Let's say: Main(2fr) ...Columns(1fr each)... Status(150px)
    return `2fr ${'1fr '.repeat(colCount)} 150px`
})

// Tabs logic
const tabs = computed(() => {
    const base = [{ label: 'Tümü', value: 'All' }]
    
    // Attempt to extract options from status field if exists
    if (statusFields.value.length > 0 && meta.value) {
        const statusField = meta.value.fields.find(f => f.fieldname === statusFields.value[0])
        if (statusField && statusField.options) {
            const opts = statusField.options.split('\n').filter(o => o)
            opts.forEach(o => base.push({ label: o, value: o }))
        }
    }
    return base
})

const fieldNames = computed(() => {
  if (!meta.value) return ['name']
  const inputFields = meta.value.fields.filter(f => f.in_list_view).map(f => f.fieldname)
  
  if (titleField.value && !inputFields.includes(titleField.value)) inputFields.push(titleField.value)
  if (imageField.value && !inputFields.includes(imageField.value)) inputFields.push(imageField.value)
  // Ensure status fields are fetched
  statusFields.value.forEach(s => {
      if (!inputFields.includes(s)) inputFields.push(s)
  })
  
  return ['name', ...inputFields]
})

const resources = {
  list: createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: doctypeNameTitleCase.value,
      fields: fieldNames.value,
      limit_page_length: 50,
      order_by: 'creation desc'
    },
    auto: false
  })
}

function handleSearch() {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        reloadList()
    }, 300)
}

watch(currentTab, () => {
    reloadList()
})

// Watch route query changes (e.g. clicking different filtered links)
watch(() => route.query, () => {
    reloadList()
})

function reloadList() {
    const filters = []
    
    // Search
    if (searchQuery.value) {
        const searchField = titleField.value || 'name'
        filters.push([doctypeNameTitleCase.value, searchField, 'like', `%${searchQuery.value}%`])
    }
    
    // Text Filter logic
    if (currentTab.value !== 'All' && statusFields.value.length > 0) {
        filters.push([doctypeNameTitleCase.value, statusFields.value[0], '=', currentTab.value])
    }

    // URL Query Filters (e.g. ?filters={"account_type":"Bank"})
    if (route.query.filters) {
        try {
            const queryFilters = JSON.parse(route.query.filters)
            if (Array.isArray(queryFilters)) {
                queryFilters.forEach(f => filters.push(f))
            } else {
                Object.keys(queryFilters).forEach(key => {
                    filters.push([doctypeNameTitleCase.value, key, '=', queryFilters[key]])
                })
            }
        } catch (e) {
            console.error("Invalid URL filters:", e)
        }
    }
    
    resources.list.update({
        params: {
            doctype: doctypeNameTitleCase.value,
            fields: fieldNames.value,
            filters: filters,
            limit_page_length: 50,
            order_by: 'creation desc'
        }
    })
    resources.list.reload()
}

async function fetchMeta() {
  metaLoading.value = true
  try {
    const response = await frappeRequest({
      url: 'frappe.desk.form.load.getdoctype',
      params: {
        doctype: doctypeNameTitleCase.value,
        with_parent: 1
      }
    })
    meta.value = response.docs[0]
    reloadList()
  } catch (e) {
    console.error('Failed to fetch meta:', e)
  } finally {
    metaLoading.value = false
  }
}

function navigateToNew() {
  router.push(`/auto/${props.doctype.toLowerCase()}/new`)
}

function getStatusVariant(status) {
    if (!status) return 'gray'
    const s = status.toLowerCase()
    if (['active', 'enabled', 'success', 'paid', 'completed', 'submitted'].includes(s)) return 'green'
    if (['draft', 'pending', 'open'].includes(s)) return 'gray'
    if (['cancelled', 'rejected', 'error', 'overdue'].includes(s)) return 'red'
    if (['warning', 'processing', 'hold'].includes(s)) return 'orange'
    return 'gray'
}

function formatCurrency(value) {
  if(!value && value !== 0) return '-'
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(value);
}

function formatDecimal(value) {
  if(!value && value !== 0) return '-'
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
}

onMounted(() => {
  fetchMeta()
})

watch(() => props.doctype, () => {
    meta.value = null
    searchQuery.value = ''
    currentTab.value = 'All'
    fetchMeta()
})
</script>
