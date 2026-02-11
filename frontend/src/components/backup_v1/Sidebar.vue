<template>
  <div 
    class="bg-[#0f172a] text-white flex flex-col shadow-2xl transition-all duration-300 overflow-hidden border-r border-slate-800 relative"
    :class="[isCollapsed ? 'w-0 opacity-0' : 'w-72 opacity-100']"
  > 
    <!-- Ambient Glow (Optional subtle effect) -->
    <div class="absolute top-0 left-0 w-full h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2"></div>

    <!-- Logo Area -->
    <div class="h-24 flex items-center px-8 border-b border-slate-800/60 min-w-[18rem] relative z-10">
      <div class="flex items-center gap-3.5 group cursor-pointer" @click="$router.push('/')">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center font-bold text-xl text-white shadow-lg shadow-blue-500/25 ring-1 ring-white/10 group-hover:scale-105 transition-transform duration-300">
            A
        </div>
        <div class="flex flex-col">
            <h1 class="text-xl font-bold tracking-tight text-white leading-none group-hover:text-blue-400 transition-colors">Arch ERP</h1>
            <span class="text-[0.65rem] font-medium text-slate-500 uppercase tracking-widest mt-1">Enterprise</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center text-slate-500 min-w-[18rem]">
      <div class="animate-spin h-6 w-6 border-2 border-slate-700 border-t-blue-500 rounded-full mb-3"></div>
      <span class="text-sm font-medium">Yükleniyor...</span>
    </div>

    <!-- Sidebar Menu -->
    <nav v-else class="flex-1 px-4 py-8 space-y-2 overflow-y-auto min-w-[18rem] custom-scrollbar relative z-10">
      
      <!-- Static Home Link -->
      <router-link
        to="/"
        class="flex items-center gap-3.5 px-4 py-3.5 text-lg font-medium rounded-xl transition-all duration-300 group"
        :class="[
          $route.path === '/'
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 ring-1 ring-white/10'
            : 'text-slate-400 hover:bg-white/5 hover:text-white',
        ]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="transition-transform duration-300 group-hover:scale-110"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span class="tracking-wide">Ana Sayfa</span>
      </router-link>

      <div class="pt-2">
          <div class="px-4 text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Modüller</div>
      </div>

      <!-- Dynamic Modules -->
      <div v-for="modul in menuTree" :key="modul.name" class="space-y-1">
        
        <!-- Module Header (Accordion Trigger) -->
        <button 
          @click="toggleModule(modul.name)"
          class="w-full flex items-center justify-between px-4 py-3.5 text-lg font-medium transition-all duration-300 rounded-xl group relative overflow-hidden"
          :class="[
            expandedModule === modul.name 
              ? 'bg-gradient-to-r from-slate-800 to-transparent text-white shadow-md shadow-black/20' 
              : 'text-slate-400 hover:bg-white/5 hover:text-white'
          ]"
        >
          <!-- Active Indicator Line -->
          <div v-if="expandedModule === modul.name" class="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-1 bg-blue-500 rounded-r-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>

          <span class="flex items-center gap-3.5 z-10 group-hover:translate-x-1 transition-transform duration-300">
             <!-- Generic Module Icon -->
             <div class="p-1 rounded-lg transition-colors" 
                  :class="expandedModule === modul.name ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800/50 text-slate-500 group-hover:text-slate-300'"
                  v-html="getIcon(modul.ikon)">
             </div>
             {{ modul.modul_adi }}
          </span>
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
            class="transition-transform duration-300 opacity-40 group-hover:opacity-100"
            :class="{ 'rotate-180 text-white': expandedModule === modul.name }"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>

        <!-- Module Content -->
        <div 
          class="grid transition-[grid-template-rows] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]"
          :class="expandedModule === modul.name ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
        >
          <div class="overflow-hidden">
            <div class="pl-4 space-y-4 py-3 relative">
              <!-- Connector Line -->
              <div class="absolute left-[1.65rem] top-0 bottom-0 w-px bg-gradient-to-b from-slate-800 via-slate-800 to-transparent"></div>

              <!-- Groups -->
              <div v-for="(groupItems, groupName) in modul.groups" :key="groupName" class="pt-1 relative">
                
                <!-- Group Header -->
                <button 
                  v-if="groupName !== 'Genel'"
                  @click="toggleGroup(modul.name, groupName)"
                  class="w-full flex items-center justify-between px-3 py-1.5 text-base font-bold text-slate-500 uppercase tracking-wider hover:text-blue-400 transition-colors pl-6 group/grouphead"
                >
                  <span class="group-hover/grouphead:translate-x-1 transition-transform duration-200">{{ groupName }}</span>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    width="12" 
                    height="12" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="2" 
                    stroke-linecap="round" 
                    stroke-linejoin="round"
                    class="transition-transform duration-300 opacity-0 group-hover/grouphead:opacity-100"
                    :class="{ 'rotate-180': isGroupExpanded(modul.name, groupName) }"
                  >
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </button>

                <!-- Group Links -->
                <div 
                    class="grid transition-[grid-template-rows] duration-300 ease-in-out"
                    :class="(groupName === 'Genel' || isGroupExpanded(modul.name, groupName)) ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
                >
                  <div class="overflow-hidden">
                    <div class="space-y-1 mt-1 pl-4">
                      <router-link
                        v-for="item in groupItems"
                        :key="item.name"
                        :to="resolveRoute(item)"
                        class="flex items-center gap-3 px-3 py-2 text-lg font-medium rounded-lg transition-all duration-200 border border-transparent group/link relative"
                        :class="[
                          $route.path === resolveRoute(item)
                            ? 'text-white bg-blue-600/10 border-blue-600/20'
                            : 'text-slate-400 hover:text-blue-200 hover:bg-white/5',
                        ]"
                      >
                         <span class="w-1.5 h-1.5 rounded-full transition-all duration-300 shadow-[0_0_8px_rgba(59,130,246,0.5)]" 
                               :class="$route.path === resolveRoute(item) ? 'bg-blue-400 scale-125' : 'bg-slate-700 group-hover/link:bg-blue-400 group-hover/link:scale-110'">
                         </span>
                         <span class="group-hover/link:translate-x-1 transition-transform duration-200">{{ item.etiket }}</span>
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

    </nav>

    <!-- Footer -->
    <div class="p-4 border-t border-slate-800 min-w-[18rem] bg-slate-950/30">
        <div class="flex items-center gap-3 p-3 rounded-xl bg-slate-900 border border-slate-800/50 hover:border-slate-700 transition-colors group cursor-pointer">
            <div class="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shadow-lg">ER</div>
            <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-white truncate">Ertuğrul</div>
                <div class="text-xs text-slate-500 truncate">Yönetici</div>
            </div>
            <button @click="logout" class="p-1.5 rounded-lg hover:bg-red-500/10 hover:text-red-400 text-slate-500 transition-colors" title="Çıkış Yap">
                <div v-html="getIcon('log-out', 16)"></div>
            </button>
        </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import feather from 'feather-icons'
