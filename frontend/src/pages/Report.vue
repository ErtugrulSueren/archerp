<template>
  <div class="rpt-root">
    <!-- Header -->
    <header class="rpt-header">
      <div class="rpt-header__left">
        <h1 class="rpt-header__title">{{ reportTitle }}</h1>
        <Badge v-if="data.length" theme="gray" size="sm" class="rpt-header__badge">{{ data.length }} Kayıt</Badge>
      </div>
      
      <div class="rpt-header__actions">
        <AppButton 
          variant="subtle" 
          theme="gray" 
          size="md" 
          icon-left="refresh-cw" 
          @click="runReport"
          :loading="loading"
          class="rpt-header__btn"
        >
          <span class="rpt-header__btn-text">Yenile</span>
        </AppButton>
        <AppButton 
          variant="subtle" 
          theme="gray" 
          size="md" 
          icon-left="download" 
          @click="exportToExcel"
          :disabled="!data.length"
          class="rpt-header__btn"
        >
          <span class="rpt-header__btn-text">Dışa Aktar</span>
        </AppButton>
        <AppButton 
          variant="solid" 
          size="md" 
          icon-left="play" 
          @click="runReport"
          :loading="loading"
          class="rpt-header__run-btn"
        >
          <span class="rpt-header__btn-text--full">Raporu Çalıştır</span>
          <span class="rpt-header__btn-text--short">Çalıştır</span>
        </AppButton>
      </div>
    </header>

    <!-- Filter Bar -->
    <div class="rpt-filter-bar">
      <!-- Script Report Filters (inline) -->
      <template v-if="isScriptReport && filters.length > 0">
        <div v-for="filter in filters" :key="filter.fieldname" class="rpt-filter">
          <label class="rpt-filter__label">{{ filter.label }}</label>
          
          <!-- Link Field -->
          <select 
            v-if="filter.fieldtype === 'Link'"
            v-model="filterValues[filter.fieldname]"
            class="rpt-filter__select"
          >
            <option value="">Tümü</option>
            <option v-for="opt in filter.options_list || []" :key="opt" :value="opt">{{ opt }}</option>
          </select>
          
          <!-- Date Field -->
          <input 
            v-else-if="filter.fieldtype === 'Date'"
            type="date"
            v-model="filterValues[filter.fieldname]"
            class="rpt-filter__input"
          />
          
          <!-- Select Field -->
          <select 
            v-else-if="filter.fieldtype === 'Select'"
            v-model="filterValues[filter.fieldname]"
            class="rpt-filter__select"
          >
            <option value="">Tümü</option>
            <option v-for="opt in (filter.options || '').split('\n').filter(o => o)" :key="opt" :value="opt">{{ opt }}</option>
          </select>
          
          <!-- Check Field -->
          <label v-else-if="filter.fieldtype === 'Check'" class="rpt-filter__check">
            <input 
              type="checkbox" 
              v-model="filterValues[filter.fieldname]"
              class="rpt-filter__checkbox"
            />
          </label>
          
          <!-- Default Text/Data -->
          <input 
            v-else
            type="text"
            v-model="filterValues[filter.fieldname]"
            :placeholder="filter.label"
            class="rpt-filter__input"
          />
        </div>
        
        <AppButton 
          variant="ghost" 
          size="sm" 
          class="rpt-filter__clear-btn"
          @click="resetFilters"
        >
          Temizle
        </AppButton>
      </template>
      
      <!-- Report Builder Filters (Popover based) -->
      <template v-else-if="!isScriptReport && doctypeMeta">
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
            <div class="rpt-filter-popover">
              <div class="rpt-filter-popover__header">
                <span class="rpt-filter-popover__title">Filtre Oluştur</span>
              </div>

              <div class="rpt-filter-popover__field">
                <label class="rpt-filter-popover__label">Alan</label>
                <select 
                  v-model="newFilter.field"
                  class="rpt-filter-popover__select"
                >
                  <option value="" disabled selected>Seçiniz...</option>
                  <option v-for="opt in filterableFieldOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
              
              <div class="rpt-filter-popover__field" v-if="newFilter.field">
                <label class="rpt-filter-popover__label">Koşul</label>
                <select 
                  v-model="newFilter.operator"
                  class="rpt-filter-popover__select"
                >
                  <option v-for="op in operators" :key="op.value" :value="op.value">
                    {{ op.label }}
                  </option>
                </select>
              </div>

              <div class="rpt-filter-popover__field" v-if="newFilter.field">
                <label class="rpt-filter-popover__label">Değer</label>
                <input
                  v-model="newFilter.value"
                  type="text"
                  class="rpt-filter-popover__input"
                  placeholder="Değer girin..."
                />
              </div>

              <div class="rpt-filter-popover__actions">
                <AppButton 
                  variant="subtle"
                  class="rpt-filter-popover__cancel"
                  size="sm"
                  @click="showFilterPopover = false"
                >
                  İptal
                </AppButton>
                <AppButton 
                  variant="solid" 
                  class="rpt-filter-popover__apply"
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

        <div class="rpt-filter-bar__sep" v-if="activeFilters.length > 0"></div>

        <!-- Active Filters -->
        <div v-for="(filter, idx) in activeFilters" :key="idx" class="rpt-active-filter">
          <span class="rpt-active-filter__text">{{ filter.display }}</span>
          <button class="rpt-active-filter__remove" @click="removeFilter(idx)">
            <FeatherIcon name="x" class="rpt-active-filter__x" />
          </button>
        </div>
        
        <AppButton 
          v-if="activeFilters.length > 0" 
          variant="ghost" 
          size="sm" 
          class="rpt-filter__clear-btn"
          @click="clearFilters"
        >
          Temizle
        </AppButton>
      </template>
    </div>

    <!-- Content -->
    <div class="rpt-content">
      
      <!-- Loading State -->
      <div v-if="loading" class="rpt-loading">
        <div v-for="i in 5" :key="i" class="rpt-loading__row"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rpt-error">
        <FeatherIcon name="alert-circle" class="rpt-error__icon" />
        <span class="rpt-error__text">{{ error }}</span>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!data.length && !loading" class="rpt-empty">
        <div class="rpt-empty__icon-wrap">
          <FeatherIcon name="file-text" class="rpt-empty__icon" />
        </div>
        <h3 class="rpt-empty__title">Rapor Verisi Yok</h3>
        <p class="rpt-empty__desc">Filtreleri ayarlayıp "Raporu Çalıştır" butonuna tıklayın</p>
      </div>

      <!-- Data Table (Desktop) -->
      <div v-else class="rpt-table-wrap">
        <div class="rpt-table-scroll">
          <table class="rpt-table">
            <thead>
              <tr class="rpt-table__head-row">
                <th 
                  v-for="col in columns" 
                  :key="col.fieldname" 
                  class="rpt-table__th"
                >
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(row, idx) in data" 
                :key="idx" 
                class="rpt-table__row"
              >
                <td 
                  v-for="col in columns" 
                  :key="col.fieldname" 
                  class="rpt-table__td"
                >
                  <template v-if="col.fieldtype === 'Currency'">
                    {{ formatCurrency(row[col.fieldname]) }}
                  </template>
                  <template v-else-if="col.fieldtype === 'Float' || col.fieldtype === 'Percent'">
                    {{ formatNumber(row[col.fieldname]) }}
                  </template>
                  <template v-else-if="col.fieldtype === 'Date'">
                    {{ formatDate(row[col.fieldname]) }}
                  </template>
                  <template v-else-if="col.fieldname === 'name'">
                    <span class="rpt-table__name">{{ row[col.fieldname] }}</span>
                  </template>
                  <template v-else>
                    {{ row[col.fieldname] ?? '-' }}
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Mobile Cards -->
        <div class="rpt-cards">
          <div 
            v-for="(row, idx) in data" 
            :key="'card-'+idx" 
            class="rpt-card"
          >
            <!-- Card Header: show name or first column -->
            <div class="rpt-card__header">
              <span class="rpt-card__id">{{ row[columns[0]?.fieldname] || '-' }}</span>
            </div>
            <!-- Card Body: remaining columns in 2-col grid -->
            <div class="rpt-card__body">
              <div 
                v-for="col in columns.slice(1, 7)" 
                :key="col.fieldname" 
                class="rpt-card__field"
              >
                <span class="rpt-card__field-label">{{ col.label }}</span>
                <span class="rpt-card__field-value">
                  <template v-if="col.fieldtype === 'Currency'">{{ formatCurrency(row[col.fieldname]) }}</template>
                  <template v-else-if="col.fieldtype === 'Float' || col.fieldtype === 'Percent'">{{ formatNumber(row[col.fieldname]) }}</template>
                  <template v-else-if="col.fieldtype === 'Date'">{{ formatDate(row[col.fieldname]) }}</template>
                  <template v-else>{{ row[col.fieldname] ?? '-' }}</template>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="rpt-footer">
          <p class="rpt-footer__text">
            Toplam <span class="rpt-footer__count">{{ data.length }}</span> kayıt gösteriliyor
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { call, FeatherIcon, Badge, Popover } from 'frappe-ui'
import AppButton from '../components/AppButton.vue'
import { useSessionDefaults } from '@/composables/useSessionDefaults'

