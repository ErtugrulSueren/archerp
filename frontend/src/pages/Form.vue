<template>
  <div class="form-root">
    <!-- Header -->
    <header class="form-header" :class="{ 'form-header--dirty': isDirty }">
      <div class="form-header__left">
        <!-- Breadcrumbs -->
        <div class="form-breadcrumbs">
            <span class="form-breadcrumbs__item form-breadcrumbs__item--link" @click="router.push('/')">
                <FeatherIcon name="home" class="form-breadcrumbs__icon" />
                <span class="form-breadcrumbs__text">Ana Sayfa</span>
            </span>
            <span class="form-breadcrumbs__sep">/</span>
            <span class="form-breadcrumbs__item form-breadcrumbs__item--link" @click="router.push(`/auto/${doctype}`)">{{ formatDoctype(doctype) }}</span>
            <span class="form-breadcrumbs__sep">/</span>
            <span class="form-breadcrumbs__item form-breadcrumbs__current">{{ isNew ? 'Yeni' : (title || id) }}</span>
        </div>

        <div class="form-header__title-row">
            <h1 class="form-header__title">{{ title }}</h1>
            <div v-if="isDirty" class="form-status form-status--dirty">
                <div class="form-status__dot"></div>
                Kaydedilmedi
            </div>
            <div v-if="!isNew && !isDirty" class="form-status form-status--saved">
                <div class="form-status__dot"></div>
                Kaydedildi
            </div>
        </div>
      </div>
      
      <div class="form-header__actions">
         <!-- Secondary Actions Menu -->
         <Popover v-if="!isNew" v-model:show="showActions">
            <template #target>
                <button 
                    class="form-header__more-btn"
                    @click="showActions = !showActions"
                >
                    <FeatherIcon name="more-horizontal" class="form-header__more-icon" />
                </button>
            </template>
            <template #body-main>
                <div class="form-actions-menu">
                    <button class="form-actions-menu__item" @click="printDoc">
                        <FeatherIcon name="printer" class="form-actions-menu__icon" />
                        Yazdır
                    </button>
                    <button class="form-actions-menu__item" @click="duplicateDoc">
                        <FeatherIcon name="copy" class="form-actions-menu__icon" />
                        Çoğalt
                    </button>
                    <div class="form-actions-menu__divider"></div>
                    <button class="form-actions-menu__item form-actions-menu__item--danger" @click="deleteDoc">
                        <FeatherIcon name="trash-2" class="form-actions-menu__icon" />
                        Sil
                    </button>

                     <!-- Custom Actions -->
                     <template v-if="visibleActions.length > 0">
                        <div class="form-actions-menu__divider"></div>
                        <div class="form-actions-menu__section-title">İşlemler</div>
                        <button 
                            v-for="action in visibleActions" 
                            :key="action.name"
                            class="form-actions-menu__item form-actions-menu__item--action" 
                            @click="handleCustomAction(action)"
                        >
                            <FeatherIcon name="zap" class="form-actions-menu__icon form-actions-menu__icon--action" />
                            {{ action.buton_etiketi }}
                        </button>
                     </template>
                </div>
            </template>
         </Popover>

        <AppButton 
          variant="solid" 
          theme="gray" 
          :loading="saving"
          :disabled="(!isDirty && !isNew) || isReadOnly"
          icon-left="save"
          class="form-save-btn"
          @click="save"
        >
          <span class="form-save-btn__text">{{ isNew ? 'Oluştur' : 'Kaydet' }}</span>
        </AppButton>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="form-loading">
        <div class="form-loading__inner">
            <div class="form-spinner"></div>
            <p class="form-spinner__text">Yükleniyor...</p>
        </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="form-error-wrap">
        <div class="form-error">
            <div class="form-error__icon-wrap">
                <FeatherIcon name="alert-triangle" class="form-error__icon"/>
            </div>
            <div class="form-error__body">
                <h4 class="form-error__title">Bir hata oluştu</h4>
                <p class="form-error__msg">{{ error }}</p>
                <div class="form-error__action">
                    <button class="form-error__retry" @click="reload">Sayfayı Yenile</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Form Content Wrapper -->
    <div v-else class="form-body">
        
        <!-- Main Form Area -->
        <div class="form-main">
            <div class="form-main__inner">
                
                <!-- Tabs Implementation -->
                <div v-if="layout.length > 0">
                    <!-- Tab Bar -->
                    <div v-if="layout.length > 1" class="form-tabs">
                        <div class="form-tabs__inner">
                            <button 
                                v-for="(tab, index) in layout" 
                                :key="index"
                                @click="activeTab = index"
                                class="form-tabs__btn"
                                :class="activeTab === index ? 'form-tabs__btn--active' : ''"
                            >
                                {{ tab.label || 'Detaylar' }}
                            </button>
                        </div>
                    </div>

                    <!-- Tab Content -->
                    <transition name="fade" mode="out-in">
                        <div :key="activeTab" class="form-tab-content">
                            <div class="form-sections">
                                <!-- Sections -->
                                <template v-for="(section, sIndex) in layout[activeTab].sections" :key="sIndex">
                                    <div 
                                        v-if="section.columns.length > 0"
                                        class="form-section"
                                    >
                                        <!-- Section Header -->
                                        <div 
                                            v-if="section.label" 
                                            class="form-section__header"
                                            @click="section.isCollapsed = !section.isCollapsed"
                                        >
                                            <h3 class="form-section__title">
                                                <div class="form-section__bar"></div>
                                                {{ section.label }}
                                            </h3>
                                            <div class="form-section__line"></div>
                                            <div v-if="section.collapsible" class="form-section__toggle">
                                                <FeatherIcon :name="section.isCollapsed ? 'chevron-right' : 'chevron-down'" class="form-section__toggle-icon" />
                                            </div>
                                        </div>

                                        <!-- Section Body (Columns) -->
                                        <div v-show="!section.isCollapsed">
                                            <div class="form-columns" :style="{ '--col-count': section.columns.length }">
                                                <!-- Columns -->
                                                <template v-for="(col, cIndex) in section.columns" :key="cIndex">
                                                    <div 
                                                        v-if="col.fields.length > 0" 
                                                        class="form-card"
                                                    >
                                                        <!-- Fields -->
                                                        <template v-for="field in col.fields" :key="field.fieldname">
                                                            <div v-if="!field.hidden" class="form-card__field">
                                                                <FormControl 
                                                                    :field="field"
                                                                    v-model="formData[field.fieldname]"
                                                                    :doc="formData"
                                                                    :disabled="isReadOnly"
                                                                />
                                                            </div>
                                                        </template>
                                                    </div>
                                                </template>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </transition>
                </div>
            </div>
        </div>

        <!-- Activity Sidebar (Right Panel) -->
        <ActivitySidebar 
            v-if="!isNew" 
            :doctype="doctype"
            :docname="id"
            class="form-activity"
        />

    </div>

    <!-- Delete Confirmation Dialog -->
    <Dialog
      v-model="showDeleteDialog"
      :options="{
        title: 'Kaydı Sil',
        message: 'Bu kaydı kalıcı olarak silmek istediğinize emin misiniz? Bu işlem geri alınamaz.',
        size: 'sm',
        actions: [
          {
            label: 'Sil',
            variant: 'solid',
            theme: 'red',
            loading: loading,
            onClick: confirmDelete
          }
        ]
      }"
    />
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { call, Badge, FeatherIcon, Popover, Dialog } from 'frappe-ui'
import FormControl from '../components/FormControl.vue'
import AppButton from '../components/AppButton.vue'
import ActivitySidebar from '../components/ActivitySidebar.vue'

