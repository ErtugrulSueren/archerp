<template>
  <div class="form-control" v-if="componentType">
    <!-- Component Logic -->
    
    <!-- Link Field -->
    <LinkControl
      v-if="componentType === 'Link'"
      v-model="model"
      :target-doctype="field.options"
      :label="field.label"
      :disabled="isDisabled"
      :required="!!field.reqd"
      :placeholder="field.label"
      :filters="linkFilters"
    />

    <!-- Select Field -->
    <Select
      v-else-if="componentType === 'Select'"
      v-model="model"
      :options="selectOptions"
      :label="field.label"
      :disabled="isDisabled"
      :required="!!field.reqd"
      :placeholder="field.label"
    />

    <!-- Checkbox Field -->
    <Checkbox
      v-else-if="componentType === 'Check'"
      v-model="checkboxModel"
      :label="field.label"
      :disabled="isDisabled"
      :help="field.description"
    />

    <!-- Textarea (Text, Small Text) -->
    <div v-else-if="componentType === 'Textarea'">
        <label v-if="field.label" class="block text-sm font-medium text-gray-700 mb-1">
            {{ field.label }} <span v-if="field.reqd" class="text-red-500">*</span>
        </label>
        <textarea
            v-model="model"
            :disabled="isDisabled"
            rows="3"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm disabled:bg-gray-50 disabled:text-gray-500"
            :placeholder="field.label"
        ></textarea>
        <p v-if="field.description" class="mt-1 text-sm text-gray-500">{{ field.description }}</p>
    </div>

    <!-- Table Field (Child Table) -->
    <TableControl
      v-else-if="componentType === 'Table'"
      v-model="model"
      :doctype="field.options"
      :label="field.label"
      :disabled="isDisabled"
      :description="field.description"
      :required="!!field.reqd"
    />

    <!-- HTML Field -->
    <div v-else-if="componentType === 'HTML'" v-html="field.options" class="prose max-w-none text-sm text-gray-600 my-2"></div>

    <!-- File/Attach Field -->
    <FileUploader
      v-else-if="componentType === 'File'"
      v-model="model"
      :label="field.label"
      :disabled="isDisabled"
      :doctype="doc.doctype"
      :docname="doc.name"
      :fieldname="field.fieldname"
      :is-private="field.options === 'Private'"
    />

    <!-- Heading Field -->
    <div v-else-if="componentType === 'Heading'" class="mt-2 mb-1">
        <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider">{{ field.label }}</h4>
    </div>

    <!-- Default Input (Data, Int, Float, Currency, Date, Time, Color, etc.) -->
    <Input
      v-else
      v-model="model"
      :type="inputType"
      :label="field.label"
      :disabled="isDisabled"
      :required="!!field.reqd"
      :placeholder="field.label"
      :help="field.description"
    />

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button } from 'frappe-ui'
import Input from './Input.vue'
import Select from './Select.vue'
import Checkbox from './Checkbox.vue'
import LinkControl from './LinkControl.vue'
import TableControl from './TableControl.vue'
import FileUploader from './FileUploader.vue'