const { defaults, getSessionDefaultFields, loadDefaults: loadSessionDefaults, isLoaded: sessionDefaultsLoaded } = useSessionDefaults()

const props = defineProps({
  reportName: { type: String, required: true }
})

const router = useRouter()
const route = useRoute()

// State
const loading = ref(false)
const error = ref(null)
const reportMeta = ref(null)
const filters = ref([])
const filterValues = ref({})
const columns = ref([])
const data = ref([])
const isScriptReport = ref(false)
const refDoctype = ref(null)
const doctypeMeta = ref(null)

// Report Builder Filter State
const showFilterPopover = ref(false)
const activeFilters = ref([])
const newFilter = ref({
  field: null,
  operator: '=',
  value: null
})

// Operators
const operators = [
  { label: 'Eşittir', value: '=' },
  { label: 'Eşit Değil', value: '!=' },
  { label: 'İçerir', value: 'like' },
  { label: 'Büyüktür', value: '>' },
  { label: 'Küçüktür', value: '<' },
  { label: 'Büyük Eşit', value: '>=' },
  { label: 'Küçük Eşit', value: '<=' },
]

// Computed for filter field options
const filterableFieldOptions = computed(() => {
  if (!doctypeMeta.value || !doctypeMeta.value.fields) return []
  return doctypeMeta.value.fields
    .filter(f => !['Section Break', 'Column Break', 'Tab Break'].includes(f.fieldtype) && !f.hidden)
    .map(f => ({
      label: f.label,
      value: f.fieldname,
      fieldtype: f.fieldtype
    }))
})

