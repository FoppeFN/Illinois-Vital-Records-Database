import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // This is the crucial line:
  // It tells Vite that all assets should be loaded relative to '/iivrd/'
  base: '/iivrd/',
})