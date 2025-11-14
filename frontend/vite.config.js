import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  preview: {
    port: 10061,
    host: '0.0.0.0',
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
  },
})
