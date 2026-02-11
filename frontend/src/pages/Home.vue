<template>
  <div class="space-y-8">
      
      <!-- Welcome Section -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
           <h2 class="text-3xl font-bold text-slate-900 tracking-tight">Hoşgeldin, {{ sessionUser }} 👋</h2>
           <p class="text-slate-500 mt-1 text-lg">Bugün neler yapmak istersiniz?</p>
        </div>
        <div class="flex gap-3">
             <Button variant="outline">{{ currentDate }}</Button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card class="p-6">
              <h3 class="text-lg font-medium text-gray-500">Toplam Satış</h3>
              <p class="text-3xl font-bold text-primary-600 mt-2">₺124,500</p>
          </Card>
          <Card class="p-6">
              <h3 class="text-lg font-medium text-gray-500">Bekleyen Siparişler</h3>
              <p class="text-3xl font-bold text-orange-600 mt-2">12</p>
          </Card>
          <Card class="p-6">
              <h3 class="text-lg font-medium text-gray-500">Toplam Müşteri</h3>
              <p class="text-3xl font-bold text-green-600 mt-2">48</p>
          </Card>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'

const user = ref('Kullanıcı')

const sessionUser = computed(() => user.value)

const currentDate = computed(() => {
    return new Date().toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

onMounted(async () => {
    try {
        const u = await call('frappe.auth.get_logged_user')
        user.value = u
    } catch (e) {
        console.error(e)
    }
})
</script>