// Computed
const reportTitle = computed(() => {
  if (reportMeta.value?.report_name) return reportMeta.value.report_name
  return decodeURIComponent(props.reportName).replace(/-/g, ' ')
})

// Helpers
function formatCurrency(val) {
  if (val == null || val === '') return '-'
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(val)
}

function formatNumber(val) {
  if (val == null || val === '') return '-'
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)
}

function formatDate(val) {
  if (!val) return '-'
  return new Date(val).toLocaleDateString('tr-TR')
}

// Load Report Meta
async function loadReportMeta() {
  loading.value = true
  error.value = null
  
  // Reset all report state for clean navigation between reports
  columns.value = []
  data.value = []
  filters.value = []
  filterValues.value = {}
  reportMeta.value = null
  isScriptReport.value = false
  refDoctype.value = null
  doctypeMeta.value = null
  activeFilters.value = []
  
  try {
    // First ensure session defaults are loaded
    if (!sessionDefaultsLoaded.value) {
      await loadSessionDefaults()
    }
    
    const reportName = decodeURIComponent(props.reportName)
    
    // Get report document
    const reportDoc = await call('frappe.client.get', {
      doctype: 'Report',
      name: reportName
    })
    
    reportMeta.value = reportDoc
    
    // Check report type: Script Report and Query Report both use query_report API
    if (reportDoc.is_standard === 'Yes' || reportDoc.report_type === 'Script Report' || reportDoc.report_type === 'Query Report') {
      // Script Report / Query Report - use query_report API
      isScriptReport.value = true
      
      const scriptResult = await call('frappe.desk.query_report.get_script', {
        report_name: reportName
      })
      
      if (scriptResult?.filters && scriptResult.filters.length > 0) {
        filters.value = scriptResult.filters
        scriptResult.filters.forEach(f => {
          filterValues.value[f.fieldname] = f.default !== undefined ? f.default : ''
        })
        await loadLinkOptions()
      } else if (reportDoc.report_type === 'Query Report' && reportDoc.query) {
        // Query Report without filter definitions: extract %(key)s placeholders from SQL
        const placeholderRegex = /%\((\w+)\)s/g
        let match
        const extractedFilters = []
        const seen = new Set()
        
        while ((match = placeholderRegex.exec(reportDoc.query)) !== null) {
          const key = match[1]
          if (seen.has(key)) continue
          seen.add(key)
          
          // Guess fieldtype from key name
          const isDate = key.includes('date') || key.includes('tarih')
          const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
          
          extractedFilters.push({
            fieldname: key,
            label: label,
            fieldtype: isDate ? 'Date' : 'Data',
            reqd: 1
          })
          filterValues.value[key] = ''
        }
        
        if (extractedFilters.length > 0) {
          filters.value = extractedFilters
        }
      }
    } else {
      // Report Builder - get doctype meta for filters
      isScriptReport.value = false
      
      if (reportDoc.ref_doctype) {
        refDoctype.value = reportDoc.ref_doctype
        
        // Get doctype meta for field info
        const metaRes = await call('frappe.desk.form.load.getdoctype', { 
          doctype: reportDoc.ref_doctype 
        })
        
        if (metaRes.docs && metaRes.docs.length > 0) {
          doctypeMeta.value = metaRes.docs[0]
        }
      }
    }
    
    // Apply session defaults to activeFilters for Report Builder
    if (!isScriptReport.value && doctypeMeta.value) {
      applySessionDefaultFilters()
    }
    
    // Auto-run report: skip if Query Report has SQL placeholders without values
    let shouldAutoRun = true
    
    if (reportDoc.report_type === 'Query Report' && reportDoc.query) {
      // Extract all %(key)s placeholders from SQL
      const placeholderRegex = /%\((\w+)\)s/g
      let match
      while ((match = placeholderRegex.exec(reportDoc.query)) !== null) {
        const key = match[1]
        if (!filterValues.value[key] || filterValues.value[key] === '') {
          shouldAutoRun = false
          break
        }
      }
    } else if (isScriptReport.value && filters.value.some(f => 
      f.reqd && (!filterValues.value[f.fieldname] || filterValues.value[f.fieldname] === '')
    )) {
      shouldAutoRun = false
    }
    
    if (shouldAutoRun) {
      await runReport()
    }
    
  } catch (e) {
    error.value = e.message || 'Rapor yüklenemedi'
    console.error('Report load error:', e)
  } finally {
    loading.value = false
  }
}

