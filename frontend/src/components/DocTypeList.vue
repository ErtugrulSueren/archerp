<template>
  <div class="dtl-root">
    <!-- Header -->
    <header class="dtl-header">
      <div class="dtl-header__left">
        <h1 class="dtl-header__title">{{ doctype }}</h1>
        <Badge v-if="listResource.data" theme="gray" size="sm" class="dtl-header__badge">{{ listResource.data.length }} Kayıt</Badge>
      </div>
      
      <div class="dtl-header__actions">
        <AppButton 
          variant="subtle" 
          theme="gray" 
          size="md" 
          icon-left="refresh-cw" 
          @click="listResource.reload"
          :loading="listResource.loading"
          class="dtl-header__btn-refresh"
        >
          <span class="dtl-header__btn-text">Yenile</span>
        </AppButton>
        <AppButton 
          variant="solid" 
          size="md" 
          icon-left="plus" 
          @click="router.push(`/auto/${doctype}/new`)"
        >
          <span class="dtl-header__btn-text">Yeni {{ doctype }}</span>
          <span class="dtl-header__btn-text--mobile">Yeni</span>
        </AppButton>
      </div>
    </header>

    <!-- Filter Bar -->
    <div class="dtl-filters">
        <Popover v-model:show="showFilterPopover">
            <template #target>
                <AppButton 
                    variant="subtle" 
                    theme="gray"
                    size="sm" 
                    icon-left="filter"
                    :active="showFilterPopover"
                    @click="showFilterPopover = !showFilterPopover"
                >
                    Filtrele
                </AppButton>
            </template>
            <template #body-main>
                <div class="dtl-filter-popup">
                    <div class="dtl-filter-popup__header">
                         <span class="dtl-filter-popup__title">Filtre Oluştur</span>
                    </div>

                    <div class="dtl-filter-popup__field">
                        <label class="dtl-filter-popup__label">Alan</label>
                        <select 
                            v-model="newFilter.field"
                            class="dtl-filter-popup__select"
                        >
                            <option value="" disabled selected>Seçiniz...</option>
                            <option v-for="opt in filterableFieldOptions" :key="opt.value" :value="opt.value">
                                {{ opt.label }}
                            </option>
                        </select>
                    </div>
                    
                    <div class="dtl-filter-popup__field" v-if="newFilter.field">
                        <label class="dtl-filter-popup__label">Koşul</label>
                        <select 
                            v-model="newFilter.operator"
                            class="dtl-filter-popup__select"
                        >
                            <option v-for="op in operators" :key="op.value" :value="op.value">
                                {{ op.label }}
                            </option>
                        </select>
                    </div>

                    <div class="dtl-filter-popup__field" v-if="newFilter.field">
                        <label class="dtl-filter-popup__label">Değer</label>
                        <FormControl 
                            :field="{ ...selectedFieldMeta, label: '', reqd: 0 }" 
                            v-model="newFilter.value"
                            :doc="{}"
                            size="sm"
                        />
                    </div>

                    <div class="dtl-filter-popup__actions">
                         <AppButton 
                            variant="subtle"
                            class="dtl-filter-popup__btn"
                            size="sm"
                            @click="showFilterPopover = false"
                        >
                            İptal
                        </AppButton>
                        <AppButton 
                            variant="solid" 
                            class="dtl-filter-popup__btn" 
                            size="sm"
                            :disabled="!newFilter.field || newFilter.value === null || newFilter.value === ''"
                            @click="addFilter"
                        >
                            Uygula
                        </AppButton>
                    </div>
                </div>
            </template>
        </Popover>

        <div class="dtl-filters__divider" v-if="activeFilters.length > 0"></div>

        <!-- Active Filters -->
        <div class="dtl-filters__tags">
          <div v-for="(filter, idx) in activeFilters" :key="idx" class="dtl-filter-tag">
              <span class="dtl-filter-tag__text">{{ filter.display }}</span>
              <button class="dtl-filter-tag__remove" @click="removeFilter(idx)">
                  <FeatherIcon name="x" class="dtl-filter-tag__icon" />
              </button>
          </div>
        </div>
        
        <AppButton 
            v-if="activeFilters.length > 0" 
            variant="ghost" 
            size="sm" 
            class="dtl-filters__clear"
            @click="clearFilters"
        >
            Temizle
        </AppButton>
    </div>

    <!-- Content -->
    <div class="dtl-content">
      
      <!-- Loading State -->
      <div v-if="loadingMeta || listResource.loading" class="dtl-loading">
        <div v-for="i in 5" :key="i" class="dtl-loading__skeleton"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="dtl-error">
        <FeatherIcon name="alert-circle" class="dtl-error__icon" />
        {{ error }}
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!listResource.data || listResource.data.length === 0" class="dtl-empty">
          <div class="dtl-empty__icon-wrap">
              <FeatherIcon name="inbox" class="dtl-empty__icon" />
          </div>
          <h3 class="dtl-empty__title">Kayıt Bulunamadı</h3>
          <p class="dtl-empty__desc">Bu liste için henüz bir kayıt oluşturulmamış. Yeni bir kayıt ekleyerek başlayabilirsiniz.</p>
          <AppButton 
              variant="outline" 
              class="dtl-empty__btn"
              icon-left="plus" 
              @click="router.push(`/auto/${doctype}/new`)"
          >
              Yeni Oluştur
          </AppButton>
      </div>

      <!-- Data View -->
      <div v-else class="dtl-data">

        <!-- Desktop Table -->
        <div class="dtl-table-wrap">
          <table class="dtl-table">
              <thead>
                  <tr class="dtl-table__head-row">
                      <th class="dtl-table__th dtl-table__th--checkbox">
                          <input type="checkbox" class="dtl-checkbox" />
                      </th>
                      <th 
                          v-for="col in columns" 
                          :key="col.key" 
                          class="dtl-table__th"
                          :class="col.align === 'right' ? 'dtl-table__th--right' : ''"
                          :style="{ width: col.width ? col.width + 'px' : 'auto' }"
                      >
                          {{ col.label }}
                      </th>
                  </tr>
              </thead>
              <tbody>
                  <tr 
                      v-for="row in listResource.data" 
                      :key="row.name" 
                      class="dtl-table__row"
                      @click="router.push(`/auto/${doctype}/${row.name}`)"
                  >
                      <td class="dtl-table__td dtl-table__td--checkbox" @click.stop>
                          <input type="checkbox" class="dtl-checkbox" />
                      </td>
                      <td 
                          v-for="col in columns" 
                          :key="col.key" 
                          class="dtl-table__td"
                          :class="col.align === 'right' ? 'dtl-table__td--right' : ''"
                      >
                          <div v-if="col.key === 'name'" class="dtl-table__name-cell">
                              {{ row[col.key] }}
                          </div>
                          <div v-else-if="col.key === 'status'">
                              <Badge :theme="getStatusTheme(row[col.key])" size="sm" variant="subtle">
                                  {{ row[col.key] }}
                              </Badge>
                          </div>
                          <div v-else class="dtl-table__cell-text">
                              {{ row[col.key] }}
                          </div>
                      </td>
                  </tr>
              </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="dtl-cards">
          <div 
            v-for="row in listResource.data" 
            :key="row.name" 
            class="dtl-card"
            @click="router.push(`/auto/${doctype}/${row.name}`)"
          >
            <div class="dtl-card__header">
              <span class="dtl-card__id">{{ row.name }}</span>
              <Badge 
                v-if="row.status" 
                :theme="getStatusTheme(row.status)" 
                size="sm" 
                variant="subtle"
              >
                {{ row.status }}
              </Badge>
            </div>
            <div class="dtl-card__body">
              <div 
                v-for="col in mobileColumns" 
                :key="col.key" 
                class="dtl-card__field"
              >
                <span class="dtl-card__field-label">{{ col.label }}</span>
                <span class="dtl-card__field-value">{{ row[col.key] || '—' }}</span>
              </div>
            </div>
            <div class="dtl-card__footer">
              <span class="dtl-card__modified">{{ row.modified }}</span>
              <FeatherIcon name="chevron-right" class="dtl-card__arrow" />
            </div>
          </div>
        </div>

        <!-- Pagination Footer -->
        <div class="dtl-pagination">
            <p class="dtl-pagination__info">
                Toplam <span class="dtl-pagination__count">{{ listResource.data.length }}</span> kayıt gösteriliyor
            </p>
            <div class="dtl-pagination__btns">
                <AppButton size="sm" variant="outline" icon-left="chevron-left" disabled>Önceki</AppButton>
                <AppButton size="sm" variant="outline" icon-right="chevron-right" disabled>Sonraki</AppButton>
            </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { createListResource, call, Badge, FeatherIcon, Popover } from 'frappe-ui'
