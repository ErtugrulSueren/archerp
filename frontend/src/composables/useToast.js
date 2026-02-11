import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
    const add = (options) => {
        const id = Math.random().toString(36).substring(2, 9)
        const toast = {
            id,
            title: options.title,
            message: options.message,
            variant: options.variant || 'info', // success, error, warning, info
            duration: options.duration || 3000,
        }

        toasts.value.push(toast)

        if (toast.duration) {
            setTimeout(() => {
                remove(id)
            }, toast.duration)
        }
    }

    const remove = (id) => {
        const index = toasts.value.findIndex((t) => t.id === id)
        if (index !== -1) {
            toasts.value.splice(index, 1)
        }
    }

    const success = (message, title = 'Success') => add({ title, message, variant: 'success' })
    const error = (message, title = 'Error') => add({ title, message, variant: 'error' })
    const warning = (message, title = 'Warning') => add({ title, message, variant: 'warning' })
    const info = (message, title = 'Info') => add({ title, message, variant: 'info' })

    return {
        toasts,
        add,
        remove,
        success,
        error,
        warning,
        info
    }
}