const props = defineProps({
  doctype: { type: String, required: true },
  id: { type: String, default: null }
})

const router = useRouter()
const route = useRoute()

// State
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const meta = ref(null)
const formData = ref({})
const layout = ref([]) 
const activeTab = ref(0)
const initialData = ref(null)
const showActions = ref(false)
const fetchMap = ref({}) 
const childFetchMap = ref({}) // map[tableField][childLinkField] = [{target, source, linkOptions}] 
const isReadOnly = ref(false) // fieldname -> [{ target, source }]
const customActions = ref([])

const isNew = computed(() => !props.id || props.id === 'new')
const title = computed(() => {
    if (isNew.value) return `Yeni ${formatDoctype(props.doctype)}`
    return formData.value.name || props.id || props.doctype
})

const isDirty = computed(() => {
    if (!initialData.value) return false
    // Simple check - in production consider something like 'lodash.isequal'
    return JSON.stringify(formData.value) !== JSON.stringify(initialData.value)
})

// Realtime Calculation Logic
let debounceTimer = null
watch(() => [
    // Watch specific fields that affect totals
    formData.value.kalemler,
    formData.value.vergi_dahil_mi,
    formData.value.ek_iskonto_tutari,
    formData.value.vergi_orani // If item level changes are deep watched via 'kalemler'
], (newVal, oldVal) => {
    if (!formData.value || loading.value) return
    
    // Simple debounce
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(async () => {
        // Only if we have items
        if (!formData.value.kalemler || formData.value.kalemler.length === 0) return

        try {
            // Call the generic controller method
            const updatedDoc = await call('archerp.controllers.transaction_controller.calculate_doc', {
                doc: formData.value
            })
            
            // Merge results back to formData (preserve other fields)
            // We mainly want to update totals and item calculations
            if (updatedDoc) {
                formData.value.ara_toplam = updatedDoc.ara_toplam
                formData.value.vergi_toplami = updatedDoc.vergi_toplami
                formData.value.genel_toplam = updatedDoc.genel_toplam
                
                // Update item calculations (amounts)
                if (updatedDoc.kalemler && updatedDoc.kalemler.length === formData.value.kalemler.length) {
                    updatedDoc.kalemler.forEach((uItem, idx) => {
                        const originalItem = formData.value.kalemler[idx]
                        if (originalItem) {
                             originalItem.tutar = uItem.tutar
                             // Can also update unit_prices if backend recalculates them
                        }
                    })
                }
            }
        } catch (e) {
            console.warn('Calculation failed', e)
        }
    }, 600) // 600ms debounce
}, { deep: true })

