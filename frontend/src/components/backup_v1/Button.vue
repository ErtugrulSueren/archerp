<template>
  <button
    :class="[
      'inline-flex items-center justify-center gap-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
      sizeClasses,
      variantClasses,
      roundedClasses
    ]"
    :disabled="loading || disabled"
    v-bind="$attrs"
  >
    <svg v-if="loading" class="animate-spin -ml-1 h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span v-if="iconLeft" class="flex items-center">
        <!-- We can use Feather icons simply by name if we had a resolver, but for now we expect svg or handle dynamically. 
             Since simple icon passing is tricky without a lib, let's assume specific icons or slots. 
             Ideally use slots for icons. For compatibility with Frappe UI props, we support a basic slot logic. -->
        <component :is="iconLeft" v-if="typeof iconLeft === 'object'" class="w-5 h-5" />
    </span>
    <slot></slot>
    <span v-if="iconRight" class="flex items-center">
         <component :is="iconRight" v-if="typeof iconRight === 'object'" class="w-5 h-5" />
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'solid', // solid, subtle, outline, ghost
  },
  theme: {
    type: String,
    default: 'blue', // blue, gray, red, green
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg, xl
  },
  loading: Boolean,
  disabled: Boolean,
  iconLeft: [Object, String],
  iconRight: [Object, String],
})

const sizeClasses = computed(() => {
    switch (props.size) {
        case 'sm': return 'px-3 py-1.5 text-sm';
        case 'lg': return 'px-6 py-3 text-lg';
        case 'xl': return 'px-8 py-4 text-xl';
        default: return 'px-5 py-2.5 text-base'; // md
    }
})

const roundedClasses = computed(() => 'rounded-xl') // Modern large rounded corners

const variantClasses = computed(() => {
    const t = props.theme
    
    // Style Definitions
    const styles = {
        solid: {
            blue: 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-600/20 border border-transparent',
            gray: 'bg-slate-800 text-white hover:bg-slate-700 shadow-lg shadow-slate-800/20 border border-transparent',
            red: 'bg-red-600 text-white hover:bg-red-700 shadow-lg shadow-red-600/20 border border-transparent',
            green: 'bg-green-600 text-white hover:bg-green-700 shadow-lg shadow-green-600/20 border border-transparent',
        },
        subtle: {
             blue: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-transparent',
             gray: 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-transparent',
             red: 'bg-red-50 text-red-700 hover:bg-red-100 border border-transparent',
             green: 'bg-green-50 text-green-700 hover:bg-green-100 border border-transparent',
        },
        outline: {
             blue: 'bg-transparent text-blue-600 border-2 border-blue-200 hover:border-blue-600',
             gray: 'bg-transparent text-slate-600 border-2 border-slate-200 hover:border-slate-600',
             red: 'bg-transparent text-red-600 border-2 border-red-200 hover:border-red-600',
             green: 'bg-transparent text-green-600 border-2 border-green-200 hover:border-green-600',
        },
        ghost: {
             blue: 'bg-transparent text-blue-600 hover:bg-blue-50',
             gray: 'bg-transparent text-slate-600 hover:bg-slate-100',
             red: 'bg-transparent text-red-600 hover:bg-red-50',
             green: 'bg-transparent text-green-600 hover:bg-green-50',
        }
    }

    return styles[props.variant]?.[t] || styles.solid.blue
})
</script>