import AppButton from './AppButton.vue'
import { useRouter, useRoute } from 'vue-router'
import FormControl from './FormControl.vue'
import { useSessionDefaults } from '@/composables/useSessionDefaults'

const { defaults, getSessionDefaultFields, loadDefaults: loadSessionDefaults, isLoaded: sessionDefaultsLoaded } = useSessionDefaults()

// Filter State
const showFilterPopover = ref(false)
const activeFilters = ref([])
const newFilter = ref({
    field: null,
    operator: '=',
    value: null
})

const operators = [
    { label: 'Eşittir', value: '=' },
    { label: 'Eşit Değil', value: '!=' },
    { label: 'İçerir', value: 'like' },
    { label: 'Büyüktür', value: '>' },
    { label: 'Küçüktür', value: '<' },
    { label: 'Büyük Eşit', value: '>=' },
    { label: 'Küçük Eşit', value: '<=' },
]

const filterableFieldOptions = computed(() => {
    if (!meta.value || !meta.value.fields) return []
    return meta.value.fields
        .filter(f => !['Section Break', 'Column Break', 'Tab Break'].includes(f.fieldtype) && !f.hidden)
        .map(f => ({
            label: f.label,
            value: f.fieldname,
            fieldtype: f.fieldtype
        }))
})

const selectedFieldMeta = computed(() => {
    if (!newFilter.value.field || !meta.value) return null
    return meta.value.fields.find(f => f.fieldname === newFilter.value.field)
})