// Helpers
function formatDoctype(name) {
    if (!name) return ''
    return name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

// Action Fetcher
async function fetchCustomActions() {
    try {
        const res = await call('frappe.client.get_list', {
            doctype: 'Arch Action',
            filters: {
                ilgili_belge: props.doctype,
                aktif: 1
            },
            fields: ['buton_etiketi', 'aksiyon_tipi', 'metot_veya_rota', 'kosul', 'name']
        })
        customActions.value = res || []
    } catch (e) {
        console.warn('Custom actions fetch failed', e)
    }
}

// Condition Evaluator
function evaluateCondition(condition, doc) {
    if (!condition) return true
    try {
        // Safe-ish eval using Function constructor
        // eslint-disable-next-line no-new-func
        return new Function('doc', `return ${condition}`)(doc)
    } catch (e) {
        console.warn('Condition eval error', e)
        return false
    }
}

// Filtered Actions
// We use a computed property so it reacts to formData changes
const visibleActions = computed(() => {
    if (!customActions.value.length) return []
    return customActions.value.filter(action => {
        return evaluateCondition(action.kosul, formData.value)
    })
})

async function handleCustomAction(action) {
    if (action.aksiyon_tipi === 'Route') {
        let route = action.metot_veya_rota
        if (formData.value.name) {
            route = route.replace(':name', formData.value.name)
            route = route.replace(':id', formData.value.name) 
        }
        
        if (route.startsWith('http')) {
            window.open(route, '_blank')
        } else {
            router.push(route)
        }
    } 
    else if (action.aksiyon_tipi === 'Server Method') {
        loading.value = true
        try {
            // Frappe mapper methods usually expect 'source_name' or 'name' 
            // We pass multiple variants to cover different conventions
            // We pass multiple variants to cover different conventions
            const res = await call(action.metot_veya_rota, {
                doc: formData.value,
                doctype: props.doctype,
                name: formData.value.name,
                source_name: formData.value.name, 
                docname: formData.value.name      
            })

            // RESPONSE HANDLING
            // If the method returns a dictionary that looks like a Document
            if (res && res.doctype && typeof res === 'object') {
                const targetDoctype = res.doctype
                
                if (res.name && !res.__islocal) {
                    // It's a saved document -> Go to it
                    router.push(`/auto/${targetDoctype}/${res.name}`)
                } 
                else {
                    // It's an UNSAVED (dirty) document (e.g. make_sales_order returns transient doc)
                    // We need to pass this data to the new form.
                    // Using sessionStorage as a temporary handover mechanism
                    sessionStorage.setItem('frappe_ui_mapped_doc', JSON.stringify(res))
                    router.push(`/auto/${targetDoctype}/new`)
                }
                return // Skip reload
            } else if (typeof res === 'string' && res.startsWith('/')) {
                // Returns a URL?
                router.push(res)
                return
            }

            // Default: just reload current
            await loadForm()
        } catch (e) {
            error.value = e.message || 'İşlem başarısız'
        } finally {
            loading.value = false
        }
    }
    
    showActions.value = false
}

// Layout Processor & Fetch Map Builder
function processMeta(doctypeMeta) {
    meta.value = doctypeMeta
    
    // Build Fetch Map
    const map = {}
    if (doctypeMeta.fields) {
        doctypeMeta.fields.forEach(f => {
            if (f.fetch_from && f.fetch_from.includes('.')) {
                // fetch_from format: "link_fieldname.source_fieldname"
                // Example: customer_name fetches from customer.customer_name
                // Trigger: customer
                // Target: customer_name
                // Source: customer_name
                const [triggerField, sourceField] = f.fetch_from.split('.')
                if (!map[triggerField]) map[triggerField] = []
                map[triggerField].push({
                    targetField: f.fieldname,
                    sourceField: sourceField
                })
            }
        })
    }
    fetchMap.value = map

    // Build Layout
    layout.value = processLayoutAlgorithm(doctypeMeta.fields || [])

    // Trigger Child Meta Fetch
    fetchChildMetas(doctypeMeta)
}

async function fetchChildMetas(parentMeta) {
    if (!parentMeta.fields) return
    
    // reset
    childFetchMap.value = {}

    // Identify Table fields
    const tableFields = parentMeta.fields.filter(f => f.fieldtype === 'Table' && f.options)
    
    for (const tableField of tableFields) {
        const childDoctype = tableField.options
        try {
             // Use standard desk call to ensure we get full meta including typical desk fields
             const res = await call('frappe.desk.form.load.getdoctype', { doctype: childDoctype })
             if (res && res.docs && res.docs.length > 0) {
                 const childMeta = res.docs[0]
                 
                 // Process fields for fetch_from
                 if (childMeta.fields) {
                     childMeta.fields.forEach(f => {
                          if (f.fetch_from && f.fetch_from.includes('.')) {
                               const [triggerField, sourceField] = f.fetch_from.split('.')
                               
                               if (!childFetchMap.value[tableField.fieldname]) {
                                   childFetchMap.value[tableField.fieldname] = {}
                               }
                               
                               const triggerFieldMeta = childMeta.fields.find(tf => tf.fieldname === triggerField)
                               const linkOptions = triggerFieldMeta ? triggerFieldMeta.options : null

                               if (!childFetchMap.value[tableField.fieldname][triggerField]) {
                                   childFetchMap.value[tableField.fieldname][triggerField] = []
                               }
                               
                               childFetchMap.value[tableField.fieldname][triggerField].push({
                                   targetField: f.fieldname,
                                   sourceField: sourceField,
                                   linkOptions: linkOptions
                               })
                          }
                     })
                 }
             }
        } catch (e) {
            console.warn(`Failed to fetch meta for child table ${childDoctype}`, e)
        }
    }
}

function processLayoutAlgorithm(fields) {
    const tabs = []
    let currentTab = null
    let currentSection = null
    let currentColumn = null

    const ensureTab = (label = 'Detaylar') => {
        if (!currentTab) {
            currentTab = { label, sections: [] }
            tabs.push(currentTab)
            currentSection = null
        }
    }

    const ensureSection = (label = null, collapsible = false) => {
        ensureTab()
        if (!currentSection) {
            currentSection = { label, collapsible: !!collapsible, isCollapsed: false, columns: [] }
            currentTab.sections.push(currentSection)
            currentColumn = null
        }
    }

    const ensureColumn = () => {
        ensureSection()
        if (!currentColumn) {
            currentColumn = { fields: [] }
            currentSection.columns.push(currentColumn)
        }
    }

    if (fields.length > 0 && fields[0].fieldtype !== 'Tab Break') ensureTab()

    fields.forEach(f => {
        if (f.fieldtype === 'Tab Break') {
            currentTab = null; currentSection = null; currentColumn = null;
            ensureTab(f.label)
        } 
        else if (f.fieldtype === 'Section Break') {
            if (!currentTab) ensureTab()
            currentSection = null; currentColumn = null;
            ensureSection(f.label, f.collapsible)
        }
        else if (f.fieldtype === 'Column Break') {
            if (!currentTab) ensureTab()
            if (!currentSection) ensureSection()
            currentColumn = null;
            ensureColumn()
        }
        else if (!['Section Break', 'Column Break', 'Tab Break'].includes(f.fieldtype)) {
            ensureColumn()
            currentColumn.fields.push(f)
        }
    })
    
    return tabs.map(tab => ({
        ...tab,
        sections: tab.sections.map(sec => ({
            ...sec,
            columns: sec.columns.filter(col => col.fields.length > 0)
        })).filter(sec => sec.columns.length > 0)
    })).filter(t => t.sections.length > 0)
}

function processDefaults(fields) {
    const defaults = {}
    if (!fields) return defaults
    fields.forEach(f => {
        if (f.default) {
            let val = f.default
            if (val === 'Today') val = new Date().toISOString().split('T')[0]
            else if (val === 'Now') {
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

async function loadForm() {
    loading.value = true
    error.value = null
    const doctypeName = formatDoctype(props.doctype)

    try {
        const metaRes = await call('frappe.desk.form.load.getdoctype', { doctype: doctypeName })
        if (!metaRes.docs || !metaRes.docs.length) throw new Error('Meta data bulunamadı')
        processMeta(metaRes.docs[0])

        if (!isNew.value) {
            // Get Doc and Permissions in parallel for better performance
            const [docRes, permRes] = await Promise.all([
                call('frappe.client.get', { doctype: doctypeName, name: props.id }),
                call('frappe.client.get_doc_permissions', { doctype: doctypeName, docname: props.id })
            ])
            
            formData.value = docRes
            initialData.value = JSON.parse(JSON.stringify(docRes))
            
            // Check write permission
            if (permRes && permRes.permissions && permRes.permissions.write === 0) {
                isReadOnly.value = true
            }
        } else {
             // New Doc
             // CHECK FOR MAPPED DOC HANDOVER
             const mappedDocStr = sessionStorage.getItem('frappe_ui_mapped_doc')
             if (mappedDocStr) {
                 try {
                     const mappedDoc = JSON.parse(mappedDocStr)
                     // Verify it matches current doctype request
                     if (mappedDoc.doctype === doctypeName) {
                         formData.value = mappedDoc
                         initialData.value = JSON.parse(mappedDocStr)
                         sessionStorage.removeItem('frappe_ui_mapped_doc') // Consume it
                         // Initialize snapshots
                         previousFormData.value = JSON.parse(JSON.stringify(formData.value))
                         return // Skip default processing
                     }
                 } catch (e) {
                     console.error('Failed to parse mapped doc', e)
                 }
                 sessionStorage.removeItem('frappe_ui_mapped_doc') // Clear stale
             }
             
             // Initialize Data
        const initData = { ...route.query }
        
        // 1. Static Defaults from DocType
        if (meta.value && meta.value.fields) {
            const defaults = processDefaults(meta.value.fields)
            Object.assign(initData, defaults)
        }

        // 2. User Permission Defaults (from Backend)
        try {
            // Fetch current user reliably
            const currentUser = await call('frappe.auth.get_logged_user')
            
            if (currentUser && currentUser !== 'Guest') {
                const userPerms = await call('frappe.client.get_list', {
                    doctype: 'User Permission',
                    filters: {
                        user: currentUser,
                        is_default: 1
                    },
                    fields: ['allow', 'for_value']
                })

                if (userPerms && userPerms.length) {
                    userPerms.forEach(perm => {
                        const targetField = meta.value.fields.find(f => 
                            f.fieldtype === 'Link' && 
                            f.options === perm.allow && 
                            !initData[f.fieldname]
                        )
                        
                        if (targetField) {
                            console.log(`[Form] Applying Default Permission: ${targetField.fieldname} = ${perm.for_value}`)
                            initData[targetField.fieldname] = perm.for_value
                        }
                    })
                }
            }
        } catch (e) {
             console.warn('Failed to load User Permission defaults:', e)
        }

        // Apply to formData
        formData.value = initData
        
        // Trigger initial fetch for fields that have persistent defaults (e.g. User Permissions)
        if (fetchMap.value) {
             await Promise.all(Object.keys(fetchMap.value).map(key => {
                 if (initData[key]) return applyFetchFrom(key, initData[key])
             }))
        }

        initialData.value = JSON.parse(JSON.stringify(formData.value))
        }
        
         // Initialize snapshot for watcher
        previousFormData.value = JSON.parse(JSON.stringify(formData.value))
        
    } catch (e) {
        error.value = e.message
        console.error(e)
    } finally {
        loading.value = false
        // Fetch custom actions after load
        fetchCustomActions()
    }
}

async function save() {
    saving.value = true
    error.value = null
    try {
        // Use desk savedocs for full verification and child table support
        const res = await call('frappe.desk.form.save.savedocs', { 
            doc: JSON.stringify(formData.value),
            action: 'Save'
        })
        
        const savedDoc = res.docs[0]
        formData.value = savedDoc
        initialData.value = JSON.parse(JSON.stringify(savedDoc))
        previousFormData.value = JSON.parse(JSON.stringify(savedDoc)) // Update snapshot
        
        if (isNew.value) {
             router.replace(`/auto/${props.doctype}/${savedDoc.name}`)
        }
        
    } catch(e) {
        // Parse server error messages if possible
        if (e.messages && e.messages.length > 0) {
             error.value = e.messages.join('\n')
        } else {
             error.value = e.message || 'Kayıt sırasında hata oluştu'
        }
        console.error(e)
    } finally {
        saving.value = false
    }
}

// Watchers for Fetch From

// Watchers for Fetch From
// Capture previous state snapshot to detect WHAT changed.
const previousFormData = ref({})

watch(formData, async (newVal) => {
    if (loading.value) {
        previousFormData.value = JSON.parse(JSON.stringify(newVal))
        return
    }

    const map = fetchMap.value
    // Watch for changes in main form fields
    for (const key of Object.keys(map)) {
        if (newVal[key] !== previousFormData.value[key]) {
             await applyFetchFrom(key, newVal[key])
        }
    }

    // Watch for changes in Child Tables
    if (childFetchMap.value && Object.keys(childFetchMap.value).length > 0) {
        for (const tableField of Object.keys(childFetchMap.value)) {
            const newRows = newVal[tableField] || []
            const oldRows = previousFormData.value[tableField] || []
            const rules = childFetchMap.value[tableField] 

            newRows.forEach(async (row, index) => {
                // If new row or existing row modified
                // Note: deeply checking rows is hard if they don't have IDs. 
                // But normally we edit existing rows. 
                // Simple index matching is risky if rows are reordered, but for now Standard Frappe Grid logic.
                const oldRow = oldRows[index] || {} 

                for (const triggerField of Object.keys(rules)) {
                    if (row[triggerField] !== oldRow[triggerField]) {
                        await applyChildFetch(row, triggerField, rules, tableField)
                    }
                }
            })
        }
    }
    // Update snapshot
    previousFormData.value = JSON.parse(JSON.stringify(newVal))
}, { deep: true })

async function applyFetchFrom(key, linkValue) {
    if (!linkValue) {
        fetchMap.value[key]?.forEach(m => formData.value[m.targetField] = null)
        return
    }

    try {
        const fieldMeta = meta.value.fields.find(f => f.fieldname === key)
        if (!fieldMeta || !fieldMeta.options) return

        // Using get instead of get_value to ensure we get all fields reliably
        const sourceRes = await call('frappe.client.get', {
            doctype: fieldMeta.options,
            name: linkValue
        })

        if (sourceRes) {
            fetchMap.value[key].forEach(m => {
                // Check strictly for undefined, as null/extra-falsey values are valid
                if (sourceRes[m.sourceField] !== undefined) {
                    const newVal = sourceRes[m.sourceField]
                    formData.value[m.targetField] = newVal
                }
            })
        }
    } catch (e) {
        console.warn(`[Form] Fetch failed for ${key}:`, e)
    }
}

async function applyChildFetch(row, triggerField, rules, tableField) {
    if (!rules[triggerField]) return

    const linkValue = row[triggerField]

    if (!linkValue) {
        rules[triggerField].forEach(r => {
             row[r.targetField] = null
             applyChildFetch(row, r.targetField, rules, tableField)
        })
        return
    }

    const fieldRuleList = rules[triggerField]
    const linkDoctype = fieldRuleList[0].linkOptions
    if (!linkDoctype) return

    try {
        const sourceFields = fieldRuleList.map(r => r.sourceField)
        
        const sourceRes = await call('frappe.client.get_value', {
            doctype: linkDoctype,
            fieldname: sourceFields,
            filters: { name: linkValue }
        })

        if (sourceRes) {
            for (const r of fieldRuleList) {
                if (sourceRes[r.sourceField] !== undefined) {
                    const newValue = sourceRes[r.sourceField]
                    const oldValue = row[r.targetField]
                    
                    row[r.targetField] = newValue
                    
                    if (newValue !== oldValue) {
                         await applyChildFetch(row, r.targetField, rules, tableField)
                    }
                }
            }
        }
    } catch (e) {
        console.warn(`Child table fetch failed for ${tableField}.${triggerField}`, e)
    }
}


// Actions
function printDoc() {
    // Open standard print view
    const printUrl = `/printview?doctype=${props.doctype}&name=${props.id}` // Frappe default
    // Or just window.print() if we had a print view. 
    // For now simple alert
    alert('Yazdırma servisi henüz aktif değil.')
}

function duplicateDoc() {
    // Create new with current data
    const newDoc = { ...formData.value }
    delete newDoc.name
    delete newDoc.creation
    delete newDoc.modified
    delete newDoc.owner
    delete newDoc.docstatus
    
    // We can't just push router, we need to pass data.
    // Frappe standard: Route to new, and maybe pass 'copy_from' param?
    // Simplified: Just redirect to new and we lose data unless we use store.
    // Let's keep it simple: "Not implemented" for now or use query params?
    alert('Çoğaltma özelliği bir sonraki güncellemede.')
}

const showDeleteDialog = ref(false)

function deleteDoc() {
    showDeleteDialog.value = true
}

async function confirmDelete() {
    try {
        await call('frappe.client.delete', { doctype: props.doctype, name: props.id })
        showDeleteDialog.value = false
        router.push(`/auto/${props.doctype}`)
    } catch (e) {
        error.value = e.message
        showDeleteDialog.value = false
    }
}


function reload() {
    loadForm()
}

watch(() => [props.doctype, props.id], loadForm, { immediate: true })

</script>

<style scoped>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ROOT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-root {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow: hidden;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HEADER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #ffffff;
  border-bottom: 1px solid #f1f5f9;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: all 300ms;
}

.form-header--dirty {
  border-bottom-color: #fed7aa;
  background: #fffbf5;
  box-shadow: 0 2px 8px rgba(251, 146, 60, 0.08);
}

.form-header__left {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.form-header__title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-header__title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.3px;
  margin: 0;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.form-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.form-header__more-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 1px solid transparent;
  background: none;
  color: #64748b;
  cursor: pointer;
  transition: all 200ms;
}

.form-header__more-btn:hover {
  color: #0f172a;
  background: #f8fafc;
  border-color: #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.form-header__more-icon {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .form-header {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .form-header__title {
    font-size: 17px;
  }

  .form-header__title-row {
    gap: 8px;
  }

  .form-header__more-btn {
    width: 36px;
    height: 36px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BREADCRUMBS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-breadcrumbs {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
}

.form-breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.form-breadcrumbs__item--link {
  cursor: pointer;
  transition: color 200ms;
}

.form-breadcrumbs__item--link:hover {
  color: #3b82f6;
}

.form-breadcrumbs__icon {
  width: 12px;
  height: 12px;
}

.form-breadcrumbs__sep {
  color: #cbd5e1;
}

.form-breadcrumbs__current {
  color: #475569;
  font-weight: 600;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .form-breadcrumbs {
    font-size: 11px;
    gap: 4px;
  }

  .form-breadcrumbs__text {
    display: none;
  }

  .form-breadcrumbs__current {
    max-width: 120px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STATUS BADGE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.form-status__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.form-status--dirty {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #ea580c;
}

.form-status--dirty .form-status__dot {
  background: #f97316;
  animation: pulse-dot 2s infinite;
}

.form-status--saved {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.form-status--saved .form-status__dot {
  background: #22c55e;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 768px) {
  .form-status {
    font-size: 9px;
    padding: 2px 8px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SAVE BUTTON
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-save-btn {
  height: 40px !important;
  padding-left: 20px !important;
  padding-right: 20px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 300ms;
}

.form-save-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .form-save-btn {
    height: 36px !important;
    padding-left: 14px !important;
    padding-right: 14px !important;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ACTIONS MENU
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-actions-menu {
  padding: 8px;
  width: 200px;
  display: flex;
  flex-direction: column;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.form-actions-menu__item {
  width: 100%;
  text-align: left;
  padding: 10px 12px;
  font-size: 13px;
  color: #334155;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 150ms;
}

.form-actions-menu__item:hover {
  background: #f8fafc;
}

.form-actions-menu__item--danger {
  color: #dc2626;
}

.form-actions-menu__item--danger:hover {
  background: #fef2f2;
}

.form-actions-menu__item--action {
  font-weight: 500;
}

.form-actions-menu__item--action:hover {
  background: linear-gradient(to right, #eef2ff, #ffffff);
  color: #4338ca;
}

.form-actions-menu__icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  flex-shrink: 0;
}

.form-actions-menu__item:hover .form-actions-menu__icon {
  color: #64748b;
}

.form-actions-menu__item--danger .form-actions-menu__icon {
  color: #ef4444;
}

.form-actions-menu__icon--action {
  color: #f59e0b;
}

.form-actions-menu__item--action:hover .form-actions-menu__icon--action {
  color: #d97706;
}

.form-actions-menu__divider {
  height: 1px;
  background: #f1f5f9;
  margin: 4px 8px;
}

.form-actions-menu__section-title {
  padding: 6px 12px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .form-actions-menu {
    width: 220px;
  }

  .form-actions-menu__item {
    padding: 12px;
    font-size: 14px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LOADING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-loading__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.form-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f1f5f9;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.form-spinner__text {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
  margin: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ERROR
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-error-wrap {
  padding: 32px;
  display: flex;
  justify-content: center;
}

.form-error {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  max-width: 500px;
  width: 100%;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.08);
}

.form-error__icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #fee2e2;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.form-error__icon {
  width: 22px;
  height: 22px;
  color: #dc2626;
}

.form-error__body {
  flex: 1;
}

.form-error__title {
  font-size: 16px;
  font-weight: 700;
  color: #991b1b;
  margin: 0 0 4px;
}

.form-error__msg {
  font-size: 13px;
  color: #b91c1c;
  line-height: 1.5;
  margin: 0;
}

.form-error__action {
  margin-top: 12px;
}

.form-error__retry {
  font-size: 13px;
  font-weight: 600;
  color: #dc2626;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.form-error__retry:hover {
  text-decoration: underline;
  color: #991b1b;
}

@media (max-width: 768px) {
  .form-error-wrap {
    padding: 16px;
  }

  .form-error {
    padding: 16px;
    gap: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FORM BODY (Main + Activity)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
  z-index: 0;
}

.form-main {
  flex: 1;
  overflow: auto;
  padding: 24px 32px;
}

.form-main__inner {
  max-width: 1100px;
  margin: 0 auto;
  padding-bottom: 80px;
}

.form-activity {
  display: none;
}

@media (min-width: 1024px) {
  .form-activity {
    display: flex;
  }
}

@media (max-width: 768px) {
  .form-main {
    padding: 12px;
  }

  .form-main__inner {
    padding-bottom: 40px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TABS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-tabs {
  margin-bottom: 24px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.form-tabs::-webkit-scrollbar {
  display: none;
}

.form-tabs__inner {
  display: flex;
  gap: 4px;
  padding: 5px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  width: max-content;
  min-width: 100%;
}

.form-tabs__btn {
  position: relative;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  background: none;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 200ms;
}

.form-tabs__btn:hover {
  color: #0f172a;
  background: #f8fafc;
}

.form-tabs__btn--active {
  color: #3b82f6;
  background: #eff6ff;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.1);
}

@media (max-width: 768px) {
  .form-tabs {
    margin-bottom: 16px;
    margin-left: -12px;
    margin-right: -12px;
    padding: 0 12px;
  }

  .form-tabs__inner {
    min-width: unset;
  }

  .form-tabs__btn {
    padding: 9px 16px;
    font-size: 13px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TAB CONTENT + SECTIONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-tab-content {
  animation: fadeIn 200ms ease-out;
}

.form-sections {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-section {
  /* Just a wrapper */
}

.form-section__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  user-select: none;
  cursor: pointer;
}

.form-section__title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.form-section__bar {
  width: 3px;
  height: 20px;
  border-radius: 2px;
  background: #3b82f6;
  flex-shrink: 0;
}

.form-section__line {
  flex: 1;
  height: 1px;
  background: #e2e8f0;
  transition: background 200ms;
}

.form-section__header:hover .form-section__line {
  background: #cbd5e1;
}

.form-section__toggle {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #94a3b8;
  transition: all 200ms;
}

.form-section__header:hover .form-section__toggle {
  color: #3b82f6;
  border-color: #bfdbfe;
}

.form-section__toggle-icon {
  width: 14px;
  height: 14px;
}

@media (max-width: 768px) {
  .form-sections {
    gap: 20px;
  }

  .form-section__title {
    font-size: 14px;
  }

  .form-section__header {
    gap: 8px;
    margin-bottom: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   COLUMNS GRID
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-columns {
  display: grid;
  gap: 20px;
  align-items: start;
  grid-template-columns: repeat(var(--col-count, 1), minmax(0, 1fr));
}

@media (max-width: 768px) {
  .form-columns {
    grid-template-columns: 1fr !important;
    gap: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FORM CARD (Column Wrapper)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.form-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: all 250ms;
}

.form-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #cbd5e1;
}

.form-card__field {
  /* spacing handled by gap */
}

@media (max-width: 768px) {
  .form-card {
    padding: 16px;
    gap: 14px;
    border-radius: 12px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ANIMATIONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 150ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
