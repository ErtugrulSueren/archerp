import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'

// Global shared state
const modules = ref([])
const loading = ref(false)
const error = ref(null)
const expanded = ref([])
const expandedGroups = ref([])
const initialized = ref(false)
const isSidebarCollapsed = ref(false)
const isMobileOpen = ref(false)
const activeModule = ref(null) // Contextual Sidebar state

// Shared promise so multiple callers can await the same fetch
let _fetchPromise = null

export function useSidebar() {

    const fetchMenu = () => {
        // If already fetching, return the existing promise so callers can await it
        if (_fetchPromise) return _fetchPromise

        _fetchPromise = _doFetchMenu()
        return _fetchPromise
    }

    async function _doFetchMenu() {
        loading.value = true
        error.value = null

        try {
            const data = await call('archerp.archerp.api.get_sidebar_menu')
            modules.value = data || []
        } catch (e) {
            error.value = e
            console.error('Sidebar menü yüklenemedi:', e)
            modules.value = []
        } finally {
            loading.value = false
            _fetchPromise = null
        }
    }

    const toggleModule = (moduleName) => {
        if (isSidebarCollapsed.value) {
            isSidebarCollapsed.value = false
            expanded.value = [moduleName]
            return
        }

        if (expanded.value.includes(moduleName)) {
            expanded.value = []
        } else {
            expanded.value = [moduleName]
        }
    }

    const toggleGroup = (moduleName, groupName) => {
        const key = `${moduleName}::${groupName}`
        const index = expandedGroups.value.indexOf(key)

        if (index > -1) {
            expandedGroups.value.splice(index, 1)
        } else {
            const otherModuleGroups = expandedGroups.value.filter(k => !k.startsWith(`${moduleName}::`))
            expandedGroups.value = [...otherModuleGroups, key]
        }
    }

    const toggleSidebar = () => {
        isSidebarCollapsed.value = !isSidebarCollapsed.value
    }

    const toggleMobileSidebar = () => {
        isMobileOpen.value = !isMobileOpen.value
    }

    const closeMobileSidebar = () => {
        isMobileOpen.value = false
    }

    // Contextual Sidebar Logic
    const setActiveModule = (moduleName) => {
        if (!moduleName) {
            activeModule.value = null
            return
        }

        const mod = modules.value.find(m => m.name === moduleName || m.modul_adi === moduleName)
        if (mod) {
            activeModule.value = mod
            expanded.value = [mod.name]
        }
    }

    // Helper: check if a menu item's route matches the current path
    function checkPathMatch(item, path) {
        let itemRoute = ''
        if (item.hedef_rota) {
            // Strip query params — hedef_rota may contain ?key=value
            const qIdx = item.hedef_rota.indexOf('?')
            itemRoute = qIdx !== -1 ? item.hedef_rota.substring(0, qIdx) : item.hedef_rota
        }
        else if (item.ilgili_doctype) itemRoute = '/auto/' + item.ilgili_doctype
        else if (item.ilgili_rapor) itemRoute = '/report/' + item.ilgili_rapor

        if (!itemRoute) return false

        // Normalize both sides: decode URI components for consistent comparison
        const decodedPath = decodeURIComponent(path)
        const decodedRoute = decodeURIComponent(itemRoute)

        return decodedPath === decodedRoute || decodedPath.startsWith(decodedRoute + '/')
    }

    // Resolve which module should be active based on the current route path
    // moduleHint comes from route.query.module — used to disambiguate when
    // the same doctype exists in multiple modules
    function resolveActiveModule(path, moduleHint) {
        // Workspace or root => no sidebar
        if (!path || path === '/' || path === '/workspace' || path.startsWith('/workspace')) {
            activeModule.value = null
            return
        }

        // Need modules data to resolve
        if (!modules.value.length) return

        // 1) If a module hint is provided, verify the doctype actually belongs
        //    to that module and activate it. This prevents URL tampering from
        //    showing a module the user shouldn't see — if the doctype isn't
        //    in the hinted module, we fall through to normal resolution.
        if (moduleHint) {
            const hintedMod = modules.value.find(
                m => m.name === moduleHint || m.modul_adi === moduleHint
            )
            if (hintedMod) {
                const found = _moduleContainsPath(hintedMod, path)
                if (found) {
                    setActiveModule(hintedMod.name)
                    return
                }
            }
        }

        // 2) Fallback: scan all modules for first match (original behaviour)
        for (const mod of modules.value) {
            if (_moduleContainsPath(mod, path)) {
                setActiveModule(mod.name)
                return
            }
        }
    }

    // Helper: check whether any item in a module matches the given path
    function _moduleContainsPath(mod, path) {
        if (mod.grouped_items) {
            for (const group in mod.grouped_items) {
                for (const item of mod.grouped_items[group]) {
                    if (checkPathMatch(item, path)) return true
                }
            }
        }
        if (mod.items) {
            for (const item of mod.items) {
                if (checkPathMatch(item, path)) return true
            }
        }
        return false
    }

    const isExpanded = (moduleName) => expanded.value.includes(moduleName)
    const isGroupExpanded = (moduleName, groupName) => expandedGroups.value.includes(`${moduleName}::${groupName}`)

    onMounted(() => {
        if (modules.value.length === 0 && !_fetchPromise) {
            fetchMenu()
        }
    })

    return {
        modules,
        loading,
        error,
        expanded,
        expandedGroups,
        isSidebarCollapsed,
        isMobileOpen,
        activeModule,
        fetchMenu,
        toggleModule,
        toggleGroup,
        isExpanded,
        isGroupExpanded,
        toggleSidebar,
        toggleMobileSidebar,
        closeMobileSidebar,
        setActiveModule,
        resolveActiveModule
    }
}
