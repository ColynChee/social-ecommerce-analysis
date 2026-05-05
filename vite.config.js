import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
export default defineConfig(({ mode }) => ({
  plugins: [vue()],
  base: mode === 'production' ? '/social-ecommerce-analysis/' : '/',
  server: {
    port: 5173
  }
}))