function addFilter() {
    if (!newFilter.value.field || newFilter.value.value === null) return
    
    const fieldLabel = filterableFieldOptions.value.find(f => f.value === newFilter.value.field)?.label || newFilter.value.field
    const operatorLabel = operators.find(o => o.value === newFilter.value.operator)?.label
    
    activeFilters.value.push({
        field: newFilter.value.field,
        operator: newFilter.value.operator,
        value: newFilter.value.value,
        display: `${fieldLabel} ${operatorLabel} ${newFilter.value.value}`
    })
    
    newFilter.value = { field: null, operator: '=', value: null }
    showFilterPopover.value = false
    refreshList()
}

function removeFilter(index) {
    activeFilters.value.splice(index, 1)
    refreshList()
}

function clearFilters() {
    activeFilters.value = activeFilters.value.filter(f => f.isSessionDefault)
    refreshList()
}

function applySessionDefaultFilters() {
    if (!meta.value?.fields) return
    
    Object.entries(getSessionDefaultFields()).forEach(([key, config]) => {
        const value = defaults[key]
        if (!value) return
        
        const fieldMeta = meta.value.fields.find(f => f.fieldname === config.fieldname)
        if (!fieldMeta) return
        
        if (activeFilters.value.some(f => f.field === config.fieldname)) return
        
        activeFilters.value.push({
            field: config.fieldname,
            operator: '=',
            value: value,
            display: `${fieldMeta.label || config.label} = ${value}`,
            isSessionDefault: true
        })
    })
}

