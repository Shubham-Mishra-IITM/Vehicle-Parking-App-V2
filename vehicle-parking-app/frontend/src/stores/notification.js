import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  let nextId = 1

  const addNotification = (message, type = 'info', title = '', duration = 5000) => {
    const notification = {
      id: nextId++,
      message,
      type, // success, danger, warning, info
      title,
      timestamp: Date.now()
    }

    notifications.value.push(notification)

    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, duration)
    }

    return notification.id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // Convenience methods
  const success = (message, title = 'Success') => {
    return addNotification(message, 'success', title)
  }

  const error = (message, title = 'Error') => {
    return addNotification(message, 'danger', title, 8000) // Show errors longer
  }

  const warning = (message, title = 'Warning') => {
    return addNotification(message, 'warning', title)
  }

  const info = (message, title = '') => {
    return addNotification(message, 'info', title)
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }
})