// Load options for Link fields
async function loadLinkOptions() {
  const linkFilters = filters.value.filter(f => f.fieldtype === 'Link' && f.options)
  
  await Promise.all(linkFilters.map(async (f) => {
    try {
      const res = await call('frappe.client.get_list', {
        doctype: f.options,
        limit_page_length: 0,
        fields: ['name']
      })
      f.options_list = res.map(r => r.name)
    } catch (e) {
      console.warn(`Failed to load options for ${f.fieldname}`, e)
      f.options_list = []
    }
  }))
}

// Run Report
async function runReport() {
  loading.value = true
  error.value = null
  
  try {
    const reportName = decodeURIComponent(props.reportName)
    
    if (isScriptReport.value) {
      // Script Report / Query Report - use query_report API
      const reportFilters = {}
      const isQueryReport = reportMeta.value && reportMeta.value.report_type === 'Query Report'
      
      Object.entries(filterValues.value).forEach(([key, val]) => {
        if (isQueryReport) {
          // Query Report: send ALL values (even empty) so SQL %(key)s placeholders work
          reportFilters[key] = val !== null && val !== undefined ? val : ''
        } else if (val !== '' && val !== null && val !== undefined) {
          reportFilters[key] = val
        }
      })
      
      const result = await call('frappe.desk.query_report.run', {
        report_name: reportName,
        filters: JSON.stringify(reportFilters)
      })
      
      
      if (result) {
        processScriptReportResult(result)
      }
    } else {
      // Report Builder - use reportview API
      const doctype = refDoctype.value
      if (!doctype) {
        error.value = 'Rapor DocType\'ı bulunamadı'
        return
      }
      
      // Build filters from activeFilters + session defaults
      let reportFilters = activeFilters.value.map(f => {
        let val = f.value
        if (f.operator === 'like' || f.operator === 'not like') {
          if (!val.includes('%')) val = `%${val}%`
        }
        return [doctype, f.field, f.operator, val]
      })
      
      // Add session default filters (if not already in activeFilters)
      Object.entries(getSessionDefaultFields()).forEach(([key, config]) => {
        const value = defaults[key]
        if (value && !activeFilters.value.some(f => f.field === config.fieldname)) {
          // Check if doctype has this field
          if (doctypeMeta.value?.fields?.some(f => f.fieldname === config.fieldname)) {
            reportFilters.push([doctype, config.fieldname, '=', value])
          }
        }
      })
      
      // Get report columns from Report document
      let fields = ['name']
      if (reportMeta.value?.columns) {
        // Report has defined columns - could be string or array
        if (typeof reportMeta.value.columns === 'string') {
          fields = reportMeta.value.columns.split('\n').filter(c => c.trim())
        } else if (Array.isArray(reportMeta.value.columns)) {
          fields = reportMeta.value.columns.map(c => c.fieldname || c.field || c)
        }
      } else if (reportMeta.value?.json) {
        // Try to get from json config
        try {
          const jsonConfig = JSON.parse(reportMeta.value.json)
          if (jsonConfig.columns) {
            fields = jsonConfig.columns.map(c => c.fieldname || c.field || c)
          }
        } catch (e) {
          console.warn('[Report] Failed to parse json config', e)
        }
      }
      
      // If no columns defined, get from doctype meta
      if (fields.length <= 1 && doctypeMeta.value?.fields) {
        fields = doctypeMeta.value.fields
          .filter(f => f.in_list_view && !['Section Break', 'Column Break', 'Tab Break'].includes(f.fieldtype))
          .map(f => f.fieldname)
          .slice(0, 10) // Limit to 10 columns
        
        if (!fields.includes('name')) fields.unshift('name')
      }
      
      
      const result = await call('frappe.desk.reportview.get', {
        doctype: doctype,
        fields: JSON.stringify(fields),
        filters: JSON.stringify(reportFilters),
        order_by: 'modified desc',
        start: 0,
        page_length: 100,
        view: 'Report',
        with_comment_count: false
      })
      
      
      if (result) {
        processReportBuilderResult(result, fields)
      }
    }
    
  } catch (e) {
    error.value = e.message || e.exc || 'Rapor çalıştırılamadı'
    console.error('Report run error:', e)
  } finally {
    loading.value = false
  }
}