function refreshList() {
    const formattedDoctype = formatDoctype(props.doctype)
    
    const requiredFields = ['name', 'modified']
    if (meta.value && meta.value.fields) {
        meta.value.fields.forEach(f => {
            if (f.in_list_view) requiredFields.push(f.fieldname)
        })
        if (meta.value.fields.find(f => f.fieldname === 'status')) {
            requiredFields.push('status')
        }
    }

    const apiFilters = activeFilters.value.map(f => {
        let val = f.value
        if (f.operator === 'like' || f.operator === 'not like') {
            if (!val.includes('%')) val = `%${val}%`
        }
        return [f.field, f.operator, val]
    })
    
    Object.entries(getSessionDefaultFields()).forEach(([key, config]) => {
        const value = defaults[key]
        if (value && meta.value?.fields?.some(f => f.fieldname === config.fieldname)) {
            if (!activeFilters.value.some(f => f.field === config.fieldname)) {
                apiFilters.push([config.fieldname, '=', value])
            }
        }
    })
    
    const finalFilters = apiFilters.length > 0 ? apiFilters : null
    
    if (listResource.update) {
        listResource.update({ 
            doctype: formattedDoctype,
            fields: requiredFields,
            filters: finalFilters
        })
    }
    
    listResource.reload()
}

const props = defineProps({
  doctype: {
    type: String,
    required: true
  }
})

const router = useRouter()
const route = useRoute()
const meta = ref(null)
const loadingMeta = ref(false)
const error = ref(null)

const columns = computed(() => {
  if (!meta.value) return []
  
  const cols = [
    { label: 'ID', key: 'name', width: 180 }
  ]

  const listFields = meta.value.fields.filter(f => f.in_list_view)
  
  listFields.forEach(field => {
    cols.push({
      label: field.label,
      key: field.fieldname,
      width: field.width,
    })
  })

  if (meta.value.fields.find(f => f.fieldname === 'status') && !cols.find(c => c.key === 'status')) {
     cols.push({ label: 'Durum', key: 'status', width: 120 })
  }
  
  cols.push({
      label: 'Son Güncelleme',
      key: 'modified',
      width: 160,
      align: 'right'
  })

  return cols
})

// Mobile columns: exclude name, status, modified (shown separately in cards)
const mobileColumns = computed(() => {
  return columns.value.filter(c => !['name', 'status', 'modified'].includes(c.key))
})

const listResource = createListResource({
  doctype: props.doctype,
  fields: ['*'], 
  auto: false, 
  pageLength: 50
})

function formatDoctype(name) {
    if (!name) return ''
    return name.split(' ').map(word => {
        return word.charAt(0).toUpperCase() + word.slice(1)
    }).join(' ')
}

async function fetchMeta() {
  loadingMeta.value = true
  error.value = null
  
  // Reset filters when refetching meta (route change or doctype change)
  activeFilters.value = []
  
  if (!sessionDefaultsLoaded.value) {
    await loadSessionDefaults()
  }
  
  const formattedDoctype = formatDoctype(props.doctype)
  
  try {
    const requiredFields = ['name', 'modified']
    
    // Fetch DocType Metadata
    try {
        const data = await call('frappe.desk.form.load.getdoctype', { doctype: formattedDoctype })
        if (data.docs && data.docs.length > 0) {
            meta.value = data.docs[0]
            
            if (meta.value.fields) {
                meta.value.fields.forEach(f => {
                    if (f.in_list_view) requiredFields.push(f.fieldname)
                })
                const hasStatus = meta.value.fields.find(f => f.fieldname === 'status')
                if (hasStatus) requiredFields.push('status')
            }
        }
    } catch (metaError) {
        console.warn('Metadata fetch failed, falling back to basic fields:', metaError)
    }
    
    // Apply Filters
    applySessionDefaultFilters()
    applyQueryFilters()
    
    // Refresh List Resource
    refreshList()
    
  } catch (e) {
    error.value = `Liste yüklenemedi: ${e.message}`
    console.error(e)
  } finally {
    loadingMeta.value = false
  }
}