const props = defineProps({
  field: { type: Object, required: true },
  modelValue: [String, Number, Boolean, Object, Array],
  doc: { type: Object, default: () => ({}) },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const checkboxModel = computed({
    get: () => {
        const val = props.modelValue
        if (val === 0 || val === '0' || val === false || val === null || val === undefined) return false
        return true
    },
    set: (val) => emit('update:modelValue', val ? 1 : 0)
})

// Helper to evaluate expressions safely-ish
function evaluateDependsOn(expression, doc) {
    if (!expression) return true
    if (expression.startsWith && expression.startsWith('eval:')) {
        try {
            const code = expression.substring(5)
            const fn = new Function('doc', `return ${code}`)
            return fn(doc)
        } catch (e) {
            console.warn('Eval error:', e)
            return true 
        }
    }
    if (doc[expression]) return true
    return !!doc[expression]
}

const isVisible = computed(() => {
    if (props.field.hidden) return false
    if (props.field.depends_on) {
        return evaluateDependsOn(props.field.depends_on, props.doc)
    }
    return true
})

const isRequired = computed(() => {
    if (props.field.mandatory_depends_on) {
        return evaluateDependsOn(props.field.mandatory_depends_on, props.doc)
    }
    return !!props.field.reqd
})

const isDisabled = computed(() => {
  if (props.disabled) return true
  if (!!props.field.read_only || !!props.field.disabled || props.doc.docstatus === 1) return true
  if (props.field.read_only_depends_on) {
      return evaluateDependsOn(props.field.read_only_depends_on, props.doc)
  }
  return false
})

const componentType = computed(() => {
  if (!isVisible.value) return null 
  
  const type = props.field.fieldtype
  if (['Table'].includes(type)) return 'Table'
  if (['Link', 'Dynamic Link'].includes(type)) return 'Link'
  if (['Select'].includes(type)) return 'Select'
  if (['Check'].includes(type)) return 'Check'
  if (['Text', 'Small Text', 'Text Editor', 'Code', 'Long Text'].includes(type)) return 'Textarea'
  if (['HTML'].includes(type)) return 'HTML'
  if (['Attach', 'Attach Image', 'File', 'Image'].includes(type)) return 'File'
  
  // Supported Inputs
  if (['Data', 'Int', 'Float', 'Currency', 'Date', 'Datetime', 'Time', 'Password', 'Phone', 'EMail', 'Color', 'Barcode', 'Geolocation', 'Duration', 'Rating'].includes(type)) return 'Input'
  
  if (type === 'Heading') return 'Heading'

  // Fallback for unknown types (Signature, etc.) -> Show as Input to verify data presence
  return 'Input' 
})

const inputType = computed(() => {
  const type = props.field.fieldtype
  if (type === 'Date') return 'date'
  if (type === 'Datetime') return 'datetime-local'
  if (type === 'Time') return 'time'
  if (type === 'Password') return 'password'
  if (type === 'Int' || type === 'Float' || type === 'Currency' || type === 'Duration' || type === 'Rating') return 'number'
  if (type === 'Color') return 'color'
  return 'text'
})

const selectOptions = computed(() => {
  if (props.field.fieldtype !== 'Select' || !props.field.options) return []
  // Options string: "Opt1\nOpt2"
  return props.field.options.split('\n').filter(o => o)
})

const linkFilters = computed(() => {
    if (!props.field.link_filters) return null
    try {
        const filters = JSON.parse(props.field.link_filters)
        
        // Helper to process a value
        const processValue = (val) => {
             if (typeof val === 'string' && val.startsWith('eval:')) {
                try {
                    const code = val.substring(5)
                    const fn = new Function('doc', `return ${code}`)
                    return fn(props.doc)
                } catch (e) {
                    console.warn(`Eval failed for filter value ${val}:`, e)
                    return null
                }
            }
            return val
        }

        // Handle Array format (Standard Frappe)
        if (Array.isArray(filters)) {
             // We need to convert Array format to Object format for LinkControl prop?
             // Or LinkControl handles array? 
             // Looking at LinkControl.vue (assumed), it usually takes an object { key: value }.
             // If LinkControl expects Object, we must convert.
             // Standard format: [["DocType", "field", "=", "value"]]
             const processed = {}
             filters.forEach(f => {
                 if (Array.isArray(f) && f.length >= 4) {
                     const field = f[1]
                     const value = f[3]
                     processed[field] = processValue(value)
                 }
             })
             // If empty, maybe it wasn't the standard format?
             // Let's fallback to returning it as is if we can't process, but LinkControl likely needs DB filters.
             return Object.keys(processed).length ? processed : filters
        }
        
        // Handle Object format (User's current usage)
        const processedFilters = {}
        for (const [key, value] of Object.entries(filters)) {
            processedFilters[key] = processValue(value)
        }
        return processedFilters

    } catch (e) {
        console.warn('Invalid link_filters JSON:', props.field.link_filters)
        return null
    }
})


</script>