import { useRouter } from 'vue-router'

const router = useRouter()

defineProps({
  isCollapsed: {
    type: Boolean,
    default: false
  }
})

const loading = ref(true)
const menuTree = ref([]) // Stores processed modules
const expandedModule = ref(null) // String: Single currently open module name
const expandedGroups = ref({}) // Object map: { 'ModuleName': ['GroupName1', 'GroupName2'] }

function getIcon(name, size = 18) {
    if (name && feather.icons[name]) {
        return feather.icons[name].toSvg({ 
            width: size, 
            height: size, 
            'stroke-width': 2 
        })
    }
    // Fallback icon (box)
    return feather.icons['box'].toSvg({ 
        width: size, 
        height: size, 
        'stroke-width': 2 
    })
}

function isGroupExpanded(moduleName, groupName) {
    return expandedGroups.value[moduleName]?.includes(groupName)
}

function toggleModule(moduleName) {
    if (expandedModule.value === moduleName) {
        expandedModule.value = null // Close if already open
    } else {
        expandedModule.value = moduleName // Open new and auto-close others
    }
}

function toggleGroup(moduleName, groupName) {
    if (!expandedGroups.value[moduleName]) {
        expandedGroups.value[moduleName] = []
    }
    
    const groups = expandedGroups.value[moduleName]
    if (groups.includes(groupName)) {
        expandedGroups.value[moduleName] = groups.filter(n => n !== groupName)
    } else {
        expandedGroups.value[moduleName].push(groupName)
    }
}

// Fetch Modules and build Tree
async function fetchMenuData() {
    loading.value = true
    try {
        // 1. Fetch Modules
        const modules = await frappeRequest({
            url: 'frappe.client.get_list',
            params: {
                doctype: 'Arch Module',
                fields: ['name', 'modul_adi', 'ikon', 'siralama'],
                filters: { aktif: 1 },
                order_by: 'siralama asc'
            }
        })

        // 2. Fetch Details for each module (to get child table items)
        const promises = modules.map(m => frappeRequest({
            url: 'frappe.client.get',
            params: { doctype: 'Arch Module', name: m.name }
        }))
        
        const fullModules = await Promise.all(promises)

        // 3. Process Data
        menuTree.value = fullModules.map(modul => {
            const items = modul.menu_ogeleri || []
            const groups = {}

            items.forEach(item => {
                if (!item.aktif) return
                
                const groupName = item.ust_baslik || 'Genel'
                if (!groups[groupName]) {
                    groups[groupName] = []
                }
                groups[groupName].push(item)
            })

            return {
                ...modul,
                groups
            }
        })
        
    } catch (e) {
        console.error("Failed to fetch menu:", e)
    } finally {
        loading.value = false
    }
}

function resolveRoute(item) {
    if (item.hedef_rota) return item.hedef_rota
    if (item.ilgili_doctype) return `/auto/${item.ilgili_doctype}`
    return '/' 
}

async function logout() {
  try {
    await frappeRequest({
      url: '/api/method/logout',
      method: 'POST',
    })
    // Redirect to SPA Login page accurately
    window.location.href = router.resolve({ name: 'Login' }).href
  } catch (error) {
    console.error('Logout error:', error)
    window.location.href = router.resolve({ name: 'Login' }).href
  }
}


onMounted(() => {
    if (window.csrf_token && window.csrf_token.includes('{{')) {
        window.csrf_token = null;
    }
    fetchMenuData()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.1);
}
</style>