function applyQueryFilters() {
    const query = route.query
    if (!query) return

    // Exclude 'module' from filters as it's used for sidebar context
    const excludeKeys = ['module']

    Object.entries(query).forEach(([key, value]) => {
        if (excludeKeys.includes(key)) return
        
        // Find field meta to get label
        const fieldMeta = meta.value?.fields?.find(f => f.fieldname === key)
        const label = fieldMeta?.label || key

        activeFilters.value.push({
            field: key,
            operator: '=',
            value: value,
            display: `${label} = ${value}`,
            isQueryParam: true
        })
    })
}

watch(
  [() => props.doctype, () => route.query], 
  () => {
    fetchMeta()
  }, 
  { deep: true, immediate: true }
)

watch(
  () => defaults,
  () => {
    if (meta.value && sessionDefaultsLoaded.value) {
      activeFilters.value = activeFilters.value.filter(f => !f.isSessionDefault)
      applySessionDefaultFilters()
      refreshList()
    }
  },
  { deep: true }
)

function getStatusTheme(status) {
    if (!status) return 'gray'
    const s = status.toLowerCase()
    if (s === 'active' || s === 'enabled' || s === 'paid' || s === 'completed') return 'green'
    if (s === 'draft' || s === 'open' || s === 'pending') return 'orange'
    if (s === 'cancelled' || s === 'disabled' || s === 'overdue') return 'red'
    return 'gray'
}
</script>

<style scoped>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ROOT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-root {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HEADER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  background: #ffffff;
}

.dtl-header__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.dtl-header__title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.3px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dtl-header__badge {
  font-weight: 500;
  flex-shrink: 0;
}

.dtl-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.dtl-header__btn-text--mobile {
  display: none;
}

@media (max-width: 768px) {
  .dtl-header {
    padding: 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .dtl-header__title {
    font-size: 17px;
  }

  .dtl-header__btn-text {
    display: none;
  }

  .dtl-header__btn-text--mobile {
    display: inline;
  }

  .dtl-header__btn-refresh .dtl-header__btn-text {
    display: none;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FILTERS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-filters {
  padding: 10px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .dtl-filters {
    padding: 10px 16px;
    gap: 6px;
  }
}

.dtl-filters__divider {
  width: 1px;
  height: 16px;
  background: #e2e8f0;
  margin: 0 4px;
}

.dtl-filters__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.dtl-filter-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 4px 8px 4px 10px;
  font-size: 12px;
  transition: all 200ms;
}

.dtl-filter-tag:hover {
  border-color: #cbd5e1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.dtl-filter-tag__text {
  color: #475569;
  font-weight: 500;
}

.dtl-filter-tag__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: none;
  border-radius: 4px;
  background: #f1f5f9;
  color: #94a3b8;
  cursor: pointer;
  transition: all 150ms;
}

.dtl-filter-tag__remove:hover {
  background: #fee2e2;
  color: #ef4444;
}

.dtl-filter-tag__icon {
  width: 12px;
  height: 12px;
}

.dtl-filters__clear {
  font-size: 12px;
  color: #94a3b8;
}

.dtl-filters__clear:hover {
  color: #ef4444;
}

/* Filter Popup */
.dtl-filter-popup {
  padding: 16px;
  width: 320px;
}

.dtl-filter-popup__header {
  margin-bottom: 12px;
}

.dtl-filter-popup__title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.dtl-filter-popup__field {
  margin-bottom: 10px;
}

.dtl-filter-popup__label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 4px;
}

.dtl-filter-popup__select {
  width: 100%;
  font-size: 13px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 7px 12px;
  background: #f8fafc;
  color: #0f172a;
  outline: none;
  transition: border-color 200ms;
}

