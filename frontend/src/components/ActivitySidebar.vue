<template>
  <div class="flex flex-col h-full bg-white/50 backdrop-blur-xl border-l border-white/20 shadow-[-10px_0_30px_-5px_rgba(0,0,0,0.03)] w-[350px] min-w-[320px] transition-all duration-300">
      
      <!-- Header -->
      <div class="px-5 py-4 border-b border-gray-100/50 flex items-center justify-between bg-white/40">
          <h3 class="font-bold text-gray-800 flex items-center gap-2">
              <div class="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg">
                  <FeatherIcon name="activity" class="w-4 h-4" />
              </div>
              Aktivite & Yorumlar
          </h3>
          <div class="text-xs font-semibold px-2 py-0.5 rounded-md bg-gray-100 text-gray-500">
              {{ activities.length }}
          </div>
      </div>
      
      <div v-if="!loading && !trackChangesEnabled" class="mx-4 mt-4 p-3 bg-orange-50 border border-orange-100 rounded-lg flex items-start gap-2">
          <FeatherIcon name="alert-circle" class="w-4 h-4 text-orange-500 mt-0.5" />
          <div class="text-xs text-orange-700">
              Bu belge türü için <b>Değişiklik Takibi</b> (Track Changes) kapalı. Düzenlemeler kaydedilmiyor.
          </div>
      </div>

      <!-- Add Comment Area -->
      <div class="p-4 bg-gradient-to-b from-white/60 to-transparent">
          <CommentInput @submit="addComment" />
      </div>

      <!-- Timeline Scroll Area -->
      <div class="flex-1 overflow-y-auto custom-scrollbar px-4 pb-20 space-y-6">
          
          <div v-if="loading" class="space-y-4 pt-4">
               <div v-for="i in 3" :key="i" class="flex gap-3">
                   <div class="w-8 h-8 rounded-full bg-gray-200 animate-pulse"></div>
                   <div class="flex-1 space-y-2">
                       <div class="h-3 w-24 bg-gray-200 rounded animate-pulse"></div>
                       <div class="h-16 w-full bg-gray-100 rounded-xl animate-pulse"></div>
                   </div>
               </div>
          </div>

          <div v-else-if="activities.length === 0" class="text-center py-10">
              <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
                   <FeatherIcon name="message-square" class="w-5 h-5 text-gray-300" />
              </div>
              <p class="text-sm text-gray-400">Henüz bir aktivite yok.</p>
          </div>

          <template v-else>
               <!-- Timeline Connector Line -->
               <div class="relative">
                   <div class="absolute left-[15px] top-6 bottom-6 w-0.5 bg-gray-100 -z-10"></div>
                   
                   <div v-for="item in activities" :key="item.name" class="relative">
                        <TimelineItem 
                            :item="item" 
                            @delete="deleteActivity"
                            @update="updateActivity"
                        />
                   </div>
               </div>
          </template>

      </div>

      <!-- Delete Confirmation Dialog -->
      <Dialog
        v-model="showDeleteDialog"
        title="Yorumu Sil"
      >
        <p class="text-sm text-gray-600">
            Bu yorumu kalıcı olarak silmek istediğinize emin misiniz? Bu işlem geri alınamaz.
        </p>
        <template #actions>
            <Button
                variant="subtle"
                label="İptal"
                @click="showDeleteDialog = false"
            />
            <Button
                variant="solid"
                theme="red"
                label="Sil"
                :loading="deleteLoading"
                @click="confirmDelete"
            />
        </template>
      </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { call, FeatherIcon, Button } from 'frappe-ui'
import TimelineItem from './TimelineItem.vue'
import CommentInput from './CommentInput.vue'
import Dialog from './Dialog.vue'
import { useToast } from '../composables/useToast'

const props = defineProps({
    doctype: String,
    docname: String
})

// State
const activities = ref([])
const loading = ref(false)
const trackChangesEnabled = ref(true)

// Dialog State
const showDeleteDialog = ref(false)
const itemToDelete = ref(null)
const deleteLoading = ref(false)

const toast = useToast()

