import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  preview: {
    port: 10065,
    host: '0.0.0.0',
    open: false, // 禁用自动打开浏览器
  },
  server: {
    port: 10065,
    host: '0.0.0.0',
    open: false, // 禁用自动打开浏览器，让终端链接在系统默认浏览器中打开
    strictPort: false,
  },
})