.dtl-filter-popup__select:focus {
  border-color: #94a3b8;
}

.dtl-filter-popup__actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
}

.dtl-filter-popup__btn {
  flex: 1;
}

@media (max-width: 768px) {
  .dtl-filter-popup {
    width: 260px;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CONTENT AREA
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-content {
  flex: 1;
  overflow: auto;
  background: #f8fafc;
  padding: 20px 24px;
}

@media (max-width: 768px) {
  .dtl-content {
    padding: 12px;
  }
}

/* Loading */
.dtl-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dtl-loading__skeleton {
  height: 56px;
  width: 100%;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: dtl-shimmer 1.5s infinite;
  border-radius: 10px;
}

@keyframes dtl-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Error */
.dtl-error {
  padding: 16px;
  border-radius: 10px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.dtl-error__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Empty */
.dtl-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  text-align: center;
  padding: 24px;
}

.dtl-empty__icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.dtl-empty__icon {
  width: 28px;
  height: 28px;
  color: #94a3b8;
}

.dtl-empty__title {
  font-size: 17px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 6px;
}

.dtl-empty__desc {
  font-size: 14px;
  color: #64748b;
  max-width: 340px;
  line-height: 1.5;
  margin: 0;
}

.dtl-empty__btn {
  margin-top: 16px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DATA CONTAINER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-data {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
  overflow: hidden;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DESKTOP TABLE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-table-wrap {
  overflow-x: auto;
}

.dtl-table {
  width: 100%;
  text-align: left;
  border-collapse: collapse;
}

.dtl-table__head-row {
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}

.dtl-table__th {
  padding: 12px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  white-space: nowrap;
}

.dtl-table__th--checkbox {
  width: 44px;
  padding-right: 0;
}

.dtl-table__th--right {
  text-align: right;
}

.dtl-table__row {
  border-bottom: 1px solid #f1f5f9;
  transition: background 150ms;
  cursor: pointer;
}

.dtl-table__row:hover {
  background: #f8fafc;
}

.dtl-table__row:last-child {
  border-bottom: none;
}

.dtl-table__td {
  padding: 12px 16px;
  font-size: 13px;
  color: #334155;
  white-space: nowrap;
}

.dtl-table__td--checkbox {
  width: 44px;
  padding-right: 0;
}

.dtl-table__td--right {
  text-align: right;
}

.dtl-table__name-cell {
  font-weight: 600;
  color: #3b82f6;
}

.dtl-table__row:hover .dtl-table__name-cell {
  color: #2563eb;
}

.dtl-table__cell-text {
  color: #475569;
}

.dtl-checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid #cbd5e1;
  cursor: pointer;
  transition: all 150ms;
  accent-color: #3b82f6;
}

/* Hide table on mobile */
@media (max-width: 768px) {
  .dtl-table-wrap {
    display: none;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MOBILE CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-cards {
  display: none;
}

@media (max-width: 768px) {
  .dtl-cards {
    display: flex;
    flex-direction: column;
  }
}

.dtl-card {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 150ms;
}

.dtl-card:hover {
  background: #f8fafc;
}

.dtl-card:last-child {
  border-bottom: none;
}

.dtl-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.dtl-card__id {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
}

.dtl-card__body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}

.dtl-card__field {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.dtl-card__field-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #94a3b8;
}

.dtl-card__field-value {
  font-size: 13px;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dtl-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #f1f5f9;
}

.dtl-card__modified {
  font-size: 11px;
  color: #94a3b8;
}

.dtl-card__arrow {
  width: 16px;
  height: 16px;
  color: #cbd5e1;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PAGINATION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dtl-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}

.dtl-pagination__info {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.dtl-pagination__count {
  font-weight: 600;
  color: #0f172a;
}

.dtl-pagination__btns {
  display: flex;
  gap: 6px;
}

@media (max-width: 768px) {
  .dtl-pagination {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}
</style>