// Process Script Report result
function processScriptReportResult(result) {
  if (result.columns) {
    columns.value = result.columns.map(col => {
      if (typeof col === 'string') {
        const parts = col.split(':')
        return {
          label: parts[0],
          fieldname: parts[0].toLowerCase().replace(/ /g, '_'),
          fieldtype: parts[1] || 'Data',
          width: parts[2] || 150
        }
      }
      return {
        label: col.label || col.fieldname,
        fieldname: col.fieldname || col.label?.toLowerCase().replace(/ /g, '_'),
        fieldtype: col.fieldtype || 'Data',
        width: col.width || 150
      }
    })
  }
  
  let resultData = result.result || result.data || []
  
  if (resultData.length > 0 && Array.isArray(resultData[0])) {
    resultData = resultData.map(row => {
      const obj = {}
      columns.value.forEach((col, idx) => {
        obj[col.fieldname] = row[idx]
      })
      return obj
    })
  }
  
  data.value = resultData
}

// Process Report Builder result
function processReportBuilderResult(result, fields) {
  // Build columns from fields and doctype meta
  columns.value = fields.map(fieldname => {
    const fieldMeta = doctypeMeta.value?.fields?.find(f => f.fieldname === fieldname)
    return {
      label: fieldMeta?.label || fieldname,
      fieldname: fieldname,
      fieldtype: fieldMeta?.fieldtype || 'Data',
      width: 150
    }
  })
  
  // Result structure: { keys: [...], values: [[...], [...]] }
  if (result.keys && result.values && Array.isArray(result.values)) {
    data.value = result.values.map(row => {
      const obj = {}
      result.keys.forEach((key, idx) => {
        obj[key] = row[idx]
      })
      return obj
    })
  } else if (Array.isArray(result)) {
    data.value = result
  } else {
    data.value = []
  }
}

// Add Filter (for Report Builder)
function addFilter() {
  if (!newFilter.value.field || newFilter.value.value === null || newFilter.value.value === '') return
  
  const fieldLabel = filterableFieldOptions.value.find(f => f.value === newFilter.value.field)?.label || newFilter.value.field
  const operatorLabel = operators.find(o => o.value === newFilter.value.operator)?.label
  
  activeFilters.value.push({
    field: newFilter.value.field,
    operator: newFilter.value.operator,
    value: newFilter.value.value,
    display: `${fieldLabel} ${operatorLabel} ${newFilter.value.value}`
  })
  
  // Reset
  newFilter.value = { field: null, operator: '=', value: null }
  showFilterPopover.value = false
  
  runReport()
}

