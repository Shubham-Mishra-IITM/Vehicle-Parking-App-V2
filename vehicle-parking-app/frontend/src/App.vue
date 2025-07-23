<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
import NotificationComponent from './components/NotificationComponent.vue'
</script>

<template>
  <Navbar />
  <main class="container mt-4">
    <RouterView />
  </main>
  <NotificationComponent />
</template>

<style>
/* Add any global styles here */
</style>
