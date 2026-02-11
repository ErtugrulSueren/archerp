<template>
  <div class="flex gap-3 group">
    <!-- Avatar / Icon -->
    <div class="flex-shrink-0 mt-1">
         <div v-if="item.owner" class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-100 to-purple-100 border border-white shadow-sm flex items-center justify-center text-xs font-bold text-indigo-700">
             {{ getInitials(item.owner) }}
         </div>
         <div v-else class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400">
             <FeatherIcon name="activity" class="w-4 h-4" />
         </div>
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-0.5">
            <span class="text-sm font-semibold text-gray-900 truncate">{{ item.owner || 'Sistem' }}</span>
            <span class="text-xs text-gray-400">{{ formatTime(item.creation) }}</span>
        </div>
        
        <!-- Comment Bubble -->
        <div v-if="item.communication_type === 'Comment'" class="group/bubble relative">
            <div v-if="!isEditing" class="relative bg-gray-50/80 p-3 rounded-r-xl rounded-bl-xl border border-gray-100 text-sm text-gray-700 leading-relaxed shadow-sm transition-all duration-200">
                <div v-html="item.content"></div>
                
                <!-- Actions (Always visible for debugging/usability) -->
                <div class="absolute -top-3 -right-2 flex gap-1 bg-white shadow-sm border border-gray-100 rounded-md p-0.5 z-10">
                    <button class="p-1 hover:bg-gray-50 rounded text-gray-400 hover:text-indigo-600" title="Düzenle" @click.stop="startEdit">
                        <FeatherIcon name="edit-2" class="w-3 h-3" />
                    </button>
                    <button class="p-1 hover:bg-gray-50 rounded text-gray-400 hover:text-red-600" title="Sil" @click.stop="handleDelete">
                        <FeatherIcon name="trash-2" class="w-3 h-3" />
                    </button>
                </div>
            </div>

            <!-- Inline Editing -->
            <div v-else class="bg-white p-2 rounded-xl border border-indigo-200 shadow-sm ring-2 ring-indigo-50">
                <textarea 
                    v-model="editContent" 
                    rows="2" 
                    class="block w-full text-sm border-0 focus:ring-0 resize-none bg-transparent p-0"
                    ref="editInput"
                ></textarea>
                <div class="flex justify-end gap-2 mt-2">
                    <button class="text-xs text-gray-500 hover:text-gray-700 font-medium px-2 py-1" @click="cancelEdit">İptal</button>
                    <button class="text-xs bg-indigo-600 text-white px-3 py-1 rounded-md font-medium hover:bg-indigo-700" @click="saveEdit">Kaydet</button>
                </div>
            </div>
        </div>

        <!-- System Action -->
        <div v-else class="text-sm text-gray-500">
            <span v-if="item.content" v-html="item.content"></span>
            <span v-else>
                {{ item.subject || 'Bir işlem yaptı' }}
            </span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
    item: { type: Object, required: true }
})

const emit = defineEmits(['delete', 'update'])

const isEditing = ref(false)
const editContent = ref('')
const editInput = ref(null)

function startEdit() {
    editContent.value = props.item.content
    isEditing.value = true
    nextTick(() => {
        editInput.value?.focus()
    })
}

function cancelEdit() {
    isEditing.value = false
    editContent.value = ''
}

function handleDelete() {
    emit('delete', props.item)
}

function saveEdit() {
    if (editContent.value.trim() !== props.item.content) {
        emit('update', props.item, editContent.value)
    }
    isEditing.value = false
}
function getInitials(name) {
    if (!name) return 'S'
    // If email
    if (name.includes('@')) name = name.split('@')[0]
    return name.substring(0, 2).toUpperCase()
}

function formatTime(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diff = (now - date) / 1000 // seconds

    if (diff < 60) return 'Az önce'
    if (diff < 3600) return `${Math.floor(diff / 60)}dk`
    if (diff < 86400) return `${Math.floor(diff / 3600)}s`
    
    return date.toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' })
}
</script>
