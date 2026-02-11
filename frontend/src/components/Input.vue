<template>
  <div :class="['relative', className]">
    <div class="relative group">
      <!-- Input element -->
      <input
        :id="id"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        placeholder=" " 
        :disabled="disabled"
        class="block px-4 pb-2.5 pt-5 w-full text-base text-gray-900 bg-gray-50/50 border border-gray-200 rounded-xl appearance-none focus:outline-none focus:ring-0 focus:border-indigo-600 peer transition-all duration-200"
        :class="[
            iconLeft ? 'pl-11' : '',
            disabled ? 'bg-gray-100 cursor-not-allowed opacity-75' : 'hover:bg-gray-100/50',
            error ? 'border-red-300 focus:border-red-500 bg-red-50/10' : ''
        ]"
        @input="$emit('update:modelValue', $event.target.value)"
        @focus="handleFocus"
        @blur="handleBlur"
        v-bind="$attrs"
      />

       <!-- Prefix icon -->
      <div
        v-if="iconLeft"
        class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 transition-colors duration-200"
        :class="error ? 'text-red-400' : 'text-gray-400 peer-focus:text-indigo-600'"
      >
        <component :is="iconLeft" class="h-5 w-5" />
      </div>

      <!-- Floating Label -->
      <label
        :for="id"
        class="absolute text-gray-500 duration-200 transform -translate-y-4 scale-75 top-4 z-10 origin-[0] left-4 peer-focus:text-indigo-600 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-4 pointer-events-none truncate max-w-[calc(100%-2rem)]"
        :class="[
            iconLeft ? 'left-11' : '',
            error ? 'text-red-500 peer-focus:text-red-600' : ''
        ]"
      >
        {{ label }} <span v-if="required" class="text-red-500">*</span>
      </label>

      <!-- Suffix icon -->
      <div
        v-if="iconRight"
        class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4 transition-colors duration-200"
        :class="error ? 'text-red-400' : 'text-gray-400 peer-focus:text-indigo-600'"
      >
        <component :is="iconRight" class="h-5 w-5" />
      </div>

       <!-- Bottom Highlight (Animated) -->
       <div 
        v-if="!disabled && !error"
        class="absolute bottom-0 left-0 h-[2px] w-0 bg-indigo-600 transition-all duration-300 peer-focus:w-full"
       ></div>
    </div>
    
    <!-- Error message -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <p v-if="error" class="mt-1 ml-1 text-xs font-medium text-red-600 flex items-center gap-1">
        {{ error }}
      </p>
    </Transition>
    
    <!-- Helper Text -->
     <p v-if="help && !error" class="mt-1 ml-1 text-xs text-gray-500">{{ help }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  labelFloating: Boolean, 
  type: {
    type: String,
    default: 'text',
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
  placeholder: String,
  help: String,
  error: String,
  success: Boolean,
  required: Boolean,
  disabled: Boolean,
  maxLength: Number,
  className: String,
  id: {
    type: String,
    default: () => `input-${Math.random().toString(36).substring(2, 9)}`,
  },
  iconLeft: [Object, Function, String],
  iconRight: [Object, Function, String],
})

defineEmits(['update:modelValue'])

const isFocused = ref(false)
const inputRef = ref(null)

const handleFocus = () => {
  isFocused.value = true
}

const handleBlur = () => {
  isFocused.value = false
}
</script>