function removeFilter(index) {
  activeFilters.value.splice(index, 1)
  runReport()
}

function clearFilters() {
  activeFilters.value = activeFilters.value.filter(f => f.isSessionDefault)
  runReport()
}

// Apply session default values as visible filters
function applySessionDefaultFilters() {
  if (!doctypeMeta.value?.fields) return
  
  Object.entries(getSessionDefaultFields()).forEach(([key, config]) => {
    const value = defaults[key]
    if (!value) return
    
    // Check if doctype has this field
    const fieldMeta = doctypeMeta.value.fields.find(f => f.fieldname === config.fieldname)
    if (!fieldMeta) return
    
    // Check if already in activeFilters
    if (activeFilters.value.some(f => f.field === config.fieldname)) return
    
    // Add as a session default filter
    activeFilters.value.push({
      field: config.fieldname,
      operator: '=',
      value: value,
      display: `${fieldMeta.label || config.label} = ${value}`,
      isSessionDefault: true
    })
  })
}

// Reset Filters (for Script Reports)
function resetFilters() {
  filters.value.forEach(f => {
    filterValues.value[f.fieldname] = f.default !== undefined ? f.default : ''
  })
}

// Export to Excel (simple CSV for now)
function exportToExcel() {
  if (!data.value.length) return
  
  const headers = columns.value.map(c => c.label).join(',')
  const rows = data.value.map(row => 
    columns.value.map(c => {
      let val = row[c.fieldname] ?? ''
      // Escape commas and quotes
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
        val = `"${val.replace(/"/g, '""')}"`
      }
      return val
    }).join(',')
  )
  
  const csv = [headers, ...rows].join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${reportTitle.value}_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
}

// Watch for route changes
watch(() => props.reportName, () => {
  loadReportMeta()
})

// Watch session defaults changes and rerun report
watch(
  () => defaults,
  () => {
    if (doctypeMeta.value && sessionDefaultsLoaded.value && !isScriptReport.value) {
      // First remove old session default filters
      activeFilters.value = activeFilters.value.filter(f => !f.isSessionDefault)
      // Reapply session default filters and run report
      applySessionDefaultFilters()
      runReport()
    }
  },
  { deep: true }
)

onMounted(() => {
  loadReportMeta()
})
</script>

<style scoped>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ROOT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-root {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HEADER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.rpt-header__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.rpt-header__title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.3px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rpt-header__badge {
  flex-shrink: 0;
  font-weight: 600;
}

.rpt-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.rpt-header__btn-text--short {
  display: none;
}

@media (max-width: 768px) {
  .rpt-header {
    padding: 14px 16px;
    gap: 10px;
  }

  .rpt-header__title {
    font-size: 16px;
  }

  .rpt-header__actions {
    gap: 6px;
  }

  .rpt-header__btn-text {
    display: none;
  }

  .rpt-header__btn-text--full {
    display: none;
  }

  .rpt-header__btn-text--short {
    display: inline;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FILTER BAR
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.rpt-filter-bar__sep {
  width: 1px;
  height: 16px;
  background: #e2e8f0;
  margin: 0 4px;
}

@media (max-width: 768px) {
  .rpt-filter-bar {
    padding: 8px 12px;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .rpt-filter-bar::-webkit-scrollbar {
    display: none;
  }

  .rpt-filter-bar__sep {
    display: none;
  }
}

/* ── Script Report Filter Item ── */
.rpt-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.rpt-filter__label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  white-space: nowrap;
}

.rpt-filter__select,
.rpt-filter__input {
  font-size: 13px;
  padding: 6px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  min-width: 140px;
  transition: border-color 200ms, box-shadow 200ms;
  outline: none;
}

.rpt-filter__select:focus,
.rpt-filter__input:focus {
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.15);
}

.rpt-filter__check {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.rpt-filter__checkbox {
  width: 16px;
  height: 16px;
  accent-color: #3b82f6;
  border-radius: 4px;
}

.rpt-filter__clear-btn {
  font-size: 12px;
  color: #94a3b8;
  flex-shrink: 0;
}

.rpt-filter__clear-btn:hover {
  color: #ef4444;
}

@media (max-width: 768px) {
  .rpt-filter__select,
  .rpt-filter__input {
    min-width: 120px;
    font-size: 13px;
    padding: 8px 10px;
  }
}

/* ── Report Builder Active Filters ── */
.rpt-active-filter {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  transition: all 200ms;
  cursor: default;
  flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.rpt-active-filter:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.rpt-active-filter__text {
  color: #475569;
  font-weight: 500;
  margin-right: 6px;
  white-space: nowrap;
}

.rpt-active-filter__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f1f5f9;
  border-radius: 4px;
  padding: 2px;
  cursor: pointer;
  color: #94a3b8;
  transition: all 200ms;
}

.rpt-active-filter__remove:hover {
  color: #ef4444;
  background: #fef2f2;
}

.rpt-active-filter__x {
  width: 12px;
  height: 12px;
}

/* ── Filter Popover ── */
.rpt-filter-popover {
  padding: 16px;
  width: 320px;
}

.rpt-filter-popover__header {
  margin-bottom: 12px;
}

.rpt-filter-popover__title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.rpt-filter-popover__field {
  margin-bottom: 12px;
}

.rpt-filter-popover__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 4px;
}

.rpt-filter-popover__select,
.rpt-filter-popover__input {
  width: 100%;
  font-size: 13px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  outline: none;
  transition: border-color 200ms;
}

.rpt-filter-popover__select:focus,
.rpt-filter-popover__input:focus {
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.15);
}

.rpt-filter-popover__actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
}

