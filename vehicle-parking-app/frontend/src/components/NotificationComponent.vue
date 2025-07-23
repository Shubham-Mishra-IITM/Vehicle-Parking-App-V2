<template>
  <div class="notification-container">
    <div 
      v-for="notification in notifications" 
      :key="notification.id"
      :class="['alert', `alert-${notification.type}`, 'alert-dismissible', 'fade', 'show', 'notification']"
      role="alert"
    >
      <strong v-if="notification.title">{{ notification.title }}</strong>
      {{ notification.message }}
      <button 
        type="button" 
        class="btn-close" 
        @click="removeNotification(notification.id)"
      ></button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useNotificationStore } from '@/stores/notification'

export default defineComponent({
  name: 'NotificationComponent',
  setup() {
    const notificationStore = useNotificationStore()

    const removeNotification = (id) => {
      notificationStore.removeNotification(id)
    }

    return {
      notifications: notificationStore.notifications,
      removeNotification
    }
  }
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1050;
  max-width: 350px;
}

.notification {
  margin-bottom: 10px;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
