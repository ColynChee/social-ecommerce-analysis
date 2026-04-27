import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/社交电商用户行为分析/',
  server: {
    port: 5173
  }
})