async function fetchActivities() {
    if (!props.docname || props.docname === 'new') return
    loading.value = true
    try {
        // 1. Fetch Basic Doc Details (For Creation Log)
        const docDetailsPromise = call('frappe.client.get_value', {
            doctype: props.doctype,
            filters: { name: props.docname },
            fieldname: ['creation', 'owner']
        })

        // 2. Fetch DocType Meta (To check Track Changes)
        const metaPromise = call('frappe.client.get', {
            doctype: 'DocType',
            name: props.doctype
        })

        // 3. Fetch Comments
        const commentsReq = call('frappe.client.get_list', {
            doctype: 'Comment',
            filters: {
                reference_doctype: props.doctype,
                reference_name: props.docname
            },
            fields: ['name', 'content', 'owner', 'creation', 'comment_type', 'subject'],
            order_by: 'creation desc',
            limit: 50
        })

        // 4. Fetch Versions
        const versionsReq = call('frappe.client.get_list', {
            doctype: 'Version',
            filters: {
                ref_doctype: props.doctype,
                docname: props.docname
            },
            fields: ['name', 'owner', 'creation', 'data'],
            order_by: 'creation desc',
            limit: 50
        })

        const [docDetails, docMeta, comments, versions] = await Promise.all([
            docDetailsPromise, 
            metaPromise, 
            commentsReq, 
            versionsReq
        ])

        // Check Track Changes
        if (docMeta) {
            trackChangesEnabled.value = !!docMeta.track_changes
        }

        // Process Comments
        const processedComments = (comments || []).map(c => ({
            ...c,
            communication_type: 'Comment',
            timestamp: new Date(c.creation).getTime()
        }))

        // Process Versions
        const processedVersions = (versions || []).map(v => {
            return {
                ...v,
                communication_type: 'Version',
                content: formatVersionContent(v.data),
                timestamp: new Date(v.creation).getTime()
            }
        })
        
        let allActivities = [...processedComments, ...processedVersions]

        // ALWAYS Add "Created" Log
        if (docDetails && docDetails.creation) {
            const creationTime = new Date(docDetails.creation).getTime()
            // Avoid duplicate if a comment/log already exists with exact same time and content
            // (Unlikely but good to be safe)
            allActivities.push({
                name: `created-${props.docname}`,
                owner: docDetails.owner,
                creation: docDetails.creation,
                content: 'Oluşturdu',
                communication_type: 'System', 
                timestamp: creationTime,
                is_creation: true
            })
        }

        activities.value = allActivities.sort((a, b) => b.timestamp - a.timestamp)

    } catch (e) {
        console.warn('Activity fetch failed', e)
    } finally {
        loading.value = false
    }
}

function formatVersionContent(dataStr) {
    if (!dataStr) return 'Bir değişiklik yaptı'
    try {
        const data = typeof dataStr === 'string' ? JSON.parse(dataStr) : dataStr
        
        if (data.changed && data.changed.length > 0) {
            return data.changed.map(change => {
                const field = change[0]
                const oldVal = change[1]
                const newVal = change[2]
                return `<span class="font-medium text-gray-900">${field}</span>: <span class="line-through text-gray-400">${oldVal || 'boş'}</span> &rarr; <span class="font-medium text-gray-900">${newVal}</span>`
            }).join('<br>')
        }
        if (data.row_changed && data.row_changed.length > 0) {
             return 'Tablo satırlarında değişiklik yaptı'
        }
        if (data.added && data.added.length > 0) {
             return 'Yeni kayıtlar ekledi'
        }
        if (data.removed && data.removed.length > 0) {
             return 'Kayıtları sildi'
        }
        return 'Bir güncelleme yaptı'
    } catch (e) {
        return 'Bir değişiklik yaptı'
    }
}

async function addComment(content) {
    try {
        await call('frappe.desk.form.utils.add_comment', {
            reference_doctype: props.doctype,
            reference_name: props.docname,
            content: content,
            comment_email: 'Administrator', // Fallback or current user
            comment_by: 'Administrator'
        })
        toast.success('Yorum eklendi', 'Başarılı')
        await fetchActivities()
    } catch (e) {
        console.error(e)
        // Adjust error message handling if e is object
        const msg = e.message || (typeof e === 'string' ? e : 'Yorum eklenirken hata oluştu')
        toast.error(msg, 'Hata')
    }
}

function deleteActivity(item) {
    if (!item || !item.name) return
    itemToDelete.value = item
    showDeleteDialog.value = true
}

async function confirmDelete() {
    if (!itemToDelete.value) return
    deleteLoading.value = true
    try {
        await call('frappe.client.delete', {
            doctype: 'Comment',
            name: itemToDelete.value.name
        })
        toast.success('Yorum silindi', 'Başarılı')
        await fetchActivities()
        showDeleteDialog.value = false
    } catch (e) {
        console.error('Delete failed', e)
        const msg = e.message || (typeof e === 'string' ? e : 'Silme işlemi başarısız')
        toast.error(msg, 'Hata')
    } finally {
        deleteLoading.value = false
        itemToDelete.value = null
    }
}

async function updateActivity(item, newContent) {
    if (!item || !item.name) return
    try {
        await call('frappe.desk.form.utils.update_comment', {
            name: item.name,
            content: newContent
        })
        toast.success('Yorum güncellendi', 'Başarılı')
        await fetchActivities()
    } catch (e) {
        console.error('Update failed', e)
        const msg = e.message || (typeof e === 'string' ? e : 'Güncelleme başarısız')
        toast.error(msg, 'Hata')
    }
}

watch(() => props.docname, fetchActivities, { immediate: true })

</script>
