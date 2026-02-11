<template>
  <div class="space-y-2">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
        {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Read Only / Preview Mode -->
    <div v-if="modelValue">
        <div v-if="isImage" class="relative group w-32 h-32 bg-gray-100 rounded-lg border border-gray-200 overflow-hidden flex items-center justify-center">
            <img :src="modelValue" class="w-full h-full object-cover" />
            
            <div v-if="!disabled" class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                 <Button variant="ghost" icon="eye" class="text-white hover:bg-white/20" @click="openFile" />
                 <Button variant="ghost" icon="trash-2" class="text-red-400 hover:bg-white/20 hover:text-red-500" @click="clearFile" />
            </div>
        </div>

        <div v-else class="flex items-center gap-2 p-2 bg-gray-50 border border-gray-200 rounded-md max-w-md">
            <FeatherIcon name="file" class="w-4 h-4 text-gray-500" />
            <span class="text-sm text-gray-700 truncate flex-1" :title="modelValue">{{ fileName }}</span>
            <div v-if="!disabled" class="flex items-center gap-1">
                 <Button variant="ghost" icon="external-link" size="sm" @click="openFile" />
                 <Button variant="ghost" icon="trash-2" size="sm" class="text-red-500" @click="clearFile" />
            </div>
            <Button v-else variant="ghost" icon="external-link" size="sm" class="ml-auto" @click="openFile" />
        </div>
    </div>

    <!-- Upload Mode -->
    <div v-else>
        <div v-if="!disabled">
             <input
                ref="fileInput"
                type="file"
                class="hidden"
                @change="handleFileSelect"
            />
            <div 
                @click="triggerUpload"
                class="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-gray-500 hover:border-gray-400 hover:bg-gray-50 transition-colors cursor-pointer text-center group"
            >
                <div class="bg-indigo-50 p-3 rounded-full mb-3 group-hover:bg-indigo-100 transition-colors">
                    <LoadingIndicator v-if="uploading" class="w-6 h-6 text-indigo-600" />
                    <FeatherIcon v-else :name="isImageField ? 'image' : 'upload-cloud'" class="w-6 h-6 text-indigo-500" />
                </div>
                
                <span class="text-sm font-medium text-gray-700">
                    {{ uploading ? 'Yükleniyor...' : (label ? `${label} Seç veya Sürükle` : 'Dosya Seç veya Sürükle') }}
                </span>
                <span v-if="!uploading" class="text-xs text-gray-400 mt-1">Maksimum 10MB {{ isImageField ? '(PNG, JPG, WEBP)' : '' }}</span>
            </div>
            <div v-if="error" class="text-xs text-red-500 mt-1">{{ error }}</div>
        </div>
        <div v-else class="text-sm text-gray-400 italic bg-gray-50 p-2 rounded border border-gray-100">Dosya yok</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const props = defineProps({
  modelValue: String,
  label: String,
  required: Boolean,
  disabled: Boolean,
  doctype: String,
  docname: String,
  fieldname: String,
  isPrivate: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const uploading = ref(false)
const error = ref(null)

const isImageField = computed(() => {
    // Basic heuristic: if label contains 'Resim' or 'Image', treat as image field for UI
    if (props.label && (props.label.toLowerCase().includes('resim') || props.label.toLowerCase().includes('image') || props.label.toLowerCase().includes('foto'))) {
        return true
    }
    return false
})

const isImage = computed(() => {
    if (!props.modelValue) return false
    const ext = props.modelValue.split('.').pop().toLowerCase()
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)
})

const fileName = computed(() => {
    if (!props.modelValue) return ''
    return props.modelValue.split('/').pop()
})

function triggerUpload() {
    if (uploading.value) return
    fileInput.value.click()
}

async function handleFileSelect(event) {
    const file = event.target.files[0]
    if (!file) return

    uploading.value = true
    error.value = null

    const formData = new FormData()
    formData.append('file', file, file.name)
    formData.append('is_private', props.isPrivate ? 1 : 0)
    formData.append('folder', 'Home')
    if (props.doctype && props.docname) {
        formData.append('doctype', props.doctype)
        formData.append('docname', props.docname)
        formData.append('fieldname', props.fieldname)
    }

    try {
        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.csrf_token
            },
            body: formData
        })

        const data = await response.json()
        if (data.message && data.message.file_url) {
            emit('update:modelValue', data.message.file_url)
        } else {
            error.value = 'Dosya yüklenirken hata oluştu.'
            console.error('Upload failed', data)
        }
    } catch (e) {
        error.value = 'Bağlantı hatası.'
        console.error('Upload error', e)
    } finally {
        uploading.value = false
        // Reset input
        if (fileInput.value) fileInput.value.value = ''
    }
}

function clearFile() {
    emit('update:modelValue', null)
}

function openFile() {
    if (props.modelValue) {
        window.open(props.modelValue, '_blank')
    }
}
</script>
