import { ref, reactive, readonly } from 'vue'
import { call } from 'frappe-ui'

// Singleton state
const defaults = reactive({})
const fields = ref([])
const isLoaded = ref(false)
const isLoading = ref(false)

export function useSessionDefaults() {

    // Load defaults from Frappe using official API
    async function loadDefaults() {
        if (isLoading.value) return

        isLoading.value = true
        try {
            // Use Frappe's official session default API
            const result = await call('frappe.core.doctype.session_default_settings.session_default_settings.get_session_default_values')

            if (result) {
                const parsedFields = JSON.parse(result)
                fields.value = parsedFields

                // Build defaults from fields
                parsedFields.forEach(field => {
                    defaults[field.fieldname] = field.default || ''
                })
            }

            isLoaded.value = true
        } catch (e) {
            console.error('Failed to load session defaults:', e)
        } finally {
            isLoading.value = false
        }
    }

    // Set a default value using Frappe's official API
    async function setDefault(fieldname, value) {
        try {
            await call('frappe.core.doctype.session_default_settings.session_default_settings.set_session_default_values', {
                default_values: JSON.stringify({ [fieldname]: value || '' })
            })

            defaults[fieldname] = value || ''
        } catch (e) {
            console.error(`Failed to set default for ${fieldname}:`, e)
            throw e
        }
    }

    // Set multiple defaults at once
    async function setDefaults(values) {
        try {
            await call('frappe.core.doctype.session_default_settings.session_default_settings.set_session_default_values', {
                default_values: JSON.stringify(values)
            })

            Object.entries(values).forEach(([key, value]) => {
                defaults[key] = value || ''
            })
        } catch (e) {
            console.error('Failed to set defaults:', e)
            throw e
        }
    }

    // Clear all defaults
    async function clearAllDefaults() {
        const clearValues = {}
        fields.value.forEach(field => {
            clearValues[field.fieldname] = ''
        })

        await setDefaults(clearValues)
    }

    // Get a single default
    function getDefault(fieldname) {
        return defaults[fieldname] || ''
    }

    // Check if a field has a session default
    function hasDefault(fieldname) {
        return !!defaults[fieldname]
    }

    // Get count of active defaults
    function getActiveDefaultsCount() {
        return Object.values(defaults).filter(v => v).length
    }

    // Get session default fields configuration
    function getSessionDefaultFields() {
        const result = {}
        fields.value.forEach(field => {
            result[field.fieldname] = {
                label: field.label,
                doctype: field.options,
                fieldname: field.fieldname
            }
        })
        return result
    }

    return {
        defaults: readonly(defaults),
        fields: readonly(fields),
        isLoaded: readonly(isLoaded),
        isLoading: readonly(isLoading),
        loadDefaults,
        setDefault,
        setDefaults,
        clearAllDefaults,
        getDefault,
        hasDefault,
        getActiveDefaultsCount,
        getSessionDefaultFields
    }
}
