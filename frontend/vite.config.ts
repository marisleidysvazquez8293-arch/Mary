import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// Proxy por defecto hacia el backend Django (PASO 4) en :8000.
// Alternativa: definir VITE_API_URL y llamar la API de forma absoluta.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
