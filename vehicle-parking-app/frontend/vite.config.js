import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8081, // Match the port in docker-compose.yml
    proxy: {
      '/api': {
        target: 'http://localhost:5004', // Your Flask backend URL
        changeOrigin: true,
      },
    },
  }
})
