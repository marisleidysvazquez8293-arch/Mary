/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_PROXY_TARGET?: string
  readonly VITE_API_USER?: string
  readonly VITE_API_PASSWORD?: string
  readonly VITE_DEMO_CONJUNTO_PESOS_ID?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