.rpt-filter-popover__cancel,
.rpt-filter-popover__apply {
  flex: 1;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CONTENT
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

@media (max-width: 768px) {
  .rpt-content {
    padding: 12px;
  }
}

/* ── Loading ── */
.rpt-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rpt-loading__row {
  height: 52px;
  width: 100%;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: rpt-shimmer 1.5s ease-in-out infinite;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

@keyframes rpt-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Error ── */
.rpt-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-radius: 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 14px;
}

.rpt-error__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* ── Empty ── */
.rpt-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 320px;
  text-align: center;
  padding: 20px;
}

.rpt-empty__icon-wrap {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #e2e8f0, #f1f5f9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.rpt-empty__icon {
  width: 32px;
  height: 32px;
  color: #94a3b8;
}

.rpt-empty__title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.rpt-empty__desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
  max-width: 300px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DATA TABLE (Desktop)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-table-wrap {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
  overflow: hidden;
}

.rpt-table-scroll {
  overflow-x: auto;
}

.rpt-table {
  width: 100%;
  text-align: left;
  border-collapse: collapse;
}

.rpt-table__head-row {
  background: linear-gradient(180deg, #f8fafc, #f1f5f9);
  border-bottom: 1px solid #e2e8f0;
}

.rpt-table__th {
  padding: 12px 16px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #64748b;
  white-space: nowrap;
  position: sticky;
  top: 0;
  background: inherit;
}

.rpt-table__row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 150ms ease;
}

.rpt-table__row:hover {
  background: #f8fafc;
}

.rpt-table__row:last-child {
  border-bottom: none;
}

.rpt-table__td {
  padding: 12px 16px;
  font-size: 13px;
  color: #334155;
  white-space: nowrap;
}

.rpt-table__name {
  font-weight: 600;
  color: #3b82f6;
}

/* Hide table on mobile, show cards instead */
@media (max-width: 768px) {
  .rpt-table-scroll {
    display: none;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MOBILE CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-cards {
  display: none;
}

@media (max-width: 768px) {
  .rpt-cards {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .rpt-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
    transition: box-shadow 200ms;
  }

  .rpt-card:active {
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }

  .rpt-card__header {
    padding: 12px 14px;
    border-bottom: 1px solid #f1f5f9;
    background: #f8fafc;
  }

  .rpt-card__id {
    font-size: 14px;
    font-weight: 600;
    color: #3b82f6;
  }

  .rpt-card__body {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: #f1f5f9;
  }

  .rpt-card__field {
    display: flex;
    flex-direction: column;
    padding: 10px 14px;
    background: white;
  }

  .rpt-card__field-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #94a3b8;
    margin-bottom: 2px;
  }

  .rpt-card__field-value {
    font-size: 13px;
    color: #334155;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FOOTER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.rpt-footer {
  padding: 12px 16px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rpt-footer__text {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
}

.rpt-footer__count {
  font-weight: 600;
  color: #334155;
}

@media (max-width: 768px) {
  .rpt-footer {
    padding: 10px 14px;
  }
}
</style>
