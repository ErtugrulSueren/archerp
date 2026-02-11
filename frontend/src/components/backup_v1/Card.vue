<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-slate-200/60">
    
    <!-- Optional Header -->
    <div v-if="$slots.header || title" class="px-6 py-5 border-b border-slate-50 flex items-center justify-between">
       <div class="flex items-center gap-3">
           <slot name="header">
               <h3 v-if="title" class="text-lg font-bold text-slate-800">{{ title }}</h3>
               <p v-if="subtitle" class="text-sm text-slate-500 font-medium">{{ subtitle }}</p>
           </slot>
       </div>
       <div v-if="$slots.actions">
           <slot name="actions"></slot>
       </div>
    </div>

    <!-- Body -->
    <div class="px-6 py-6">
      <slot></slot>
    </div>

    <!-- Optional Footer -->
    <div v-if="$slots.footer" class="px-6 py-4 bg-slate-50/50 border-t border-slate-50">
        <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  subtitle: String,
})
</script>
